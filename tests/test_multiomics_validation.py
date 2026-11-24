"""Scientific adversarial controls, independently calculated numerical references."""

from copy import deepcopy
from decimal import Decimal, localcontext
import warnings

import numpy as np
import pandas as pd
import pytest

from test_domain_recipes import views as declared_views
from bioskills.omics import cross_view_analysis, numerical_guard, stable_pearson
from bioskills.science import ScientificValidationError, reconcile_omics, validate_matrix


@pytest.fixture
def views():
    return declared_views.__wrapped__()


def decimal_reference(left, right):
    """Independent 100-digit centered covariance, using exact binary64 inputs."""
    with localcontext() as ctx:
        ctx.prec = 100
        vectors = []
        for data in (left, right):
            values = [Decimal.from_float(float(v)) for v in data]
            scale = max(map(abs, values))
            values = [v / scale for v in values]
            mean = sum(values) / len(values)
            vectors.append([v - mean for v in values])
        x, y = vectors
        return float(
            sum(a * b for a, b in zip(x, y, strict=True))
            / (sum(a * a for a in x) * sum(b * b for b in y)).sqrt()
        )


@pytest.mark.parametrize(
    "left,right,expected",
    [
        ([1, 2, 3, 4], [2, 4, 6, 8], 1),
        ([1, 2, 3, 4], [8, 6, 4, 2], -1),
        ([-1, 0, 1], [1, -2, 1], 0),
        ([1e308, -1e308, 1e308, -1e308], [2, 1, 4, 3], 1 / np.sqrt(5)),
        ([1e-308, 2e-308, 3e-308, 4e-308], [1, 2, 3, 4], 1),
    ],
)
def test_stable_reference(left, right, expected):
    state = np.geterr().copy()
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        actual = stable_pearson(left, right)
    assert not seen
    assert actual == pytest.approx(expected, abs=2e-15)
    assert actual == pytest.approx(decimal_reference(left, right), abs=2e-15)
    assert np.geterr() == state


def test_invariance_and_near_constant_policy():
    x = np.array([-3.0, 1.0, 5.0, 9.0])
    y = np.array([2.0, 8.0, 4.0, 7.0])
    assert stable_pearson(x, y) == pytest.approx(
        stable_pearson(x * 1e100, y * 0.25 + 100), abs=2e-15
    )
    for vector, gate in [([1, 1, 1], "constant"), ([1, 1 + 1e-15, 1 - 1e-15], "near_constant")]:
        with pytest.raises(ScientificValidationError, match=gate) as error:
            stable_pearson(vector, [1, 2, 3])
        assert error.value.evidence["analysis_status"] == "NOT_RUN"
    assert stable_pearson([1, 1 + 1e-8, 1 + 2e-8], [1, 2, 3]) == pytest.approx(1, abs=1e-14)


@pytest.mark.parametrize("kind", ["overflow", "underflow", "warning"])
def test_structured_failure_and_state_restoration(kind):
    state, filters = np.geterr().copy(), list(warnings.filters)
    events = []
    with pytest.raises(ScientificValidationError, match="numerical_reliability") as error:
        with numerical_guard("adversarial", events):
            if kind == "warning":
                warnings.warn("synthetic numerical warning", RuntimeWarning)
            else:
                np.multiply(
                    1e308 if kind == "overflow" else 1e-308, 1e308 if kind == "overflow" else 1e-308
                )
    assert error.value.evidence["analysis_status"] == "NOT_RUN"
    assert error.value.evidence["numerical_events"][0]["stage"] == "adversarial"
    assert np.geterr() == state and warnings.filters == filters


@pytest.mark.parametrize("field", ["specimen_id", "subject_id", "split", "timepoint"])
@pytest.mark.parametrize("operation", ["missing", "duplicate", "contradictory"])
def test_metadata_columns(views, field, operation):
    matrices, maps, decl, pairs = views
    table = maps["protein"]
    if operation == "missing":
        maps["protein"] = table.drop(columns=field)
    else:
        extra = table[[field]].copy()
        if operation == "contradictory":
            extra.iloc[0, 0] = "contradiction"
        maps["protein"] = pd.concat([table, extra], axis=1)
    with pytest.raises(ScientificValidationError, match="mapping_fields|mapping_columns"):
        cross_view_analysis(matrices, maps, decl, pairs)


@pytest.mark.parametrize(
    "assay,field",
    [
        ("rna", "namespace"),
        ("rna", "reference"),
        ("rna", "count_generation"),
        ("rna", "normalization_scope"),
        ("protein", "namespace"),
        ("protein", "reference"),
        ("protein", "modality"),
        ("rna", "scale"),
    ],
)
@pytest.mark.parametrize("value", [None, "", " \t", float("inf"), 123, []])
def test_meaningless_declarations(views, assay, field, value):
    views[2][assay][field] = value
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(*views)


