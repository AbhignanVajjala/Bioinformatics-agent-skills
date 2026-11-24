"""Synthetic scientific controls for the executable domain recipes."""

import numpy as np
import pandas as pd
import pytest

from bioskills.domain_workflows import check_fba_status, cross_view_analysis, metabolic_recipe
from bioskills.science import ScientificValidationError, solve_model, toy_model


@pytest.fixture
def views():
    samples = list("abcd")
    matrices = {
        "rna": pd.DataFrame(
            [[10, 20, 35, 55], [50, 40, 25, 10]], columns=samples, index=["g1", "g2"]
        ),
        "protein": pd.DataFrame([[2, 3, 4, 5], [5, 4, 3, 2]], columns=samples, index=["p1", "p2"]),
    }
    maps = {
        name: pd.DataFrame(
            {
                "subject_id": samples,
                "specimen_id": samples,
                "timepoint": ["t0"] * 4,
                "split": ["train", "train", "test", "test"],
            },
            index=samples,
        )
        for name in matrices
    }
    declarations = {
        "rna": {
            "scale": "raw_counts",
            "modality": "rna",
            "count_generation": "synthetic",
            "count_universe": "complete_supplied_matrix",
            "normalization_scope": "All synthetic generated genes",
            "namespace": "genes",
            "reference": "synthetic-v1",
        },
        "protein": {
            "scale": "log2_intensity",
            "modality": "protein",
            "namespace": "proteins",
            "reference": "synthetic-v1",
        },
    }
    mapping = pd.DataFrame({"rna": ["g1", "g2"], "protein": ["p1", "p2"]})
    return matrices, maps, declarations, mapping


def test_cross_view_calculations(views):
    result = cross_view_analysis(*views)
    assert result["analysis_status"] == "EXECUTED"
    assert len(result["correlations"]) == 2
    assert all(row["pearson_r"] > 0.95 for row in result["correlations"])
    assert result["audit"]["matched_specimens"] == list("abcd")


@pytest.mark.parametrize(
    "failure",
    [
        "permutation",
        "duplicate",
        "leakage",
        "scale",
        "timepoint",
        "namespace",
        "missing",
        "mapping",
    ],
)
def test_cross_view_scientific_failures(views, failure):
    matrices, maps, declarations, mapping = views
    if failure == "permutation":
        maps["protein"] = maps["protein"].iloc[::-1]
    elif failure == "duplicate":
        maps["protein"].loc["b", "specimen_id"] = "a"
    elif failure == "leakage":
        for table in maps.values():
            table.loc["c", "subject_id"] = "a"
    elif failure == "scale":
        declarations["rna"]["scale"] = "TPM"
    elif failure == "timepoint":
        maps["protein"].loc["a", "timepoint"] = "other"
    elif failure == "namespace":
        del declarations["protein"]["namespace"]
    elif failure == "missing":
        matrices["protein"].iloc[0, 0] = np.nan
    else:
        mapping.loc[1, "rna"] = "g1"
    with pytest.raises(ScientificValidationError):
        cross_view_analysis(matrices, maps, declarations, mapping)


def test_metabolic_recipe_executes(tmp_path):
    pytest.importorskip("cobra")
    report = metabolic_recipe(tmp_path / "recipe")
    assert report["analysis_status"] == "EXECUTED"
    assert report["infeasible_control"] == "infeasible"
    assert report["unbounded_control"] == "unbounded"
    assert report["restored_growth"] == pytest.approx(10)
    assert [row["product"] for row in report["tradeoff"]] == pytest.approx([10, 5, 1])


def test_flux_bounds_gate():
    pytest.importorskip("cobra")
    model = toy_model()
    solution = solve_model(model)
    assert check_fba_status(model, solution)["status"] == "PASS"
    solution.fluxes.loc["BIOMASS"] = 11
    with pytest.raises(ScientificValidationError):
        check_fba_status(model, solution)
