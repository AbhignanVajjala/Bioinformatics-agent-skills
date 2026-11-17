"""Execute actual mini-projects and verify evidence contracts and preservation."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ["bulk-rnaseq", "multiomics", "metabolic-modeling"]


def read_json(path):
    return json.loads(path.read_text())


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("example", EXAMPLES)
def test_examples_execute_and_preserve_evidence(tmp_path, example):
    if example == "bulk-rnaseq":
        pytest.importorskip("matplotlib", reason="Install examples extra for the QC plot")
    if example == "metabolic-modeling":
        pytest.importorskip("cobra", reason="Install examples extra for constraint optimization")
    output = tmp_path / example
    env = os.environ.copy()
    env["XDG_CACHE_HOME"] = str(tmp_path / "cache")
    env["MPLCONFIGDIR"] = str(tmp_path / "matplotlib")
    command = [sys.executable, str(ROOT / "examples" / example / "run.py"), "--output", str(output)]
    completed = subprocess.run(
        command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    contracts = {
        "analysis_run.json": "analysis_run",
        "validation_report.json": "validation_report",
        "claims.json": "scientific_claim_ledger",
    }
    for filename, schema_name in contracts.items():
        schema = read_json(ROOT / "schemas" / f"{schema_name}.schema.json")
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
            read_json(output / filename)
        )

    run = read_json(output / "analysis_run.json")
    assert run["exit_status"] == 0
    assert run["commands"] == [command]
    assert datetime.fromisoformat(run["started_at"]) <= datetime.fromisoformat(run["ended_at"])
    assert run["inputs"] and run["outputs"]
    for artifact in run["inputs"] + run["outputs"]:
        path = Path(artifact["path"])
        if not path.is_absolute():
            path = ROOT / path
        assert file_hash(path) == artifact["sha256"]
    assert any(Path(row["path"]).name == "science.py" for row in run["inputs"])
    validation = read_json(output / "validation_report.json")
    assert validation["run_id"] == run["run_id"]
    checks = {row["domain"]: row for row in validation["checks"]}
    assert len(checks) == 5
    assert checks["biological_interpretation"]["status"] == "NOT_RUN"
    for check in checks.values():
        assert (output / check["evidence_path"]).is_file()
    for claim in read_json(output / "claims.json")["claims"]:
        assert claim["analysis_run_id"] == run["run_id"]
        assert claim["limitations"]
        assert claim["reviewer"]["independent"] is False
        for evidence in claim["source_or_artifact"]:
            assert (output / evidence).is_file()

    scientific = read_json(output / "scientific_report.json")
    assert scientific["negative_control"]["status"] == "PASS"
    if example == "bulk-rnaseq":
        assert scientific["design_rank"] == 3
        assert scientific["samples"] == 6
        assert scientific["differential_expression"] == "NOT_RUN"
        assert (output / "library-sizes.png").stat().st_size > 1000
    elif example == "multiomics":
        assert len(scientific["matched_specimens"]) == 7
        assert scientific["excluded_specimens"]["protein"] == ["specimen_extra"]
        assert scientific["integration_model"] == "NOT_RUN"
        concordance = read_json(output / "concordance.json")
        assert len(concordance) == 4
        assert all(0.8 < row["pearson_r"] <= 1 for row in concordance)
    else:
        assert scientific["fba_objective"] == pytest.approx(10)
        assert scientific["biomass_at_uptake_5"] == pytest.approx(5)
        assert "infeasible" in scientific["negative_control"]["detected"]
        assert (output / "fva.csv").is_file()
        assert (output / "pfba.csv").is_file()

    sentinel = output / "user-owned.txt"
    sentinel.write_text("Existing user data must survive reruns.\n")
    before = {path.name: file_hash(path) for path in output.iterdir() if path.is_file()}
    rerun = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert rerun.returncode != 0
    assert {path.name: file_hash(path) for path in output.iterdir() if path.is_file()} == before