@pytest.mark.parametrize("value", [None, "", " ", np.nan, np.inf, ["invalid"]])
def test_timepoint_values(views, value):
    views[1]["protein"].at["a", "timepoint"] = value
    with pytest.raises(ScientificValidationError, match="timepoint"):
        cross_view_analysis(*views)


@pytest.mark.parametrize(
    "operation",
    ["empty", "blank", "missing", "unknown", "duplicate", "columns", "mixed", "wrong_columns"],
)
def test_feature_maps(views, operation):
    matrices, maps, decl, pairs = views
    if operation == "empty":
        pairs = pairs.iloc[:0]
    elif operation == "columns":
        pairs = pd.concat([pairs, pairs[["rna"]]], axis=1)
    elif operation == "wrong_columns":
        pairs = pairs.rename(columns={"rna": "other"})
    elif operation == "duplicate":
        pairs.loc[1, "rna"] = "g1"
    else:
        pairs.at[0, "rna"] = {"blank": " ", "missing": None, "unknown": "no-such-gene", "mixed": 1}[
            operation
        ]
    with pytest.raises(ScientificValidationError, match="feature_map"):
        cross_view_analysis(matrices, maps, decl, pairs)


@pytest.mark.parametrize("group", [0, 1, 2])
@pytest.mark.parametrize("operation", ["missing", "extra", "wrong_type"])
def test_modality_keys(views, group, operation):
    data = list(views)
    if operation == "missing":
        del data[group]["protein"]
    elif operation == "extra":
        data[group]["other"] = data[group]["protein"]
    else:
        data[group] = []
    with pytest.raises(ScientificValidationError, match="modalities"):
        cross_view_analysis(*data)


@pytest.mark.parametrize("group,key", [(0, "protein"), (1, "protein"), (2, "protein")])
def test_malformed_structures(views, group, key):
    views[group][key] = []
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(*views)


@pytest.mark.parametrize("value", [np.inf, np.nan, "not-a-number"])
def test_whole_matrix_integrity(views, value):
    matrices = views[0]
    matrices["protein"].loc["unused"] = [value, 1, 1, 1]
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(*views)


def test_empty_and_mixed_identifiers(views):
    with pytest.raises(ScientificValidationError, match="empty_matrix"):
        validate_matrix(pd.DataFrame())
    for labels in [["g", 1], ["g", " "], ["g", None], ["g", "g"]]:
        matrix = views[0]["rna"].copy()
        matrix.index = labels
        with pytest.raises(ScientificValidationError):
            validate_matrix(matrix)


@pytest.mark.parametrize("number", [0, 1, 2])
def test_insufficient_overlap(views, number):
    matrices, maps, _, _ = views
    for i in range(number, 4):
        maps["protein"].iloc[i, maps["protein"].columns.get_loc("specimen_id")] = f"extra{i}"
    with pytest.raises(ScientificValidationError, match="overlap"):
        reconcile_omics(matrices, maps)


def test_reordering_immutability_and_unmapped_constant(views):
    original = deepcopy(views)
    baseline = cross_view_analysis(*views)
    for value, old in zip(views[:2], original[:2], strict=True):
        for key in value:
            pd.testing.assert_frame_equal(value[key], old[key])
    assert views[2] == original[2]
    pd.testing.assert_frame_equal(views[3], original[3])
    views[0]["protein"].loc["unused"] = 1
    views[0]["protein"] = views[0]["protein"].iloc[:, ::-1]
    views[1]["protein"] = views[1]["protein"].iloc[::-1]
    result = cross_view_analysis(*views)
    assert result["correlations"] == baseline["correlations"]
    assert result["feature_inventory"]["protein"]["constant_unmapped_features"] == ["unused"]
    views[0]["protein"].loc["p1"] = 1
    with pytest.raises(ScientificValidationError, match="constant_feature"):
        cross_view_analysis(*views)


def test_population_and_partition_semantics(views):
    for table in views[1].values():
        table["subject_id"] = "one"
        table["split"] = "test"
        table["timepoint"] = [0, 1, 2, 3]
    result = cross_view_analysis(*views)
    audit = result["audit"]
    assert audit["matched_subject_count"] == 1 and audit["matched_specimen_count"] == 4
    assert audit["specimens_per_subject"] == [{"subject_id": "one", "specimens": 4}]
    assert audit["partitions"] == {"test": {"specimens": 4, "subjects": 1}}
    assert len(audit["warnings"]) == 4
    assert [row["timepoint"] for row in result["timepoints"]] == [0, 1, 2, 3]
    assert result["prediction_status"] == result["inference_status"] == "NOT_RUN"


def test_denominator_uses_unmapped_rna(views):
    original = cross_view_analysis(*views)
    views[3].drop(index=1, inplace=True)
    subset = cross_view_analysis(*views)
    assert original["normalization"] == subset["normalization"]
    assert original["correlations"][0] == subset["correlations"][0]
    views[0]["rna"].loc["unused"] = [7, 7, 7, 7]
    augmented = cross_view_analysis(*views)
    assert augmented["normalization"]["rna"]["libraries"][0]["library_size"] == 67
    assert augmented["normalization"]["rna"]["feature_count"] == 3


