"""Narrow executable capabilities for pseudobulk, ORA and format inspection."""

from __future__ import annotations

import gzip
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

from bioskills.science import check_counts, require
from bioskills.validators import check_enrichment_background, check_replication


def pseudobulk(counts, cells, *, organism, reference, count_generation, paired=False):
    """Sum raw counts by specimen and cell population, retaining donor metadata."""
    check_counts(
        counts,
        scale="raw_counts",
        organism=organism,
        reference=reference,
        count_generation=count_generation,
    )
    fields = ["subject_id", "specimen_id", "condition", "timepoint", "cell_type"]
    require(
        cells.index.is_unique and list(cells.index) == list(counts.columns),
        "sample_alignment",
        "Cell IDs and order must match counts.",
    )
    require(
        set(fields) <= set(cells)
        and not cells[fields].isna().any().any()
        and cells[fields].astype(str).map(lambda x: bool(x.strip())).all().all(),
        "cell_metadata",
        "Complete cell/sample/subject/population metadata required.",
    )
    require(cells.condition.nunique() == 2, "contrast", "Specify two conditions for this baseline.")
    specimen_context = cells.groupby("specimen_id")[
        ["subject_id", "condition", "timepoint"]
    ].nunique()
    require((specimen_context == 1).all().all(), "identity_mismatch", "Specimen context conflicts.")
    columns, samples, totals = {}, [], []
    for index, ((specimen, population), group) in enumerate(
        cells.groupby(["specimen_id", "cell_type"], sort=True)
    ):
        name = f"pseudobulk_{index}"
        columns[name] = counts[group.index].sum(axis=1)
        context = group.iloc[0]
        samples.append(
            {
                "sample_id": name,
                "specimen_id": specimen,
                "cell_type": population,
                "subject_id": context.subject_id,
                "condition": context.condition,
                "timepoint": context.timepoint,
            }
        )
        totals.append({"sample_id": name, "cells": len(group)})
    metadata = pd.DataFrame(samples).set_index("sample_id")
    missing = []
    for population in sorted(cells.cell_type.unique()):
        present = metadata[metadata.cell_type == population]
        for donor in sorted(cells.subject_id.unique()):
            for condition in sorted(cells.condition.unique()):
                if not ((present.subject_id == donor) & (present.condition == condition)).any():
                    missing.append(
                        {"cell_type": population, "subject_id": donor, "condition": condition}
                    )
    population_status = {}
    from bioskills.science import ScientificValidationError

    for population, frame in metadata.groupby("cell_type"):
        try:
            check_replication(frame, paired=paired)
            population_status[population] = "READY_FOR_DESIGN_REVIEW"
        except ScientificValidationError:
            population_status[population] = "BLOCKED_POPULATION_INFERENCE"
    return (
        pd.DataFrame(columns),
        metadata,
        {
            "analysis_status": "EXECUTED",
            "method": "raw-count sum by specimen and cell population",
            "cells_per_sample": totals,
            "missing_donor_condition": missing,
            "population_status": population_status,
            "differential_state": "NOT_RUN",
            "limitations": [
                "Cell QC, doublets and ambient RNA must be assessed upstream",
                "Aggregation does not establish adequate replication, power or DE",
                "Multiplicity across genes and cell populations requires a declared policy",
            ],
        },
    )


def ora(data, gene_sets, *, organism, reference, database, release):
    """Use SciPy Fisher exact tests and BH across the entire supplied set family."""
    from scipy.stats import false_discovery_control, fisher_exact

    check_enrichment_background(data, organism=organism, reference=reference, multiple_testing="BH")
    require(
        bool(database) and bool(release), "gene_sets", "Gene-set database and release required."
    )
    require(
        isinstance(gene_sets, dict) and bool(gene_sets), "gene_sets", "Gene-set family required."
    )
    mapping = {row["source"]: row["target"] for row in data["mappings"]}
    tested = {mapping[g] for g in data["tested"]}
    selected = {mapping[g] for g in data["selected"]}
    rows = []
    for name, members in sorted(gene_sets.items()):
        require(
            isinstance(members, list) and all(isinstance(g, str) and g.strip() for g in members),
            "gene_sets",
            "Nonblank gene identifiers required.",
        )
        membership = set(members)
        eligible = membership & tested
        overlap = len(selected & eligible)
        table = [
            [overlap, len(selected) - overlap],
            [len(eligible) - overlap, len(tested - selected - eligible)],
        ]
        result = fisher_exact(table, alternative="greater")
        rows.append(
            {
                "gene_set": name,
                "overlap": overlap,
                "eligible_members": len(eligible),
                "duplicate_memberships": len(members) - len(membership),
                "members_outside_universe": len(membership - tested),
                "pvalue": float(result.pvalue),
            }
        )
    adjusted = false_discovery_control([row["pvalue"] for row in rows], method="bh")
    for row, value in zip(rows, adjusted, strict=True):
        row["padj"] = float(value)
    return {
        "analysis_status": "EXECUTED",
        "method": "one-sided Fisher ORA with BH",
        "database": database,
        "release": release,
        "organism": organism,
        "reference": reference,
        "testing_family": len(rows),
        "results": rows,
        "mapping_policy": "one-to-one without dropped tested genes",
        "limitations": [
            "Gene-set association does not establish pathway activation or causation",
            "Universe eligibility and annotation authenticity need upstream verification",
            "Ranked enrichment is NOT_RUN",
        ],
    }


