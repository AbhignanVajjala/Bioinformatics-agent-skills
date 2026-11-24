"""Conservative, deliberately scoped scientific readiness gates.

These gates verify declared data and simple independent-sample designs; they
cannot establish truthful assay provenance or biological validity.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from collections.abc import Mapping
from numbers import Real, Integral
from decimal import Decimal, InvalidOperation
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

import numpy as np
import pandas as pd


class ScientificValidationError(ValueError):
    """A named scientific gate failed; analysis must not continue."""

    def __init__(self, message, *, evidence=None):
        super().__init__(message)
        self.evidence = evidence or {"analysis_status": "NOT_RUN", "numerical_events": []}


def require(condition, check, message):
    if not condition:
        raise ScientificValidationError(f"{check}: {message}")


def validate_labels(labels, check="identifiers"):
    """Accept homogeneous strings or finite real labels without coercion/trimming."""
    labels = list(labels)
    strings = all(isinstance(x, str) and bool(x.strip()) for x in labels)
    numbers = all(
        isinstance(x, Real) and not isinstance(x, (bool, np.bool_)) and np.isfinite(x)
        for x in labels
    )
    require(
        bool(labels) and (strings or numbers),
        check,
        "Use nonblank strings or finite numeric labels; mixed types are ambiguous.",
    )


def validate_mapping(mapping, matrix, *, timepoint=False):
    require(isinstance(mapping, pd.DataFrame), "mapping_type", "Mapping must be a DataFrame.")
    require(mapping.columns.is_unique, "mapping_columns", "Duplicate metadata columns.")
    fields = ["specimen_id", "subject_id", "split"] + (["timepoint"] if timepoint else [])
    require(set(fields) <= set(mapping), "mapping_fields", f"Required columns: {fields}.")
    validate_labels(mapping.index, "sample_ids")
    require(
        mapping.index.is_unique and list(mapping.index) == list(matrix.columns),
        "sample_alignment",
        "Exact matrix/metadata sample alignment required.",
    )
    for field in fields:
        validate_labels(mapping[field], field)
    require(mapping.specimen_id.is_unique, "duplicate_specimen", "Duplicate specimen.")


def validate_axes(matrix):
    require(isinstance(matrix, pd.DataFrame), "matrix_type", "Matrix must be a DataFrame.")
    require(not matrix.empty, "empty_matrix", "Supply features by samples.")
    require(
        matrix.index.is_unique and matrix.columns.is_unique, "duplicate_ids", "IDs must be unique."
    )
    validate_labels(matrix.index)
    validate_labels(matrix.columns)


def validate_matrix(matrix):
    validate_axes(matrix)
    require(
        not np.iscomplexobj(matrix.to_numpy()),
        "numeric_matrix",
        "Real-valued observations required.",
    )
    try:
        values = matrix.to_numpy(dtype=float)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ScientificValidationError("numeric_matrix: Non-numeric values") from exc
    require(
        np.isfinite(values).all(),
        "nonfinite",
        "Resolve missing/nonfinite values before this demonstration.",
    )
    return values


def exact_count_values(counts, *, maximum=2**63 - 1):
    """Python-integer count arithmetic; wide aggregation never passes through float.

    Integer/text/Decimal sources support the declared bound. Float inputs must
    already be exact integers <=2^53-1; upstream rounding cannot be authenticated.
    """
    validate_axes(counts)
    reject_boolean_counts(counts)
    values = np.empty(counts.shape, dtype=object)
    for index, value in np.ndenumerate(counts.to_numpy()):
        if isinstance(value, Integral):
            number = int(value)
        elif isinstance(value, (str, Decimal)):
            try:
                decimal = Decimal(value)
            except InvalidOperation as error:
                raise ScientificValidationError("count_values: Invalid count token.") from error
            require(
                decimal.is_finite()
                and 0 <= decimal <= maximum
                and decimal == decimal.to_integral_value(),
                "count_values",
                "Exact nonnegative integer counts within the declared scope required.",
            )
            number = int(decimal)
        elif isinstance(value, Real):
            require(
                np.isfinite(value)
                and 0 <= value <= min(maximum, 2**53 - 1)
                and value == np.floor(value),
                "count_values",
                "Float counts must be integral and within exact binary64 scope.",
            )
            number = int(value)
        else:
            raise ScientificValidationError("count_values: Unsupported count type.")
        require(0 <= number <= maximum, "count_range", "Count exceeds supported integer range.")
        values[index] = number
    return values


def check_counts(
    counts, *, scale, organism, reference, count_generation=None, require_provenance=True
):
    """Count integrity shared by the legacy readiness gate and validator CLI."""
    values = validate_matrix(counts)
    validate_count_representation(counts)
    require(
        scale == "raw_counts",
        "count_scale",
        "TPM/FPKM/transformed values are not raw counts; verify provenance.",
    )
    require(
        isinstance(organism, str)
        and bool(organism.strip())
        and isinstance(reference, str)
        and bool(reference.strip()),
        "context",
        "Organism and annotation/reference are required.",
    )
    exact_count_totals(values)
    if require_provenance:
        require(
            isinstance(count_generation, str) and bool(count_generation.strip()),
            "provenance",
            "Declare the upstream count-generation method.",
        )
    return {
        "status": "PASS",
        "samples": len(counts.columns),
        "genes": len(counts),
        "limitations": ["Integer appearance cannot verify declared raw-count provenance"],
    }


def exact_count_totals(values):
    """Count denominator gate shared with cross-view normalization; no float summation."""
    require(
        (values >= 0).all() and (values == np.floor(values)).all(),
        "count_values",
        "Counts must be nonnegative integers.",
    )
    require(
        (values <= 2**53 - 1).all(), "count_range", "Counts exceed exact binary64 integer scope."
    )
    totals = [sum(int(v) for v in values[:, i]) for i in range(values.shape[1])]
    require(all(t > 0 for t in totals), "empty_library", "A zero-depth library cannot be modeled.")
    require(
        all(t <= 2**53 - 1 for t in totals),
        "count_range",
        "Library sum exceeds exact binary64 integer scope; unsupported normalization.",
    )
    return totals


def reject_boolean_counts(counts):
    values = counts.to_numpy()
    require(
        not (
            values.dtype.kind == "b"
            or (
                values.dtype.kind == "O"
                and any(isinstance(x, (bool, np.bool_)) for x in values.flat)
            )
        ),
        "count_values",
        "Boolean observations are not raw integer counts.",
    )


def validate_count_representation(counts):
    """Check exact text/Decimal count integrality before binary64 can hide fractions."""
    reject_boolean_counts(counts)
    values = counts.to_numpy()
    if values.dtype.kind in {"O", "U", "S"}:
        for value in values.flat:
            if not isinstance(value, (str, Decimal)):
                continue
            try:
                number = Decimal(value)
            except InvalidOperation as error:
                raise ScientificValidationError(
                    "count_values: Invalid numeric count token."
                ) from error
            require(
                number.is_finite()
                and number >= 0
                and number <= 2**53 - 1
                and number == number.to_integral_value(),
                "count_values",
                "Count text must represent an exact nonnegative integer within binary64 scope.",
            )


def validate_metadata(metadata, fields):
    require(isinstance(metadata, pd.DataFrame), "metadata_type", "Metadata must be a DataFrame.")
    require(metadata.columns.is_unique, "metadata_columns", "Duplicate metadata columns.")
    require(set(fields) <= set(metadata), "metadata_fields", f"Required fields: {fields}.")
    validate_labels(metadata.index, "metadata_ids")
    require(metadata.index.is_unique, "duplicate_samples", "Duplicate metadata sample IDs.")
    for field in fields:
        validate_labels(metadata[field], "metadata_missing")


def validate_counts(counts, metadata, *, scale, organism, reference):
    """Validate independent subjects with an optional categorical batch design.

    The legacy call contract retains its original provenance fields and rejects
    repeated subjects. New count-only callers require count-generation metadata.
    """
    check_counts(
        counts, scale=scale, organism=organism, reference=reference, require_provenance=False
    )
    require(
        (counts.to_numpy(dtype=float) <= 2**31 - 1).all(),
        "r_integer_range",
        "Supported R recipes require each count <=2147483647; generic count validation has a wider scope.",
    )
    require(isinstance(metadata, pd.DataFrame), "metadata_type", "Metadata must be a DataFrame.")
    validate_metadata(
        metadata, ["condition", "subject_id"] + (["batch"] if "batch" in metadata else [])
    )
    require(metadata.index.is_unique, "duplicate_samples", "Sample metadata must be unique.")
    require(
        list(counts.columns) == list(metadata.index),
        "sample_alignment",
        "Sample names AND order must match; explicitly reconcile first.",
    )
    required = ["condition", "subject_id"]
    require(set(required) <= set(metadata), "metadata_fields", "Need condition and subject_id.")
    columns = required + (["batch"] if "batch" in metadata else [])
    require(
        not metadata[columns].isna().any().any()
        and metadata[columns].astype(str).map(lambda v: bool(v.strip())).all().all(),
        "metadata_missing",
        "Design metadata cannot be missing.",
    )
    require(
        metadata.subject_id.is_unique,
        "experimental_unit",
        "Repeated subjects need a paired/repeated-measures design, unsupported by this gate.",
    )
    require(
        metadata.condition.nunique() == 2, "contrast", "This demo requires exactly two conditions."
    )
    replication = metadata.groupby("condition").subject_id.nunique()
    require(
        (replication >= 2).all(),
        "replication",
        "Need at least two independent subjects per group; this is not a power guarantee.",
    )
    design = pd.get_dummies(
        metadata[["condition"] + (["batch"] if "batch" in metadata else [])].astype("category"),
        drop_first=True,
        dtype=float,
    )
    design.insert(0, "intercept", 1.0)
    rank = int(np.linalg.matrix_rank(design.to_numpy()))
    require(
        rank == design.shape[1],
        "confounding",
        "Design is rank deficient: treatment and batch effects are not separately identifiable.",
    )
    require(design.shape[0] > rank, "residual_df", "No residual degrees of freedom.")
    return {
        "status": "PASS",
        "readiness_scope": "R count-value/design checks only; upstream count_generation still required by check_counts and R configuration",
        "samples": len(metadata),
        "genes": len(counts),
        "design_rank": rank,
        "design_columns": list(design),
        "independent_replicates": replication.to_dict(),
        "limitations": [
            "Declared provenance is not independently verified",
            "No power assessment or differential-expression model has been run",
        ],
    }


def reconcile_omics(matrices, mappings):
    """Match explicitly declared specimen IDs, checking subject identity and leakage.

    Matrices are feature x assay-sample; maps indexed by assay-sample have
    specimen_id, subject_id, split. Missing modalities are reported as exclusions.
    """
    require(
        isinstance(matrices, Mapping) and isinstance(mappings, Mapping),
        "modalities",
        "Matrices/maps must be mappings.",
    )
    require(
        len(matrices) >= 2 and set(matrices) == set(mappings),
        "modalities",
        "Need matching matrices/maps for >=2 assays.",
    )
    identities = {}
    split_by_subject = {}
    specimens = {}
    for name, matrix in matrices.items():
        validate_matrix(matrix)
        validate_mapping(mappings[name], matrix)
    for field in ["specimen_id", "subject_id"]:
        validate_labels([x for mapping in mappings.values() for x in mapping[field]], field)
    for name, matrix in matrices.items():
        mapping = mappings[name]
        require(
            set(mapping.split) <= {"train", "test", "validation"},
            "split_labels",
            "Use train/test/validation labels.",
        )
        for row in mapping.itertuples():
            require(
                row.specimen_id not in identities or identities[row.specimen_id] == row.subject_id,
                "identity_mismatch",
                "One specimen maps to conflicting subjects; resolve source metadata.",
            )
            identities[row.specimen_id] = row.subject_id
            require(
                row.subject_id not in split_by_subject
                or split_by_subject[row.subject_id] == row.split,
                "patient_leakage",
                "All specimens from a subject must share one split; regroup and re-evaluate.",
            )
            split_by_subject[row.subject_id] = row.split
        specimens[name] = set(mapping.specimen_id)
    common = sorted(set.intersection(*specimens.values()))
    require(
        len(common) >= 3,
        "overlap",
        "Fewer than three matched specimens: descriptive correlation is not useful.",
    )
    aligned = {}
    for name, matrix in matrices.items():
        renamed = matrix.copy()
        renamed.columns = mappings[name].specimen_id
        aligned[name] = renamed[common]
    matched = mappings[next(iter(matrices))].set_index("specimen_id").loc[common]
    subject_counts = matched.subject_id.value_counts()
    partition_counts = {
        split: {"specimens": int(len(group)), "subjects": int(group.subject_id.nunique())}
        for split, group in matched.groupby("split", sort=True)
    }
    warnings = ["Descriptive specimen-level association only; no independent-subject inference."]
    if (subject_counts > 1).any():
        warnings.append("Repeated specimens are not independent biological subjects.")
    if len(subject_counts) == 1:
        warnings.append("Single-subject observations cannot establish population generalization.")
    if any(split in partition_counts for split in ["test", "validation"]):
        warnings.append("Inspecting held-out data may compromise future confirmatory evaluation.")
    return aligned, {
        "status": "PASS",
        "matched_specimens": common,
        "excluded_specimens": {k: sorted(v - set(common)) for k, v in specimens.items()},
        "matched_specimen_count": len(common),
        "matched_subject_count": len(subject_counts),
        "specimens_per_subject": [
            {"subject_id": subject, "specimens": int(count)}
            for subject, count in subject_counts.items()
        ],
        "partitions": partition_counts,
        "partition_semantics": "All matched partitions contribute; no train-only fitting or held-out prediction.",
        "warnings": warnings,
        "limitations": [
            "Sample identities are declarations, not genotype authentication",
            "No predictive performance has been evaluated",
        ],
    }


def toy_model():
    """Explicit extracellular uptake, transport and cytoplasmic toy drain."""
    import cobra

    model = cobra.Model("synthetic_one_substrate")
    model.solver = "glpk"
    substrate = cobra.Metabolite("a_c", formula="C", compartment="c", charge=0)
    external = cobra.Metabolite("a_e", formula="C", compartment="e", charge=0)
    exchange = cobra.Reaction("EX_a")
    exchange.bounds = (-10, 0)
    exchange.add_metabolites({external: -1})
    transport = cobra.Reaction("TRANSPORT")
    transport.bounds = (0, 1000)
    transport.add_metabolites({external: -1, substrate: 1})
    biomass = cobra.Reaction("BIOMASS")
    biomass.bounds = (0, 1000)
    biomass.add_metabolites({substrate: -1})
    model.add_reactions([exchange, transport, biomass])
    model.compartments = {"e": "extracellular", "c": "cytoplasm"}
    model.objective = biomass
    return model


def solve_model(model):
    from cobra.util.solver import linear_reaction_coefficients

    require(
        bool(linear_reaction_coefficients(model)),
        "objective",
        "A nonzero reaction objective is required.",
    )
    for reaction in model.reactions:
        require(
            np.isfinite([reaction.lower_bound, reaction.upper_bound]).all()
            and reaction.lower_bound <= reaction.upper_bound,
            "reaction_bounds",
            "Supply ordered finite bounds.",
        )
    solution = model.optimize(raise_error=False)
    require(
        solution.status == "optimal",
        "solver_status",
        f"Solver returned {solution.status}; no flux claim is permitted.",
    )
    from cobra.util.array import create_stoichiometric_matrix

    residual = create_stoichiometric_matrix(model) @ solution.fluxes.to_numpy()
    require(
        np.max(np.abs(residual), initial=0) < 1e-7,
        "mass_balance",
        "Steady-state residual exceeds tolerance.",
    )
    require(np.isfinite(solution.objective_value), "objective_value", "Nonfinite optimum.")
    return solution


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def begin_run():
    return {
        "run_id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "commands": [[sys.executable, *sys.argv]],
    }


def finish_run(run, output, inputs, parameters):
    """Call only after assertions and report generation succeeded."""
    output = Path(output)
    revision = dirty = None
    if shutil.which("git"):
        source_root = Path(__file__).resolve().parents[2]
        revision = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        dirty = subprocess.run(
            ["git", "-C", str(source_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    inputs = list(dict.fromkeys([*inputs, *Path(__file__).parent.glob("*.py")]))
    parameters = {
        **parameters,
        "git_unborn_or_unavailable": revision is None or revision.returncode != 0,
        "git_dirty": bool(dirty.stdout) if dirty is not None and dirty.returncode == 0 else None,
    }
    run.update(
        {
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "exit_status": 0,
            "git_revision": revision.stdout.strip()
            if revision is not None and revision.returncode == 0
            else None,
            "parameters": parameters,
            "random_seed": parameters.get("seed"),
            "inputs": [{"path": str(p), "sha256": sha256(p)} for p in inputs],
            "outputs": [
                {"path": str(p), "sha256": sha256(p)}
                for p in output.iterdir()
                if p.is_file() and p.name != "analysis_run.json"
            ],
            "software": {name: importlib.metadata.version(name) for name in ["numpy", "pandas"]},
        }
    )
    run["software"].update({"python": platform.python_version(), "platform": platform.platform()})
    for name in ["matplotlib", "cobra", "swiglpk", "scipy"]:
        try:
            run["software"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    write_json(output / "analysis_run.json", run)


def write_report(output, run, report):
    """Keep domain details separate from the portable five-level QA contract."""
    write_json(Path(output) / "scientific_report.json", report)
    checks = []
    for check_id, domain, status, explanation in [
        (
            "readiness",
            "input_integrity",
            "PASS",
            "Explicit synthetic inputs passed the implemented domain gates.",
        ),
        (
            "execution",
            "computation",
            "PASS",
            "Documented numerical assertions and deliberate invalid-input rejection passed.",
        ),
        (
            "method_scope",
            "statistical_methodology",
            "WARN",
            "Only the declared toy/readiness computation was run; no inferential or predictive validation.",
        ),
        (
            "biology",
            "biological_interpretation",
            "NOT_RUN",
            "Synthetic data provide no experimental biological evidence.",
        ),
        (
            "provenance",
            "provenance_reporting",
            "PASS",
            "Input and output hashes and installed versions recorded in analysis_run.json.",
        ),
    ]:
        checks.append(
            {
                "check_id": check_id,
                "domain": domain,
                "status": status,
                "evidence_path": "analysis_run.json"
                if check_id == "provenance"
                else "scientific_report.json",
                "severity": "ADVISORY",
                "explanation": explanation,
                "remediation": "Obtain domain expert review and real-data validation before scientific interpretation.",
            }
        )
    write_json(Path(output) / "validation_report.json", {"run_id": run["run_id"], "checks": checks})


def write_claims(path, claims):
    for claim in claims:
        claim["source_or_artifact"] = [claim["source_or_artifact"]]
        if isinstance(claim["limitations"], str):
            claim["limitations"] = [claim["limitations"]]
        claim.update(
            {
                "uncertainties": ["No independent human scientific review"],
                "approval_status": "not_applicable",
                "reviewer": {
                    "identity": "example assertions",
                    "kind": "tool",
                    "independent": False,
                },
            }
        )
    write_json(path, {"claims": claims})


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
