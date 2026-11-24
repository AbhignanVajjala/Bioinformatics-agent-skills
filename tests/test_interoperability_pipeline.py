"""Permanent cross-component fixture; native methods execute only in pinned R CI."""

import importlib.util
import json
import os
from pathlib import Path
import shutil

import pytest

from bioskills.validators import read_table

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "interop", ROOT / "examples/pseudobulk-to-enrichment/run.py"
)
recipe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipe)


def test_exact_permanent_preparation_and_honest_status(tmp_path):
    output = tmp_path / "fresh"
    assert recipe.main(["--output", str(output), "--prepare-only"]) == 0
    report = json.loads((output / "pipeline-status.json").read_bytes())
    assert (report["genes"], report["cells"], report["donors"], report["planted_genes"]) == (
        600,
        48,
        12,
        50,
    )
    assert report["agent_execution"] == report["biological_validation"] == "NOT_RUN"
    assert all(x["status"] == "NOT_RUN" for x in report["methods"].values())
    assert report["aggregation"]["conservation"]["status"] == "PASS"
    assert read_table(output / "counts.tsv").index.tolist() == [f"{i:06d}" for i in range(600)]
    assert read_table(output / "samples.tsv").subject_id.tolist() == [
        f"{i:04d}" for i in range(1, 13)
    ]
    assert all(recipe.sha(output / name) == value for name, value in report["input_sha256"].items())


def test_cached_output_is_not_a_new_run(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    artifact = output / "preserved.txt"
    artifact.write_bytes(b"old evidence")
    with pytest.raises(SystemExit) as error:
        recipe.main(["--output", str(output), "--prepare-only"])
    assert error.value.code == 2 and artifact.read_bytes() == b"old evidence"


@pytest.fixture(scope="module")
def native_pipeline():
    if os.environ.get("BIOSKILLS_NATIVE_R_TESTS") != "1":
        pytest.skip("Two native-method interoperability checks require pinned R CI")
    assert shutil.which("Rscript"), "Pinned R execution is required, not optional in this job"
    output = ROOT / "artifacts/rnaseq-phase9"
    assert recipe.main(["--output", str(output)]) == 0
    return output, json.loads((output / "pipeline-status.json").read_bytes())


@pytest.mark.parametrize("method", ["deseq2", "edger"])
def test_native_600_gene_filtering_and_downstream_lineage(native_pipeline, method):
    output, report = native_pipeline
    actual = report["methods"][method]
    assert actual["status"] == "EXECUTED" and actual["exit_status"] == 0
    assert actual["filtering_ids_preserved"] == 600 and actual["planted_recovered"] == 50
    assert actual["independent_fisher_bh"] == "PASS"
    assert actual["selected_positive_effect_fdr_005"] < actual["tested"]
    assert actual["provenance"]["counts_sha256"] == recipe.sha(output / "counts.tsv")
    assert actual["provenance"]["native_results_sha256"] == recipe.sha(
        output / method / "results.tsv"
    )
    assert read_table(output / method / "filtering.tsv").index.tolist() == [
        f"{i:06d}" for i in range(600)
    ]
