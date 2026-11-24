"""Scoped descriptive multi-omics analysis; no inferential or predictive fitting."""

from collections.abc import Mapping
from contextlib import contextmanager
import math
import warnings

import numpy as np
import pandas as pd

from bioskills.science import (
    ScientificValidationError,
    exact_count_totals,
    reconcile_omics,
    require,
    validate_labels,
    validate_mapping,
    validate_matrix,
)


@contextmanager
def numerical_guard(stage, events):
    """Fail on numerical warnings/errors, retain evidence, restore caller state."""
    try:
        with warnings.catch_warnings(), np.errstate(all="raise"):
            warnings.simplefilter("error", RuntimeWarning)
            yield
    except (FloatingPointError, RuntimeWarning, OverflowError) as exc:
        events.append({"stage": stage, "category": type(exc).__name__, "message": str(exc)})
        raise ScientificValidationError(
            f"numerical_reliability: {stage}: {exc}",
            evidence={"analysis_status": "NOT_RUN", "numerical_events": list(events)},
        ) from exc


def stable_pearson(left, right, *, events=None):
    """Scale before centering; use compensated sums and unit-vector dot product.

    Near-constant vectors (maximum centered scaled variation <=64 eps)
    are rejected: subtraction accuracy cannot be guaranteed in binary64.
    """
    events = [] if events is None else events
    with numerical_guard("pearson", events):
        vectors = []
        for value in (left, right):
            x = np.asarray(value, dtype=float)
            require(
                x.ndim == 1 and len(x) >= 3 and np.isfinite(x).all(),
                "pearson_input",
                "Need >=3 finite observations per vector.",
            )
            scale = float(np.max(np.abs(x)))
            require(
                scale > 0 and not np.all(x == x[0]),
                "constant_feature",
                "Mapped feature is constant; correlation undefined. No partial execution.",
            )
            # Power-of-two scaling is exact when representable, avoiding an
            # extra rounding of every value before cancellation-sensitive centering.
            scaled = np.ldexp(x, -math.frexp(scale)[1])
            shifted = scaled - scaled[0]
            mean = math.fsum(shifted) / len(shifted)
            centered = shifted - mean
            magnitude = float(np.max(np.abs(centered)))
            require(
                magnitude > 64 * np.finfo(float).eps,
                "near_constant_feature",
                "Mapped variation is too small relative to magnitude for reliable binary64 correlation.",
            )
            centered = centered / magnitude
            norm = math.sqrt(math.fsum(np.multiply(centered, centered)))
            vectors.append(centered / norm)
        require(len(vectors[0]) == len(vectors[1]), "pearson_input", "Unequal vector lengths.")
        r = math.fsum(np.multiply(*vectors))
        require(
            math.isfinite(r) and abs(r) <= 1 + 16 * np.finfo(float).eps,
            "pearson_range",
            "Correlation outside justified binary64 tolerance.",
        )
        return min(1.0, max(-1.0, r))


def _text(value, field):
    require(
        isinstance(value, str) and bool(value.strip()),
        field,
        f"{field} requires a nonblank string declaration.",
    )


