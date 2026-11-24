"""Scientific checks with explicit scope and a predictable JSON command interface."""

from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd
from bioskills.inputs import parse_table_text, require_text, strict_json

from bioskills.domain_workflows import check_fba_status
from bioskills.science import (
    ScientificValidationError,
    check_counts,
    require,
    sha256,
    validate_matrix,
    validate_metadata,
)


NAMES = (
    "check_counts",
    "check_sample_ids",
    "check_design_rank",
    "check_replication",
    "check_fba_status",
    "check_leakage",
    "check_enrichment_background",
)


def check_sample_ids(counts, metadata, *, allow_reorder=False):
    require(
        counts.columns.is_unique and metadata.index.is_unique,
        "duplicate_ids",
        "Duplicate sample identifiers.",
    )
    require(
        not metadata.index.isna().any() and all(str(x).strip() for x in metadata.index),
        "missing_ids",
        "Missing sample identifiers.",
    )
    require(set(counts.columns) == set(metadata.index), "sample_alignment", "Sample sets differ.")
    order = metadata.index.get_indexer(counts.columns).tolist()
    reordered = order != list(range(len(order)))
    require(
        not reordered or allow_reorder, "sample_order", "Explicit ID-based reordering required."
    )
    return {
        "status": "WARN" if reordered else "PASS",
        "metadata_row_order": order,
        "reordered_in_memory": reordered,
        "samples": len(order),
    }


def check_design_rank(design):
    values = validate_matrix(design)
    rank = int(np.linalg.matrix_rank(values))
    require(
        rank == values.shape[1],
        "confounding",
        "Design is rank deficient; effects are not identifiable.",
    )
    df = values.shape[0] - rank
    require(df > 0, "residual_df", "No residual degrees of freedom.")
    return {
        "status": "PASS",
        "rank": rank,
        "residual_df": df,
        "limitations": ["Full rank cannot rule out unmeasured confounding or inadequate power"],
    }


def check_replication(metadata, *, paired=False):
    columns = ["subject_id", "condition"]
    require(isinstance(paired, bool), "paired", "paired must be Boolean.")
    validate_metadata(metadata, columns)
    require(
        set(columns) <= set(metadata), "metadata_fields", "Subject and condition fields required."
    )
    require(
        not metadata[columns].isna().any().any()
        and metadata[columns].astype(str).map(lambda x: bool(x.strip())).all().all(),
        "metadata_missing",
        "Unit and condition declarations must be complete.",
    )
    require(metadata.condition.nunique() == 2, "contrast", "Exactly two conditions required.")
    units = metadata.groupby("condition").subject_id.nunique()
    require(
        (units >= 2).all(),
        "replication",
        "Independent units absent; minimum is not a power guarantee.",
    )
    if paired:
        table = pd.crosstab(metadata.subject_id, metadata.condition)
        require(
            (table == 1).all().all(), "pairing", "One specimen per subject and condition required."
        )
    else:
        require(
            metadata.subject_id.is_unique,
            "experimental_unit",
            "Repeated subjects require a paired design.",
        )
    return {
        "status": "PASS",
        "independent_units_per_condition": sorted(map(int, units)),
        "paired": paired,
        "limitations": [
            "Declared subjects are not independently authenticated",
            "Cells and technical libraries are not biological replicates",
        ],
    }


def check_leakage(metadata):
    require(
        {"subject_id", "split"} <= set(metadata), "metadata_fields", "Subject and split required."
    )
    require(
        not metadata[["subject_id", "split"]].isna().any().any()
        and metadata.subject_id.astype(str).map(lambda x: bool(x.strip())).all(),
        "metadata_missing",
        "Subject and split declarations must be complete.",
    )
    require(
        set(metadata.split) <= {"train", "test", "validation"}, "split", "Unknown partition label."
    )
    crossing = int((metadata.groupby("subject_id").split.nunique() > 1).sum())
    require(crossing == 0, "patient_leakage", "Subject overlap across partitions detected.")
    return {
        "status": "PASS",
        "subjects": int(metadata.subject_id.nunique()),
        "partitions": sorted(metadata.split.unique()),
        "limitations": [
            "Does not detect unrecorded relatedness, preprocessing leakage, or mislabeled identity"
        ],
    }


