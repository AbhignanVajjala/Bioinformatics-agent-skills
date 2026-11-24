"""Historical evidence verification using a tiny synthetic frozen archive."""

import json
from pathlib import Path
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import review_behavioral_audit as audit  # noqa: E402


@pytest.fixture
def archive(tmp_path):
    evidence = tmp_path / "evidence"
    folder = evidence / "benchmark/run"
    folder.mkdir(parents=True)
    snapshot = tmp_path / "snapshot"
    source_files = {
        "evals/cases/triggers.json": b"[]",
        "evals/cases/scientific.json": b"[]",
        "evals/rubrics/scientific-review.md": b"synthetic rubric",
        "scripts/run_agent_evals.py": b"synthetic source; never executed",
    }
    for name, body in source_files.items():
        p = snapshot / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
    skill = snapshot / ".agents/skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(b"Synthetic guidance")
    original = tmp_path / "source.zip"
    with zipfile.ZipFile(original, "w") as z:
        z.comment = b"1" * 40
        z.writestr("README.md", "Synthetic fixture only")
    criteria = [
        {
            "id": "case",
            "skill": "example",
            "input": "Question",
            "criteria": ["Supported statement"],
            "critical_failure": ["Fabricate evidence"],
        }
    ]
    (evidence / "frozen-review-criteria.json").write_text(json.dumps(criteria))
    (evidence / "behavioral-review.txt").write_bytes(b"Synthetic review")
    provenance = {
        "original_revision": "1" * 40,
        "criteria_sha256": audit.sha((evidence / "frozen-review-criteria.json").read_bytes()),
        "source_archive_sha256": audit.sha(original.read_bytes()),
        "custom_manifest_sha256": audit.sha(source_files["evals/cases/scientific.json"]),
        "script_sha256": "2" * 64,
    }
    (evidence / "fixture-provenance.json").write_text(json.dumps(provenance))
    rows = []
    for number, mode in enumerate(("baseline", "skills"), 1):
        path = folder / f"attempt-{number:03d}"
        path.mkdir()
        (path / "prompt.txt").write_bytes(b"Question")
        (path / "response.txt").write_bytes(b"Supported statement.")
        (path / "stderr.txt").write_bytes(b"")
        events = [
            {"type": "thread.started", "thread_id": f"thread-{number}"},
            {"type": "turn.started"},
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Supported statement."},
            },
            {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]
        (path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
        rows.append(
            {
                "id": "case",
                "mode": mode,
                "artifact_dir": path.name,
                "artifacts": {p.name: audit.sha(p.read_bytes()) for p in path.iterdir()},
                "prompt_sha256": audit.sha(b"Question"),
                "command": ["codex", "--cd", "C:/synthetic/workspace"],
                "status": "COMPLETED",
                "exit_status": 0,
                "observed_skill_reads": [],
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "evaluation_status": "NOT_RUN",
                "activation_status": "UNOBSERVABLE",
                "started_at": "2026-11-24T00:00:00+00:00",
                "ended_at": "2026-11-24T00:00:01+00:00",
            }
        )
    report = {
        "run_id": "synthetic",
        "input_hashes": {k: audit.sha(v) for k, v in source_files.items()},
        "skill_hashes": {".agents/skills/example/SKILL.md": audit.sha(skill.read_bytes())},
        "results": rows,
        "requested_model": "synthetic-model",
        "resolved_model": None,
    }
    report_path = folder / "report.json"
    report_path.write_text(json.dumps(report))
    judgments = {
        "turns": {"case": {"baseline": ["Supported statement"], "skills": ["Supported statement"]}},
        "reviewer": {"identity": "synthetic fixture", "independent": False},
        "provenance": {"synthetic": True},
        "supplied_preliminary_adjudication": {"synthetic": True},
    }
    return evidence, snapshot, original, judgments, report_path


def test_original_artifacts_immutable_and_export_has_no_runtime_paths(archive):
    evidence, snapshot, original, judgments, _ = archive
    before = {p: p.read_bytes() for p in evidence.rglob("*") if p.is_file()}
    result = audit.review(evidence, snapshot, original, judgments)
    assert result["evidence_integrity"]["turn_artifacts_verified"] == 8
    assert all(p.read_bytes() == body for p, body in before.items())
    assert "C:/synthetic" not in json.dumps(result) and '"command"' not in json.dumps(result)
    assert (
        result["evidence_integrity"]["unattributed_script_status"] == "UNVERIFIED_FILE_NOT_LOCATED"
    )


@pytest.mark.parametrize("failure", ["response", "criteria", "snapshot", "malformed-trace"])
def test_tampered_or_malformed_original_evidence_rejected(archive, failure):
    evidence, snapshot, original, judgments, report_path = archive
    if failure == "response":
        (report_path.parent / "attempt-001/response.txt").write_bytes(b"modified")
    elif failure == "criteria":
        (evidence / "frozen-review-criteria.json").write_bytes(b"[]")
    elif failure == "snapshot":
        (snapshot / ".agents/skills/example/SKILL.md").write_bytes(b"changed")
    else:
        path = report_path.parent / "attempt-001/events.jsonl"
        path.write_bytes(b"malformed\n")
        report = json.loads(report_path.read_bytes())
        report["results"][0]["artifacts"]["events.jsonl"] = audit.sha(path.read_bytes())
        report_path.write_text(json.dumps(report))
    with pytest.raises(ValueError):
        audit.review(evidence, snapshot, original, judgments)
