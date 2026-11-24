"""Python readiness/serialization regressions; native R fits have separate CI evidence."""

from copy import deepcopy
import json

import numpy as np
import pandas as pd
import pytest

from bioskills.science import ScientificValidationError, check_counts, validate_counts
from bioskills.validators import check_replication, check_sample_ids, evaluate, read_table


@pytest.fixture
def inputs():
    samples = ["0001", "1", "01", "sample_A"]
    counts = pd.DataFrame(
        [[10, 20, 30, 40], [30, 40, 50, 60]], index=["0001", "1"], columns=samples
    )
    metadata = pd.DataFrame(
        {"subject_id": ["0001", "1", "s3", "s4"], "condition": ["01", "01", "1", "1"]},
        index=samples,
    )
    return counts, metadata


def generic(counts):
    return check_counts(
        counts,
        scale="raw_counts",
        organism="synthetic",
        reference="v1",
        count_generation="synthetic",
    )


def ready(counts, metadata):
    return validate_counts(
        counts, metadata, scale="raw_counts", organism="synthetic", reference="v1"
    )


@pytest.mark.parametrize("field", ["subject_id", "condition", "batch"])
@pytest.mark.parametrize("contradictory", [False, True])
def test_duplicate_metadata_controlled(inputs, field, contradictory):
    counts, metadata = inputs
    metadata["batch"] = ["a", "b", "a", "b"]
    extra = metadata[[field]].copy()
    if contradictory:
        extra.iloc[0, 0] = "contradiction"
    duplicate = pd.concat([metadata, extra], axis=1)
    for call in (lambda: ready(counts, duplicate), lambda: check_replication(duplicate)):
        with pytest.raises(ScientificValidationError, match="metadata_columns"):
            call()


@pytest.mark.parametrize("value", [True, np.bool_(False)])
def test_boolean_counts_not_raw(inputs, value):
    counts, metadata = inputs
    for frame in [counts.astype(bool), counts.astype(object)]:
        frame.iloc[0, 0] = value
        with pytest.raises(ScientificValidationError, match="count_values"):
            generic(frame)
        with pytest.raises(ScientificValidationError, match="count_values"):
            ready(frame, metadata)


def test_r_limit_is_scoped_and_inputs_immutable(inputs):
    counts, metadata = inputs
    counts.iloc[0, 0] = 2**31 - 1
    assert ready(counts, metadata)["status"] == "PASS"
    counts.iloc[0, 0] += 1
    before = deepcopy((counts, metadata))
    assert generic(counts)["status"] == "PASS"
    with pytest.raises(ScientificValidationError, match="r_integer_range"):
        ready(counts, metadata)
    pd.testing.assert_frame_equal(counts, before[0])
    pd.testing.assert_frame_equal(metadata, before[1])


@pytest.mark.parametrize("value", [1e308, np.inf, np.nan, 2**53])
def test_invalid_generic_numerical_scope(inputs, value):
    counts, _ = inputs
    counts = counts.astype(float)
    counts.iloc[0, 0] = value
    with pytest.raises(ScientificValidationError):
        generic(counts)


@pytest.mark.parametrize("axis", ["index", "columns", "subject_id", "condition", "batch"])
def test_mixed_identity_types_controlled(inputs, axis):
    counts, metadata = inputs
    if axis == "index":
        counts.index = [1, "1"]
    elif axis == "columns":
        counts.columns = [1, "1", "01", "sample_A"]
    elif axis == "batch":
        metadata[axis] = [1, "1", "a", "b"]
    else:
        metadata.at["0001", axis] = 1
    with pytest.raises(ScientificValidationError):
        ready(counts, metadata)


def test_exact_file_identifier_roundtrip(tmp_path, inputs):
    counts, metadata = inputs
    counts.index = ["0001", "123456789012345678901234567890"]
    file = tmp_path / "counts.tsv"
    meta = tmp_path / "metadata.tsv"
    counts.to_csv(file, sep="\t")
    metadata.to_csv(meta, sep="\t")
    before = (file.read_bytes(), meta.read_bytes())
    parsed, parsed_meta = read_table(file), read_table(meta)
    assert list(parsed.index) == list(counts.index)
    assert list(parsed.columns) == list(counts.columns)
    pd.testing.assert_frame_equal(parsed_meta, metadata)
    assert check_sample_ids(parsed, parsed_meta)["status"] == "PASS"
    assert check_replication(parsed_meta)["status"] == "PASS"
    assert set(ready(parsed, parsed_meta)["independent_replicates"]) == {"01", "1"}
    assert (file.read_bytes(), meta.read_bytes()) == before
    report, code = evaluate(
        "check_counts",
        file,
        dict(scale="raw_counts", organism="synthetic", reference="v1", count_generation="fixture"),
    )
    assert code == 0
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize(
    "text",
    [
        "gene_id\ta\tb\ng\t1\t2\textra\n",
        "gene_id\ta\tb\nextra\tg\t1\t2\n",
        "gene_id\ta\tb\ng\t1\n",
        "gene_id\ta\ta\ng\t1\t2\n",
        "gene_id\ta\tb\ng\t1\t2\t\n",
    ],
)
def test_ragged_input_rejected_without_inferred_rows(tmp_path, text):
    file = tmp_path / "counts.tsv"
    file.write_text(text)
    with pytest.raises(ScientificValidationError):
        read_table(file)


@pytest.mark.parametrize("metadata", [None, [], {}])
def test_metadata_structure_is_controlled(inputs, metadata):
    with pytest.raises(ScientificValidationError, match="metadata_type"):
        ready(inputs[0], metadata)
    with pytest.raises(ScientificValidationError, match="metadata_type"):
        check_replication(metadata)


def test_cross_view_boolean_count_gate_is_consistent():
    from test_domain_recipes import views
    from bioskills.omics import cross_view_analysis

    matrices, maps, declarations, pairs = views.__wrapped__()
    matrices["rna"] = matrices["rna"].astype(bool)
    with pytest.raises(ScientificValidationError, match="count_values"):
        cross_view_analysis(matrices, maps, declarations, pairs)


@pytest.mark.parametrize("value", ["1.00000000000000001", "1e-9999"])
def test_text_integrality_is_not_lost_to_float(inputs, value):
    counts, metadata = inputs
    counts = counts.astype(str)
    counts.iloc[0, 0] = value
    with pytest.raises(ScientificValidationError, match="count_values"):
        generic(counts)
    with pytest.raises(ScientificValidationError, match="count_values"):
        ready(counts, metadata)