def check_enrichment_background(data, *, organism, reference, multiple_testing):
    require_text(organism, "organism")
    require_text(reference, "reference")
    require(
        isinstance(data, dict) and {"selected", "tested", "mappings"} <= data.keys(),
        "structure",
        "Selected, tested and mappings fields required.",
    )
    selected, tested, mappings = data["selected"], data["tested"], data["mappings"]
    require(
        isinstance(selected, list) and isinstance(tested, list) and isinstance(mappings, list),
        "structure",
        "Selected/tested lists and mapping records required.",
    )
    for values in (selected, tested):
        require(
            bool(values) and all(isinstance(v, str) and v.strip() for v in values),
            "identifiers",
            "Nonblank identifiers required.",
        )
        require(
            len(set(values)) == len(values), "duplicate_ids", "Duplicate enrichment identifiers."
        )
    require(
        set(selected) < set(tested),
        "universe",
        "Eligible tested universe must extend beyond selected genes.",
    )
    require(
        multiple_testing == "BH",
        "multiplicity",
        "This workflow requires BH across tested pathways.",
    )
    require(bool(mappings), "mapping", "Mapping records required.")
    for record in mappings:
        require(
            isinstance(record, dict)
            and {"source", "target", "organism", "reference"} <= record.keys(),
            "mapping",
            "Complete mapping record required.",
        )
        for field in ("source", "target", "organism", "reference"):
            require_text(record[field], "mapping")
    mapping = pd.DataFrame(mappings)
    require(
        {"source", "target", "organism", "reference"} <= set(mapping),
        "mapping",
        "Audited source/target/organism/release mapping required.",
    )
    require(
        not mapping.isna().any().any()
        and mapping.astype(str).map(lambda x: bool(x.strip())).all().all(),
        "mapping",
        "Missing mapping identifiers.",
    )
    require(
        mapping.source.is_unique and mapping.target.is_unique,
        "mapping",
        "Ambiguous mappings require an explicit separate policy.",
    )
    require(
        set(mapping.source) == set(tested),
        "mapping",
        "Retain every tested identifier or audit losses before testing.",
    )
    require(
        (mapping.organism == organism).all() and (mapping.reference == reference).all(),
        "mapping",
        "Mapping organism or release mismatch.",
    )
    return {
        "status": "PASS",
        "selected": len(selected),
        "tested": len(tested),
        "mapping_policy": "one-to-one, no losses",
        "multiple_testing": "BH",
        "limitations": [
            "Declared universe eligibility and identifier mappings require upstream verification"
        ],
    }


def read_table(path):
    delimiter = "\t" if path.suffix.lower() in {".tsv", ".txt"} else ","
    return parse_table_text(path.read_text(encoding="utf-8"), delimiter)


def evaluate(name, input_path, config, metadata_path=None):
    """Return a report and exit code without modifying input files."""
    files = {"input": Path(input_path)}
    if metadata_path is not None:
        files["metadata"] = Path(metadata_path)
    report = {
        "schema_version": 1,
        "validator": name,
        "status": "NOT_RUN",
        "checks": [],
        "reason": "",
        "inputs": {key: path.name for key, path in files.items()},
        "input_hashes": {},
        "software_versions": {"python": platform.python_version()},
        "limitations": [
            "Metadata consistency does not authenticate biological identity",
            "Successful computation does not establish biological or clinical validity",
        ],
        "recommended_action": "Review methods and limitations before downstream interpretation.",
    }
    for package in ("numpy", "pandas", "cobra"):
        try:
            report["software_versions"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    try:
        if name not in NAMES or not isinstance(config, dict):
            raise ValueError("Unknown validator or malformed configuration")
        report["input_hashes"] = {key: sha256(path) for key, path in files.items()}
        if name == "check_fba_status":
            from cobra.io import load_json_model, read_sbml_model

            model = (
                load_json_model(str(files["input"]))
                if files["input"].suffix == ".json"
                else read_sbml_model(str(files["input"]))
            )
            model.solver = "glpk"
            # The legacy gate validates the objective and finite ordered bounds.
            from bioskills.science import solve_model

            result = check_fba_status(model, solve_model(model))
        elif name == "check_enrichment_background":
            result = check_enrichment_background(strict_json(files["input"].read_bytes()), **config)
        else:
            table = read_table(files["input"])
            if name == "check_counts":
                result = check_counts(table, **config)
            elif name == "check_sample_ids":
                result = check_sample_ids(table, read_table(files["metadata"]), **config)
            elif name == "check_design_rank":
                result = check_design_rank(table)
            elif name == "check_replication":
                result = check_replication(table, **config)
            else:
                result = check_leakage(table)
        report.update(
            status=result["status"], reason="Declared inputs passed the implemented checks."
        )
        report["checks"] = [{"check": name, **result}]
        code = 0
    except ScientificValidationError as error:
        report.update(
            status="FAIL",
            reason=str(error),
            recommended_action="Resolve the named scientific gate before downstream analysis.",
        )
        code = 2
    except ImportError:
        report.update(
            status="BLOCKED",
            reason="Optional scientific runtime is unavailable.",
            recommended_action="Install the documented optional environment.",
        )
        code = 3
    except (OSError, ValueError, TypeError, KeyError, StopIteration, csv.Error):
        report.update(
            status="FAIL",
            reason="Input, format or configuration could not be parsed.",
            recommended_action="Check the input contract and configuration.",
        )
        code = 1
    if not report["checks"]:
        report["checks"] = [{"check": name, "status": report["status"], "reason": report["reason"]}]
    return report, code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("validator", choices=NAMES)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    protected = [args.input, args.metadata, args.config]
    if args.output.exists() or any(
        p is not None and args.output.resolve() == p.resolve() for p in protected
    ):
        parser.error("Output must be a new path distinct from every input.")
    try:
        config = strict_json(args.config.read_bytes()) if args.config else {}
    except (OSError, ValueError):
        config = None
    report, code = evaluate(args.validator, args.input, config, args.metadata)
    if args.config is not None and args.config.is_file():
        report["input_hashes"]["config"] = sha256(args.config)
        report["inputs"]["config"] = args.config.name
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"validator": args.validator, "status": report["status"]}))
    return code
