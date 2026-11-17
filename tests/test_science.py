"""Negative gates and numerical regressions; synthetic data only."""

import warnings
import pytest

np = pytest.importorskip("numpy", reason="Install scientific extra")
pd = pytest.importorskip("pandas", reason="Install scientific extra")
from bioskills.science import (  # noqa: E402
    ScientificValidationError,
    reconcile_omics,
    solve_model,
    toy_model,
    validate_counts,
)


@pytest.fixture
def counts_data():
    counts = pd.DataFrame(
        [[10, 12, 8, 16, 19, 15], [20, 22, 18, 17, 21, 23]],
        index=["g1", "g2"],
        columns=list("abcdef"),
    )
    metadata = pd.DataFrame(
        {
            "condition": ["c"] * 3 + ["t"] * 3,
            "subject_id": list("ABCDEF"),
            "batch": ["x", "y", "x", "y", "x", "y"],
        },
        index=list("abcdef"),
    )
    return counts, metadata


def validate(c, m, **kwargs):
    return validate_counts(
        c, m, scale=kwargs.get("scale", "raw_counts"), organism="synthetic", reference="v1"
    )


def test_count_readiness(counts_data):
    result = validate(*counts_data)
    assert result["status"] == "PASS"
    assert result["design_rank"] == 3


def test_sample_mismatch(counts_data):
    c, m = counts_data
    with pytest.raises(ScientificValidationError, match="sample_alignment"):
        validate(c, m.iloc[::-1])


def test_batch_confounding(counts_data):
    c, m = counts_data
    m["batch"] = m.condition
    with pytest.raises(ScientificValidationError, match="confounding"):
        validate(c, m)


def test_tpm_rejected(counts_data):
    # Even integer-valued TPM must be rejected based on declared scale.
    with pytest.raises(ScientificValidationError, match="count_scale"):
        validate(*counts_data, scale="TPM")


def test_replication(counts_data):
    c, m = counts_data
    m["condition"] = ["c"] * 5 + ["t"]
    with pytest.raises(ScientificValidationError, match="replication"):
        validate(c, m)


def test_repeated_subjects(counts_data):
    c, m = counts_data
    m["subject_id"] = ["A", "A", "B", "C", "D", "E"]
    with pytest.raises(ScientificValidationError, match="experimental_unit"):
        validate(c, m)


@pytest.mark.parametrize("value", [-1, 0.5, float("nan"), float("inf")])
def test_invalid_counts(counts_data, value):
    c, m = counts_data
    c = c.astype(float)
    c.iloc[0, 0] = value
    with pytest.raises(ScientificValidationError):
        validate(c, m)


def test_duplicate_features(counts_data):
    c, m = counts_data
    c.index = ["g", "g"]
    with pytest.raises(ScientificValidationError, match="duplicate_ids"):
        validate(c, m)


def test_zero_library(counts_data):
    c, m = counts_data
    c["a"] = 0
    with pytest.raises(ScientificValidationError, match="empty_library"):
        validate(c, m)


@pytest.fixture
def omics_data():
    matrices = {
        name: pd.DataFrame([[1.0, 2.0, 3.0, 4.0]], index=[name + "feature"], columns=list("abcd"))
        for name in ["rna", "protein"]
    }
    mappings = {
        name: pd.DataFrame(
            {
                "specimen_id": list("ABCD"),
                "subject_id": list("WXYZ"),
                "split": ["train", "train", "test", "test"],
            },
            index=list("abcd"),
        )
        for name in matrices
    }
    return matrices, mappings


def test_omics_reconciliation(omics_data):
    matrices, mappings = omics_data
    mappings["protein"].loc["d", ["specimen_id", "subject_id"]] = ["extra", "extra_subject"]
    aligned, report = reconcile_omics(matrices, mappings)
    assert report["matched_specimens"] == list("ABC")
    assert report["excluded_specimens"] == {"rna": ["D"], "protein": ["extra"]}
    assert list(aligned["protein"].columns) == list("ABC")


def test_omics_identity_mismatch(omics_data):
    matrices, mappings = omics_data
    mappings["protein"].loc["a", "subject_id"] = "wrong"
    with pytest.raises(ScientificValidationError, match="identity_mismatch"):
        reconcile_omics(matrices, mappings)


def test_patient_leakage(omics_data):
    matrices, mappings = omics_data
    for mapping in mappings.values():
        mapping.loc["c", "subject_id"] = "W"
    with pytest.raises(ScientificValidationError, match="patient_leakage"):
        reconcile_omics(matrices, mappings)


def test_metabolic_optimum():
    pytest.importorskip("cobra")
    model = toy_model()
    solution = solve_model(model)
    assert solution.objective_value == pytest.approx(10)
    assert solution.fluxes.EX_a == pytest.approx(-10)
    with model:
        model.reactions.EX_a.lower_bound = -3
        assert solve_model(model).objective_value == pytest.approx(3)
    assert solve_model(model).objective_value == pytest.approx(10)


def test_metabolic_infeasible():
    pytest.importorskip("cobra")
    model = toy_model()
    model.reactions.EX_a.lower_bound = 0
    model.reactions.BIOMASS.lower_bound = 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with pytest.raises(
            ScientificValidationError, match="solver_status: Solver returned infeasible"
        ):
            solve_model(model)


def test_metabolic_missing_objective():
    pytest.importorskip("cobra")
    model = toy_model()
    model.objective = {}
    with pytest.raises(ScientificValidationError, match="objective"):
        solve_model(model)


def test_metabolic_invalid_bounds():
    pytest.importorskip("cobra")
    model = toy_model()
    # Supported library setter rejects inconsistent bounds before optimization.
    with pytest.raises(ValueError):
        model.reactions.EX_a.bounds = (2, 1)


def test_numeric_batches_are_categorical(counts_data):
    c, m = counts_data
    m["batch"] = [1, 1, 2, 3, 4, 4]
    with pytest.raises(ScientificValidationError, match="confounding"):
        validate(c, m)


@pytest.mark.parametrize("field", ["condition", "batch", "subject_id"])
def test_blank_metadata_rejected(counts_data, field):
    c, m = counts_data
    m.loc["a", field] = " "
    with pytest.raises(ScientificValidationError, match="metadata_missing"):
        validate(c, m)


@pytest.mark.parametrize("domain", ["bulk-rnaseq", "multiomics", "metabolic-modeling"])
def test_examples_refuse_nonempty_output(tmp_path, domain):
    import os
    import subprocess
    import sys
    from pathlib import Path

    pytest.importorskip("matplotlib")
    pytest.importorskip("cobra")
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "previous_run"
    output.mkdir()
    sentinel = output / "analysis_run.json"
    sentinel.write_text('{"previous": "do not overwrite"}')
    before = sentinel.read_bytes()
    environment = dict(
        os.environ, XDG_CACHE_HOME=str(tmp_path / "cache"), MPLCONFIGDIR=str(tmp_path / "mpl")
    )
    result = subprocess.run(
        [sys.executable, str(root / "examples" / domain / "run.py"), "--output", str(output)],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    assert result.returncode == 2
    assert "Output directory must be empty" in result.stderr
    assert sentinel.read_bytes() == before
    assert list(output.iterdir()) == [sentinel]
