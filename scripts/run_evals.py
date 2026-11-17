#!/usr/bin/env python3
"""Execute scientific regression cases; never score unexecuted agent prompts as passes."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def classify_junit(path: Path, returncode: int) -> tuple[str, dict]:
    """A successful runner with no actual test cases is not passing evidence."""
    counts = {"tests": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    if not path.is_file():
        return "FAIL", counts
    try:
        cases = list(ET.parse(path).getroot().iter("testcase"))
    except ET.ParseError:
        return "FAIL", counts
    counts["tests"] = len(cases)
    for case in cases:
        if case.find("failure") is not None:
            counts["failed"] += 1
        elif case.find("error") is not None:
            counts["errors"] += 1
        elif case.find("skipped") is not None:
            counts["skipped"] += 1
        else:
            counts["passed"] += 1
    if returncode != 0 or counts["failed"] or counts["errors"] or not cases:
        return "FAIL", counts
    if counts["skipped"]:
        return "BLOCKED", counts
    return "PASS", counts


def run_case(case: dict, evidence_dir: Path, root: Path = ROOT) -> dict:
    result = {"id": case["id"], "track": case["track"], "status": "NOT_RUN"}
    if case["track"] == "agent":
        result["reason"] = "No agent runner/model configured; scenario and rubric only."
        return result
    junit = evidence_dir / f"{case['id']}.xml"
    log = evidence_dir / f"{case['id']}.log"
    command = [sys.executable, "-m", "pytest", "-q", *case["test_nodes"], f"--junitxml={junit}"]
    result["command"] = command
    result["started_at"] = datetime.now(timezone.utc).isoformat()
    env = os.environ.copy()
    env["XDG_CACHE_HOME"] = str(evidence_dir / "cache")
    try:
        completed = subprocess.run(
            command, cwd=root, capture_output=True, text=True, timeout=120, env=env
        )
    except subprocess.TimeoutExpired as error:
        log.write_text(f"Timed out after 120 seconds: {error}\n")
        result.update(status="BLOCKED", reason="Timeout; checks incomplete", exit_status=None)
    else:
        log.write_text(completed.stdout + completed.stderr)
        status, counts = classify_junit(junit, completed.returncode)
        result.update(status=status, counts=counts, exit_status=completed.returncode)
    result["ended_at"] = datetime.now(timezone.utc).isoformat()
    result["evidence"] = [
        str(path.relative_to(evidence_dir.parent)) for path in (log, junit) if path.exists()
    ]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("evals/reports/latest.json"))
    args = parser.parse_args()
    manifest = ROOT / "evals/cases/scientific.json"
    cases = json.loads(manifest.read_text())
    run_id = "eval-" + uuid.uuid4().hex
    output = args.output.resolve()
    evidence_dir = output.parent / run_id
    evidence_dir.mkdir(parents=True, exist_ok=False)
    results = [run_case(case, evidence_dir) for case in cases]
    report = {
        "run_id": run_id,
        "python": sys.version,
        "pytest": importlib.metadata.version("pytest"),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "source_hashes": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ROOT / "tests/test_science.py", ROOT / "src/bioskills/science.py")
            if path.is_file()
        },
        "results": results,
        "summary": dict(Counter(case["status"] for case in results)),
        "limitations": [
            "Tool-based checks exercise synthetic inputs, not general agent behavior.",
            "Agent scenario and trigger-selection performance is NOT_RUN.",
            "No clinical validation or independent human scientific review.",
        ],
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], sort_keys=True))
    return 1 if any(case["status"] in {"FAIL", "BLOCKED"} for case in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