def cross_view_analysis(matrices, mappings, declarations, feature_map):
    """Reject invalid inputs entirely; EXECUTED means all requested pairs computed."""
    require(
        all(isinstance(x, Mapping) for x in (matrices, mappings, declarations)),
        "modalities",
        "Matrices, mappings and declarations must be mappings.",
    )
    require(
        len(matrices) == 2 and set(matrices) == set(mappings) == set(declarations),
        "modalities",
        "Exactly two assays with identical matrix/map/declaration keys required.",
    )
    names = list(matrices)
    validate_labels(names, "assay_names")
    require(
        all(isinstance(name, str) for name in names), "assay_names", "String assay names required."
    )
    for name in names:
        validate_matrix(matrices[name])  # Whole-matrix integrity, including unused rows/columns.
        validate_mapping(mappings[name], matrices[name], timepoint=True)
        declaration = declarations[name]
        require(
            isinstance(declaration, Mapping),
            "declaration",
            "Per-assay declaration must be a mapping.",
        )
        for field in ("namespace", "reference", "modality", "scale"):
            _text(declaration.get(field), field)
        if declaration["scale"] == "raw_counts":
            require(declaration["modality"] == "rna", "modality_scale", "Raw counts require RNA.")
            _text(declaration.get("count_generation"), "count_provenance")
            _text(declaration.get("count_universe"), "count_universe")
            require(
                declaration.get("count_universe") == "complete_supplied_matrix",
                "count_universe",
                "Declare complete_supplied_matrix as intended normalization universe; preselected subsets unsupported.",
            )
            _text(declaration.get("normalization_scope"), "normalization_scope")
            require(
                "library_sizes" not in declaration,
                "normalization_scope",
                "External denominators are unsupported; supply the complete intended matrix.",
            )
        else:
            require(
                declaration["scale"] == "log2_intensity"
                and declaration["modality"] in {"protein", "metabolite"},
                "modality_scale",
                "Only RNA raw_counts or protein/metabolite log2_intensity supported.",
            )
    validate_labels([v for table in mappings.values() for v in table.timepoint], "timepoint")
    timepoints = {}
    for mapping in mappings.values():
        for row in mapping.itertuples():
            require(
                row.specimen_id not in timepoints or timepoints[row.specimen_id] == row.timepoint,
                "timepoint_mismatch",
                "Cross-assay timepoints disagree.",
            )
            timepoints[row.specimen_id] = row.timepoint
    aligned, audit = reconcile_omics(matrices, mappings)
    require(
        isinstance(feature_map, pd.DataFrame), "feature_map", "Feature map must be a DataFrame."
    )
    require(
        feature_map.columns.is_unique and set(feature_map) == set(names) and len(feature_map) > 0,
        "feature_map",
        "Nonempty feature map with unique assay columns required.",
    )
    for name in names:
        validate_labels(feature_map[name], "feature_map")
        validate_labels([*matrices[name].index, *feature_map[name]], "feature_map")
        require(
            feature_map[name].is_unique and feature_map[name].isin(matrices[name].index).all(),
            "feature_map",
            "Mapped features must exist and be one-to-one.",
        )
    transformed, normalization, inventory, events = {}, {}, {}, []
    for name in names:
        values = validate_matrix(matrices[name])
        declaration = declarations[name]
        with numerical_guard(f"transform:{name}", events):
            if declaration["scale"] == "raw_counts":
                totals = exact_count_totals(values)
                normalized = np.log1p(values / np.asarray(totals) * 1e6) / np.log(2.0)
                normalization[name] = {
                    "denominator_source": "sum of every supplied count row before pair selection",
                    "count_universe": declaration["count_universe"],
                    "scope": declaration["normalization_scope"],
                    "feature_count": len(values),
                    "libraries": [
                        {"assay_sample_id": sample, "library_size": total}
                        for sample, total in zip(matrices[name].columns, totals, strict=True)
                    ],
                    "limitations": "Declared universe/provenance not authenticated; CPM does not resolve compositional bias universally.",
                }
            else:
                normalized = values.copy()
            require(
                np.isfinite(normalized).all(), "transformation", "Nonfinite transformed values."
            )
        frame = pd.DataFrame(
            normalized, index=matrices[name].index, columns=mappings[name].specimen_id
        )
        transformed[name] = frame.loc[:, audit["matched_specimens"]]
        unmapped = matrices[name].index[~matrices[name].index.isin(feature_map[name])].tolist()
        inventory[name] = {
            "unmapped_features": unmapped,
            "constant_unmapped_features": [
                feature for feature in unmapped if transformed[name].loc[feature].nunique() == 1
            ],
            "unmapped_rna_rows_retained_for_normalization": declaration["scale"] == "raw_counts",
        }
    rows = []
    for pair in feature_map.to_dict("records"):
        left, right = (transformed[name].loc[pair[name]].to_numpy() for name in names)
        rows.append({**pair, "pearson_r": stable_pearson(left, right, events=events)})
    return {
        "report_version": 2,
        "analysis_status": "EXECUTED",
        "method": "descriptive cross-view Pearson association",
        "audit": audit,
        "correlations": rows,
        "declarations": {k: dict(v) for k, v in declarations.items()},
        "timepoints": [
            {"specimen_id": specimen, "timepoint": timepoints[specimen]}
            for specimen in audit["matched_specimens"]
        ],
        "normalization": normalization,
        "feature_inventory": inventory,
        "numerical_evidence": {
            "status": "PASS",
            "events": events,
            "policy": "Scoped floating-point exceptions and RuntimeWarnings block execution; caller settings restored.",
            "method": "exact power-of-two scaling, shifted compensated mean/dot sums, rescaled centered unit vectors",
            "near_constant_threshold": "max centered scaled variation <=64*binary64 epsilon rejected",
            "range_tolerance": "16*binary64 epsilon; only roundoff excursions clipped",
        },
        "undefined_pair_policy": "Reject complete analysis; no partial EXECUTED report",
        "inference_status": "NOT_RUN",
        "prediction_status": "NOT_RUN",
        "missingness_policy": "Reject missing/nonfinite values before analysis",
        "transformations": {
            name: "log2(CPM+1)"
            if declarations[name]["scale"] == "raw_counts"
            else "declared log2 intensity unchanged"
            for name in names
        },
        "limitations": [
            "No imputation, inference, MOFA2, SNF or prediction model executed",
            "Specimen-level descriptive association is not independent-subject inference, causality or predictive validation",
            "Independent biological identity and assay provenance are not established by declarations",
        ],
    }
