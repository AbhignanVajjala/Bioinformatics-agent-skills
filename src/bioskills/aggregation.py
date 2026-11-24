"""Checked specimen/population aggregation; modeling remains separate."""

import numpy as np
import pandas as pd

from bioskills.inputs import require_text
from bioskills.science import (
    ScientificValidationError,
    exact_count_values,
    require,
    validate_metadata,
)
from bioskills.validators import check_replication

MAXIMUM = 2**63 - 1


def pseudobulk(counts, cells, *, organism, reference, count_generation, paired=False):
    require(type(paired) is bool, "paired", "paired must be Boolean.")
    for value, field in [
        (organism, "organism"),
        (reference, "reference"),
        (count_generation, "count_generation"),
    ]:
        require_text(value, field)
    values = exact_count_values(counts, maximum=MAXIMUM)
    for axis in [counts.index, counts.columns]:
        require(
            all(isinstance(x, str) for x in axis),
            "identifiers",
            "Pseudobulk feature/cell IDs must be exact strings.",
        )
    fields = ["subject_id", "specimen_id", "condition", "timepoint", "cell_type", "batch"]
    validate_metadata(cells, fields)
    for field in set(fields) - {"timepoint"}:
        require(
            all(isinstance(x, str) for x in cells[field]),
            "identifiers",
            "Categorical identities must be exact strings.",
        )
    require(
        list(cells.index) == list(counts.columns),
        "sample_alignment",
        "Exact cell ID order required.",
    )
    source_libraries = [sum(values[:, i]) for i in range(values.shape[1])]
    require(
        all(0 < n <= MAXIMUM for n in source_libraries),
        "count_range",
        "Source library total outside positive int64 scope.",
    )
    require(cells.condition.nunique() == 2, "contrast", "Two conditions required by this baseline.")
    context = cells.groupby("specimen_id")[
        ["subject_id", "condition", "timepoint", "batch"]
    ].nunique()
    require((context == 1).all().all(), "identity_mismatch", "Specimen context conflicts.")
    columns, samples, totals, library_audit = {}, [], [], []
    for index, ((specimen, population), group) in enumerate(
        cells.groupby(["specimen_id", "cell_type"], sort=True)
    ):
        name = f"pseudobulk_{index}"
        positions = counts.columns.get_indexer(group.index)
        aggregate = [sum(row[positions]) for row in values]
        require(
            all(0 <= n <= MAXIMUM for n in aggregate),
            "aggregate_range",
            "Gene aggregate exceeds supported int64 output; no wrapped result exported.",
        )
        library = sum(aggregate)
        require(
            0 < library <= MAXIMUM,
            "aggregate_range",
            "Aggregate library exceeds positive int64 scope.",
        )
        require(
            library == sum(source_libraries[i] for i in positions),
            "conservation",
            "Library conservation failed.",
        )
        columns[name] = aggregate
        row = group.iloc[0]
        samples.append({"sample_id": name, **{field: row[field] for field in fields}})
        totals.append({"sample_id": name, "cells": len(group)})
        library_audit.append({"sample_id": name, "total_decimal": str(library)})
    bulk = pd.DataFrame(columns, index=counts.index, dtype="int64")
    source_gene_totals = [sum(row) for row in values]
    output_gene_totals = [sum(int(x) for x in row) for row in bulk.to_numpy()]
    require(
        source_gene_totals == output_gene_totals,
        "conservation",
        "Gene-level count conservation failed.",
    )
    metadata = pd.DataFrame(samples).set_index("sample_id")
    missing = []
    if paired:
        for population in sorted(cells.cell_type.unique()):
            present = metadata[metadata.cell_type == population]
            for donor in sorted(cells.subject_id.unique()):
                for condition in sorted(cells.condition.unique()):
                    if not ((present.subject_id == donor) & (present.condition == condition)).any():
                        missing.append(
                            {"cell_type": population, "subject_id": donor, "condition": condition}
                        )
    population_status, design_audit = {}, {}
    for population, frame in metadata.groupby("cell_type", sort=True):
        reasons = []
        try:
            check_replication(frame, paired=paired)
        except ScientificValidationError as error:
            reasons.append(str(error))
        variables = ["condition"] + (["subject_id"] if paired else [])
        if frame.batch.nunique() > 1:
            variables.append("batch")
        design = pd.get_dummies(frame[variables].astype("category"), drop_first=True, dtype=float)
        design.insert(0, "intercept", 1.0)
        rank = int(np.linalg.matrix_rank(design.to_numpy()))
        if rank < design.shape[1]:
            reasons.append("confounding: declared condition/subject/batch design is rank deficient")
        if len(frame) <= rank:
            reasons.append("residual_df: no residual degrees of freedom")
        if paired and any(row["cell_type"] == population for row in missing):
            reasons.append(
                "pairing: expected donor-condition observations missing for this population"
            )
        status = "BLOCKED_POPULATION_INFERENCE" if reasons else "READY_FOR_DESIGN_REVIEW"
        population_status[population] = status
        design_audit[population] = {
            "status": status,
            "reasons": reasons,
            "independent_donors_by_condition": frame.groupby("condition")
            .subject_id.nunique()
            .to_dict(),
            "subjects": int(frame.subject_id.nunique()),
            "specimens": int(frame.specimen_id.nunique()),
            "declared_covariates": variables,
            "rank": rank,
            "residual_df": len(frame) - rank,
            "r_count_range_compatible": bool(
                (bulk[frame.index].to_numpy() <= 2**31 - 1).all()
                and all(
                    int(row["total_decimal"]) <= 2**53 - 1
                    for row in library_audit
                    if row["sample_id"] in frame.index
                )
            ),
        }
    return (
        bulk,
        metadata,
        {
            "analysis_status": "EXECUTED",
            "aggregation_status": "EXECUTED",
            "method": "checked exact raw-count sum by specimen and cell population",
            "count_scope": "exact source integers and int64 aggregates/libraries; float sources limited to 2^53-1",
            "cells": len(cells),
            "subjects": int(cells.subject_id.nunique()),
            "specimens": int(cells.specimen_id.nunique()),
            "populations": int(cells.cell_type.nunique()),
            "cells_per_sample": totals,
            "library_totals_decimal": library_audit,
            "gene_totals_decimal": [
                {"gene_id": gene, "total_decimal": str(n)}
                for gene, n in zip(counts.index, source_gene_totals, strict=True)
            ],
            "conservation": {
                "status": "PASS",
                "source_total_decimal": str(sum(source_gene_totals)),
                "output_total_decimal": str(sum(output_gene_totals)),
            },
            "missing_donor_condition": missing,
            "missingness_interpretation": "Paired expectations only; absent unpaired donor-condition combinations are structural, not missing observations",
            "population_status": population_status,
            "population_design": design_audit,
            "differential_state": "NOT_RUN",
            "limitations": [
                "Aggregation is not differential-state testing or biological validation",
                "Declared donors/identities and upstream QC are not independently authenticated",
                "Design readiness does not establish power; downstream R count limits are a separate gate",
                "Longitudinal/repeated observations beyond one pair per donor require a separate model",
            ],
        },
    )