def inspect_format(path: Path, *, reference=None, expected_reference=None):
    """Inspect small text records or signatures with explicit optional-parser limits."""
    require(path.is_file(), "input", "Input file required.")
    with path.open("rb") as file:
        magic = file.read(8)
    compressed = magic.startswith(b"\x1f\x8b")
    opener = gzip.open if compressed else open
    with opener(path, "rb") as file:
        raw = file.read(4 * 1024 * 1024 + 1)
    require(len(raw) <= 4 * 1024 * 1024, "size", "Use a streaming parser for files over 4 MiB.")
    format_ = "UNKNOWN"
    validation = "NOT_RUN"
    if raw.startswith(b"BAM\x01"):
        format_, validation = "BAM", "OPTIONAL_PYSAM_REQUIRED"
    elif raw.startswith(b"CRAM"):
        format_, validation = "CRAM", "OPTIONAL_PYSAM_AND_REFERENCE_REQUIRED"
    elif raw.startswith(b"BCF"):
        format_, validation = "BCF", "OPTIONAL_PYSAM_REQUIRED"
    elif raw.startswith(b"\x89HDF\r\n\x1a\n"):
        format_, validation = "HDF5_CONTAINER", "OPTIONAL_H5AD_PARSER_REQUIRED"
    else:
        text = raw.decode("utf-8")
        lines = text.splitlines()
        require(bool(lines), "empty_file", "Empty file.")
        if text.startswith("##fileformat=VCF"):
            require(
                any(line.startswith("#CHROM\tPOS\t") for line in lines),
                "vcf_header",
                "VCF column header absent.",
            )
            records = [line.split("\t") for line in lines if not line.startswith("#")]
            require(
                all(len(row) >= 8 and row[1].isdigit() and int(row[1]) >= 1 for row in records),
                "vcf_record",
                "Invalid VCF position or record.",
            )
            format_, validation = "VCF", "BASIC_TEXT_RECORDS"
        elif text.startswith(">"):
            for record in text.split(">")[1:]:
                parts = record.splitlines()
                require(len(parts) >= 2 and bool(parts[0].strip())
                        and bool("".join(parts[1:]))
                        and all(line.replace("-", "").isalpha() for line in parts[1:]),
                        "fasta", "Missing header, sequence or invalid FASTA sequence text.")
            format_, validation = "FASTA", "BASIC_TEXT_RECORDS"
        elif text.startswith("@"):
            require(len(lines) % 4 == 0, "fastq", "Incomplete four-line FASTQ.")
            for index in range(0, len(lines), 4):
                header, seq, plus, quality = lines[index : index + 4]
                require(
                    header.startswith("@")
                    and plus.startswith("+")
                    and bool(seq)
                    and len(seq) == len(quality),
                    "fastq",
                    "Invalid FASTQ record.",
                )
                require(all(33 <= ord(char) <= 126 for char in quality),
                        "fastq_quality", "FASTQ quality characters must be printable ASCII.")
            format_, validation = "FASTQ", "FOUR_LINE_FASTQ"
        elif "<sbml" in text or "sbml:" in text:
            document = ET.fromstring(text)
            require(document.tag.split("}")[-1] == "sbml", "sbml", "SBML root required.")
            format_, validation = "SBML", "XML_STRUCTURE_ONLY"
        else:
            records = [line.split("\t") for line in lines if line and not line.startswith("#")]
            if records and all(len(row) == 9 and not row[1].isdigit() for row in records):
                require(
                    all(
                        row[3].isdigit() and row[4].isdigit() and 1 <= int(row[3]) <= int(row[4])
                        for row in records
                    ),
                    "coordinates",
                    "Invalid one-based feature interval.",
                )
                format_, validation = "GTF_OR_GFF", "BASIC_TEXT_RECORDS"
            elif records and all(
                len(row) >= 3 and row[1].isdigit() and row[2].isdigit() for row in records
            ):
                require(
                    all(0 <= int(row[1]) < int(row[2]) for row in records),
                    "coordinates",
                    "Invalid zero-based half-open BED interval.",
                )
                format_, validation = "BED", "BASIC_TEXT_RECORDS"
            else:
                delimiter = "\t" if "\t" in lines[0] else ","
                table = pd.read_csv(path, sep=delimiter, index_col=0, compression="infer")
                from bioskills.science import validate_matrix

                validate_matrix(table)
                format_, validation = "NUMERIC_TABLE", "NUMERIC_STRUCTURE_ONLY"
    if expected_reference is not None:
        require(reference == expected_reference, "reference", "Declared reference build mismatch.")
    return {
        "format": format_,
        "validation": validation,
        "compression": "gzip" if compressed else "none",
        "encoding": "binary" if validation.startswith("OPTIONAL") else "utf-8",
        "reference": reference,
        "limitations": [
            "Content/signature inspection is not complete format or scientific validation",
            "Biological sample identity is not inferred from filenames",
            "Reference identity is declared, not independently authenticated",
        ],
    }
