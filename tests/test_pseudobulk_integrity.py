"""Exact arithmetic and experimental-unit gates; synthetic data only."""

from copy import deepcopy
import json
import warnings

import numpy as np
import pandas as pd
import pytest

from bioskills.expanded import pseudobulk
from bioskills.science import ScientificValidationError, validate_counts
from bioskills.validators import read_table


@pytest.fixture
def cells():
    metadata = pd.DataFrame(
        {
            "subject_id": np.repeat(["0001", "1", "d3", "d4"], 4),
            "specimen_id": np.repeat(["s1", "s2", "s3", "s4"], 4),
            "condition": ["01"] * 8 + ["1"] * 8,
            "timepoint": ["baseline"] * 16,
            "cell_type": ["T"] * 16,
            "batch": ["one"] * 16,
        },
        index=[f"c{i}" for i in range(16)],
    )
    counts = pd.DataFrame(
        np.arange(320).reshape(20, 16) % 7 + 1,
        index=["0001", "1"] + [f"g{i}" for i in range(18)],
        columns=metadata.index,
    )
    return counts, metadata


def run(counts, metadata, **kwargs):
    return pseudobulk(
        counts, metadata, organism="synthetic", reference="v1", count_generation="fixture", **kwargs
    )


def test_exact_conservation_export_and_readiness(cells, tmp_path):
    counts, metadata = cells
    before = deepcopy(cells)
    bulk, samples, audit = run(*cells)
    assert bulk.shape == (20, 4) and str(bulk.dtypes.iloc[0]) == "int64"
    for name, row in samples.iterrows():
        selected = metadata.index[metadata.specimen_id == row.specimen_id]
        assert bulk[name].tolist() == [
            sum(int(x) for x in counts.loc[g, selected]) for g in counts.index
        ]
    assert audit["conservation"]["source_total_decimal"] == str(
        sum(int(x) for x in counts.to_numpy().flat)
    )
    assert (
        audit["missing_donor_condition"] == [] and audit["subjects"] == 4 and audit["cells"] == 16
    )
    assert audit["population_status"]["T"] == "READY_FOR_DESIGN_REVIEW"
    assert audit["differential_state"] == "NOT_RUN"
    pd.testing.assert_frame_equal(counts, before[0])
    pd.testing.assert_frame_equal(metadata, before[1])
    file = tmp_path / "counts.tsv"
    meta = tmp_path / "samples.tsv"
    bulk.to_csv(file, sep="\t", index_label="gene_id")
    samples.to_csv(meta, sep="\t")
    reloaded = read_table(file)
    mapped = read_table(meta)
    assert list(reloaded.index) == list(bulk.index)
    assert (
        validate_counts(reloaded, mapped, scale="raw_counts", organism="synthetic", reference="v1")[
            "status"
        ]
        == "PASS"
    )
    json.dumps(audit, allow_nan=False)


def test_observed_wraparound_rejected_before_export(cells):
    counts, meta = cells
    counts.iloc[0, :4] = 2**62
    before = counts.copy()
    with warnings.catch_warnings(record=True) as seen:
        with pytest.raises(ScientificValidationError, match="aggregate_range"):
            run(counts, meta)
    assert not seen
    pd.testing.assert_frame_equal(counts, before)


def test_observed_large_integer_case_remains_exact(cells):
    counts, meta = cells
    counts.iloc[0, 0] = 2**53 + 1
    bulk, samples, audit = run(counts, meta)
    expected = sum(int(x) for x in counts.iloc[0, :4])
    assert int(bulk.iloc[0, 0]) == expected
    assert audit["conservation"]["status"] == "PASS"
    assert not audit["population_design"]["T"]["r_count_range_compatible"]


@pytest.mark.parametrize(
    "value", [True, -0.1, -1, np.nan, np.inf, float(2**53), "1.00000000000000001", 2**63]
)
def test_invalid_counts(cells, value):
    counts, meta = cells
    counts = counts.astype(object)
    counts.iloc[0, 0] = value
    with pytest.raises(ScientificValidationError):
        run(counts, meta)


@pytest.mark.parametrize(
    "field", ["subject_id", "specimen_id", "condition", "batch", "cell_type", "timepoint"]
)
def test_duplicate_columns_controlled(cells, field):
    counts, meta = cells
    duplicate = meta[[field]].copy()
    duplicate.iloc[0, 0] = "contradiction"
    with pytest.raises(ScientificValidationError, match="metadata_columns"):
        run(counts, pd.concat([meta, duplicate], axis=1))


@pytest.mark.parametrize("paired", ["false", 1, None, []])
def test_paired_type(cells, paired):
    with pytest.raises(ScientificValidationError, match="paired"):
        run(*cells, paired=paired)


@pytest.mark.parametrize("field", ["subject_id", "specimen_id", "cell_type", "condition", "batch"])
def test_exact_categorical_types(cells, field):
    counts, meta = cells
    meta.at["c0", field] = 1
    with pytest.raises(ScientificValidationError):
        run(counts, meta)


def test_batch_confounding_is_not_design_readiness(cells):
    counts, meta = cells
    meta["batch"] = meta.condition
    bulk, _, audit = run(counts, meta)
    assert bulk.shape == (20, 4) and audit["aggregation_status"] == "EXECUTED"
    assert audit["population_status"]["T"] == "BLOCKED_POPULATION_INFERENCE"
    assert any("confounding" in x for x in audit["population_design"]["T"]["reasons"])


def test_paired_longitudinal_expectations_and_incomplete_population(cells):
    counts, meta = cells
    meta["subject_id"] = np.repeat(["d1", "d2", "d1", "d2"], 4)
    meta["timepoint"] = [0] * 8 + [1] * 8
    _, _, audit = run(counts, meta, paired=True)
    assert audit["population_status"]["T"] == "READY_FOR_DESIGN_REVIEW"
    assert audit["missing_donor_condition"] == []
    meta.loc["c12":"c15", "cell_type"] = "other"
    _, _, audit = run(counts, meta, paired=True)
    assert audit["population_status"]["T"] == "BLOCKED_POPULATION_INFERENCE"
    assert any(
        x["cell_type"] == "T" and x["subject_id"] == "d2" and x["condition"] == "1"
        for x in audit["missing_donor_condition"]
    )


def test_multiple_populations_and_reordering(cells):
    counts, meta = cells
    meta["cell_type"] = ["A", "B"] * 8
    bulk, samples, audit = run(counts, meta)
    reordered = run(counts.iloc[:, ::-1], meta.iloc[::-1])
    pd.testing.assert_frame_equal(bulk, reordered[0])
    assert bulk.shape == (20, 8) and audit["populations"] == 2
    assert sum(x["cells"] for x in audit["cells_per_sample"]) == 16


@pytest.mark.parametrize(
    "failure", ["alignment", "identity", "timepoint", "blank", "donors", "absent"]
)
def test_preserved_scientific_gates(cells, failure):
    counts, meta = cells
    if failure == "alignment":
        meta = meta.iloc[::-1]
    elif failure == "identity":
        meta.at["c0", "subject_id"] = "different"
    elif failure == "timepoint":
        meta.at["c0", "timepoint"] = "later"
    elif failure == "blank":
        meta.at["c0", "cell_type"] = " "
    elif failure == "donors":
        meta["subject_id"] = "one"
    else:
        meta.loc[:"c7", "cell_type"] = "other"
    if failure in {"donors", "absent"}:
        audit = run(counts, meta)[2]
        assert all(x == "BLOCKED_POPULATION_INFERENCE" for x in audit["population_status"].values())
    else:
        with pytest.raises(ScientificValidationError):
            run(counts, meta)
