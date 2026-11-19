"""Exercise every validator through its API and CLI on synthetic fixtures."""

import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pandas as pd
import pytest

from bioskills.science import sha256
from bioskills.validators import NAMES, evaluate, check_sample_ids

ROOT = Path(__file__).resolve().parents[1]


def fixture_files(tmp_path, name, state):
    input_file = tmp_path / "input.csv"
    metadata_file = None
    config = {}
    counts = pd.DataFrame(
        [[10, 15, 25, 30], [20, 25, 30, 40]], columns=list("abcd"), index=["g1", "g2"]
    )
    metadata = pd.DataFrame(
        {
            "subject_id": ["u1", "u2", "u3", "u4"],
            "condition": ["c", "c", "t", "t"],
            "split": ["train", "train", "test", "test"],
        },
        index=list("abcd"),
    )
    if name == "check_counts":
        config = {
            "scale": "raw_counts",
            "organism": "synthetic",
            "reference": "v1",
            "count_generation": "synthetic fixture",
        }
        if state == "invalid":
            config["scale"] = "TPM"
        counts.to_csv(input_file)
    elif name == "check_sample_ids":
        counts.to_csv(input_file)
        metadata_file = tmp_path / "metadata.csv"
        if state == "invalid":
            metadata = metadata.iloc[::-1]
        metadata.to_csv(metadata_file)
    elif name == "check_design_rank":
        design = pd.DataFrame({"intercept": [1] * 4, "condition": [0, 0, 1, 1]})
        if state == "invalid":
            design["batch"] = design.condition
        design.to_csv(input_file)
    elif name in {"check_replication", "check_leakage"}:
        if state == "invalid":
            if name == "check_replication":
                metadata.subject_id = ["same", "same", "same", "same"]
            else:
                metadata.loc["c", "subject_id"] = "u1"
        metadata.to_csv(input_file)
    elif name == "check_enrichment_background":
        input_file = tmp_path / "input.json"
        data = {
            "selected": ["g1"],
            "tested": ["g1", "g2", "g3"],
            "mappings": [
                {"source": gene, "target": gene, "organism": "synthetic", "reference": "v1"}
                for gene in ("g1", "g2", "g3")
            ],
        }
        config = {"organism": "synthetic", "reference": "v1", "multiple_testing": "BH"}
        if state == "invalid":
            data["tested"] = data["selected"]
        input_file.write_text(json.dumps(data))
    else:
        pytest.importorskip("cobra")
        from cobra.io import save_json_model
        from bioskills.science import toy_model

        input_file = tmp_path / "input.json"
        model = toy_model()
        if state == "invalid":
            model.reactions.EX_a.lower_bound = 0
            model.reactions.BIOMASS.lower_bound = 1
        save_json_model(model, str(input_file))
    if state == "malformed":
        input_file = tmp_path / "missing-input"
    return input_file, metadata_file, config


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("state,expected", [("valid", 0), ("invalid", 2), ("malformed", 1)])
def test_api_and_cli_reports(tmp_path, name, state, expected):
    input_file, metadata_file, config = fixture_files(tmp_path, name, state)
    before = sha256(input_file) if input_file.exists() else None
    report, code = evaluate(name, input_file, config, metadata_file)
    assert code == expected
    assert report["status"] == ("PASS" if state == "valid" else "FAIL")
    schema = json.loads((ROOT / "schemas/validator_report.schema.json").read_bytes())
    jsonschema.validate(report, schema)
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps(config))
    output = tmp_path / "report.json"
    command = [
        sys.executable,
        "-m",
        "bioskills",
        name,
        "--input",
        str(input_file),
        "--config",
        str(cfg),
        "--output",
        str(output),
    ]
    if metadata_file is not None:
        command += ["--metadata", str(metadata_file)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert result.returncode == expected, result.stderr
    disk = json.loads(output.read_bytes())
    jsonschema.validate(disk, schema)
    assert json.loads(result.stdout)["status"] == report["status"]
    assert disk["reason"] == report["reason"]
    assert "u1" not in output.read_text()
    if before:
        assert sha256(input_file) == before
        assert disk["input_hashes"]["input"] == before


def test_sample_order_is_explicit_and_immutable():
    counts = pd.DataFrame([[1, 2]], columns=["a", "b"])
    metadata = pd.DataFrame({"subject_id": ["u2", "u1"]}, index=["b", "a"])
    result = check_sample_ids(counts, metadata, allow_reorder=True)
    assert result["metadata_row_order"] == [1, 0] and result["status"] == "WARN"
    assert list(metadata.index) == ["b", "a"]


def test_missing_dependency_reports_blocked(tmp_path, monkeypatch):
    import builtins

    old_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.startswith("cobra"):
            raise ImportError("missing optional runtime")
        return old_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    model = tmp_path / "model.json"
    model.write_text("{}")
    report, code = evaluate("check_fba_status", model, {})
    assert code == 3 and report["status"] == "BLOCKED"