def test_executed_report_schema_and_empty_failure(views):
    import json
    from pathlib import Path
    import jsonschema

    schema = json.loads(Path("schemas/cross_view.schema.json").read_text())
    result = cross_view_analysis(*views)
    jsonschema.validate(result, schema)
    result["correlations"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(result, schema)


def test_failed_input_is_immutable(views):
    views[3].loc[1, "rna"] = "missing"
    before = deepcopy(views)
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(*views)
    for group in [0, 1]:
        for name in views[group]:
            pd.testing.assert_frame_equal(views[group][name], before[group][name])
    assert views[2] == before[2]
    pd.testing.assert_frame_equal(views[3], before[3])


def test_extreme_dynamic_range_fails_closed():
    with pytest.raises(ScientificValidationError, match="numerical_reliability") as error:
        stable_pearson([1e308, 1e-308, -1e308], [1, 2, 3])
    assert error.value.evidence["numerical_events"][0]["stage"] == "pearson"


@pytest.mark.parametrize("value", [1e308, 2**52])
def test_shared_count_gate_prevents_sum_overflow(value):
    from bioskills.science import check_counts

    counts = pd.DataFrame([[value] * 3, [value] * 3])
    with pytest.raises(ScientificValidationError, match="count_range"):
        check_counts(
            counts,
            scale="raw_counts",
            organism="synthetic",
            reference="v1",
            count_generation="synthetic",
        )


def test_complex_matrix_is_not_silently_cast():
    with pytest.raises(ScientificValidationError, match="numeric_matrix"):
        validate_matrix(pd.DataFrame([[1 + 2j, 2 + 3j, 3 + 4j]]))


def test_duplicate_declarations_where_representable(views):
    views[2]["protein"] = pd.Series(["protein", "rna"], index=["modality", "modality"])
    with pytest.raises(ScientificValidationError, match="declaration"):
        cross_view_analysis(*views)


@pytest.mark.parametrize("field", ["specimen_id", "subject_id"])
def test_mixed_identity_types_across_assays(views, field):
    views[1]["protein"][field] = [1, 2, 3, 4]
    with pytest.raises(ScientificValidationError, match=field):
        cross_view_analysis(*views)


@pytest.mark.parametrize(
    "failure",
    ["huge", "sum", "zero", "fractional", "negative", "universe", "external", "TPM", "modality"],
)
def test_count_normalization_failures(views, failure):
    matrices, _, decl, _ = views
    if failure in {"huge", "sum", "zero", "fractional", "negative"}:
        matrices["rna"] = matrices["rna"].astype(float)
        if failure == "sum":
            matrices["rna"].iloc[:, 0] = 2**52
        elif failure == "zero":
            matrices["rna"].iloc[:, 0] = 0
        else:
            matrices["rna"].iloc[0, 0] = {"huge": 1e308, "fractional": 0.5, "negative": -1}[failure]
    elif failure == "universe":
        decl["rna"]["count_universe"] = "preselected"
    elif failure == "external":
        decl["rna"]["library_sizes"] = [10] * 4
    elif failure == "TPM":
        decl["rna"]["scale"] = "TPM"
    else:
        decl["rna"]["modality"] = "protein"
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(*views)


def test_extreme_observed_fixture_reference(tmp_path):
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("recipe", Path("examples/domain-recipes/run.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = tmp_path / "fixture"
    baseline, _ = module.multiomics_example(output)
    matrices = {
        name: pd.read_csv(output / f"{name}-matrix.csv", index_col=0) for name in ["rna", "protein"]
    }
    maps = {name: pd.read_csv(output / f"{name}-mapping.csv", index_col=0) for name in matrices}
    extreme = [1e308, -1e308] * 4
    matrices["protein"].loc["protein0"] = extreme
    pairs = pd.DataFrame({"rna": matrices["rna"].index, "protein": matrices["protein"].index})
    result = cross_view_analysis(matrices, maps, baseline["declarations"], pairs)
    counts = matrices["rna"].to_numpy(dtype=float)
    transformed = np.log1p(counts[0] / counts.sum(axis=0) * 1e6) / np.log(2.0)
    reference = decimal_reference(transformed, extreme)
    assert result["correlations"][0]["pearson_r"] == pytest.approx(reference, abs=2e-15)
    assert abs(reference) > 0.01  # the former arbitrary zero is incorrect
    assert result["numerical_evidence"]["events"] == []
    assert [row["pearson_r"] for row in baseline["correlations"]] == pytest.approx(
        [-0.18037311612127607, 0.3734261770509437, 0.41865422771703026, -0.6020016995027743],
        abs=2e-13,
    )
