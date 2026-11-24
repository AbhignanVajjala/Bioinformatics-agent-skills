#!/usr/bin/env python3
"""Verify frozen local evidence and export a separate, provisional review.

Reads original artifacts without executing their contents or changing them.
Never exports raw commands, authentication state, home paths or thread IDs.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import zipfile

from agent_benchmark import decode_json
from run_agent_evals import actions_in_stream


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    if path.resolve() != path or not path.is_file():
        raise ValueError("Missing or linked evidence file")
    return path.read_bytes()


def excerpt(response, anchor):
    if not isinstance(anchor, str) or not anchor or anchor not in response:
        raise ValueError("Reviewer excerpt anchor is absent from the response")
    start = response.index(anchor)
    stop = response.find("\n", start)
    stop = min(len(response) if stop < 0 else stop, start + 450)
    return {"start": start, "end": stop, "quote": response[start:stop]}


def auxiliary_evidence(evidence, report_path, skills):
    results = []
    for section, paths in (
        ("benchmark", [report_path]),
        ("preflight", list((evidence / "preflight").glob("*/report.json"))),
        ("smoke", list((evidence / "smoke").glob("*/report.json"))),
    ):
        for path in paths:
            raw = read(path)
            report = decode_json(raw)
            verified = 0
            for step in report.get("preflight", []):
                for name, expected in step.get("artifacts", {}).items():
                    if (
                        not re.fullmatch(r"(?:version|isolation)\.(?:stdout|stderr)", name)
                        or sha(read(path.parent / name)) != expected
                    ):
                        raise ValueError("Original preflight artifact mismatch")
                    verified += 1
            if section != "benchmark":
                for row in report.get("results", []):
                    if not re.fullmatch(r"attempt-[0-9]+", row["artifact_dir"]):
                        raise ValueError("Invalid auxiliary attempt path")
                    folder = path.parent / row["artifact_dir"]
                    for name, expected in row["artifacts"].items():
                        if (
                            name not in {"prompt.txt", "response.txt", "events.jsonl", "stderr.txt"}
                            or sha(read(folder / name)) != expected
                        ):
                            raise ValueError("Original smoke artifact mismatch")
                        verified += 1
                    command = row["command"]
                    parsed = actions_in_stream(
                        folder / "events.jsonl",
                        folder / "response.txt",
                        command[command.index("--cd") + 1],
                        skills,
                        skills_enabled=row["mode"] == "skills",
                    )
                    if "problem" in parsed or row["exit_status"] != 0:
                        raise ValueError("Original smoke completion did not verify")
            results.append(
                {
                    "section": section,
                    "report_sha256": sha(raw),
                    "artifact_hashes_verified": verified,
                    "recorded_execution_summary": report.get("summary", {}),
                    "scientific_grading": "NOT_RUN",
                }
            )
    return results


def review(evidence, snapshot, archive, judgments):
    evidence, snapshot, archive = (path.resolve() for path in (evidence, snapshot, archive))
    report_paths = list((evidence / "benchmark").glob("*/report.json"))
    if len(report_paths) != 1:
        raise ValueError("Exactly one original benchmark report required")
    report_path = report_paths[0]
    raw = read(report_path)
    original = decode_json(raw)
    frozen_raw = read(evidence / "frozen-review-criteria.json")
    frozen = decode_json(frozen_raw)
    criteria = {case["id"]: case for case in frozen}
    if len(criteria) != len(frozen):
        raise ValueError("Duplicate frozen case")
    provenance_raw = read(evidence / "fixture-provenance.json")
    provenance = decode_json(provenance_raw)
    archive_raw = read(archive)
    if (
        sha(frozen_raw) != provenance["criteria_sha256"]
        or sha(archive_raw) != provenance["source_archive_sha256"]
    ):
        raise ValueError("Frozen criteria/source archive checksum mismatch")
    for name, expected in original["input_hashes"].items():
        if (
            name
            not in {
                "evals/cases/triggers.json",
                "evals/cases/scientific.json",
                "evals/rubrics/scientific-review.md",
                "scripts/run_agent_evals.py",
            }
            or sha(read(snapshot / name)) != expected
        ):
            raise ValueError("Original input checksum mismatch")
    if (
        original["input_hashes"]["evals/cases/scientific.json"]
        != provenance["custom_manifest_sha256"]
    ):
        raise ValueError("Custom manifest provenance mismatch")
    skills = {
        p.relative_to(snapshot): read(p)
        for p in sorted((snapshot / ".agents/skills").rglob("*.md"))
    }
    if original["skill_hashes"] != {p.as_posix(): sha(body) for p, body in skills.items()}:
        raise ValueError("Preserved skill snapshot checksum mismatch")
    with zipfile.ZipFile(archive) as source:
        if source.comment.decode("ascii") != provenance["original_revision"]:
            raise ValueError("Source archive revision comment mismatch")

    turns, seen, threads, conditions = [], set(), set(), Counter()
    checked = 0
    for row in original["results"]:
        key = (row["id"], row["mode"])
        if key in seen or row["mode"] not in {"baseline", "skills"}:
            raise ValueError("Duplicate/invalid condition")
        seen.add(key)
        case = criteria[row["id"]]
        attempt = row["artifact_dir"]
        if not re.fullmatch(r"attempt-[0-9]+", attempt):
            raise ValueError("Unsafe attempt locator")
        folder = report_path.parent / attempt
        artifacts = {}
        if set(row["artifacts"]) != {"prompt.txt", "response.txt", "events.jsonl", "stderr.txt"}:
            raise ValueError("Unexpected original artifact inventory")
        for name, expected in row["artifacts"].items():
            body = read(folder / name)
            if sha(body) != expected:
                raise ValueError("Original turn artifact checksum mismatch")
            artifacts[name] = expected
            checked += 1
        prompt = read(folder / "prompt.txt").decode("utf-8")
        response = read(folder / "response.txt").decode("utf-8")
        if row["prompt_sha256"] != artifacts["prompt.txt"] or case["input"] not in prompt:
            raise ValueError("Frozen/executed prompt mismatch")
        command = row["command"]
        workspace = command[command.index("--cd") + 1]
        parsed = actions_in_stream(
            folder / "events.jsonl",
            folder / "response.txt",
            workspace,
            skills,
            skills_enabled=row["mode"] == "skills",
        )
        if (
            row["status"] != "COMPLETED"
            or row["exit_status"] != 0
            or "problem" in parsed
            or parsed["thread_id"] in threads
            or parsed["observed_skill_reads"] != row["observed_skill_reads"]
            or parsed["usage"] != row["usage"]
        ):
            raise ValueError("Frozen execution evidence did not replay consistently")
        threads.add(parsed["thread_id"])
        grading = judgments["turns"][row["id"]][row["mode"]]
        if len(grading) != len(case["criteria"]):
            raise ValueError("Every frozen criterion requires a separate judgment")
        scored = []
        for number, (criterion, judgment) in enumerate(
            zip(case["criteria"], grading, strict=True), 1
        ):
            passed = isinstance(judgment, str)
            if not passed and not (isinstance(judgment, dict) and judgment.get("missing_reason")):
                raise ValueError("Missing criterion requires an explicit reason")
            scored.append(
                {
                    "criterion_id": f"c{number}",
                    "criterion": criterion,
                    "status": "PASS" if passed else "MISSING",
                    "evidence": excerpt(response, judgment) if passed else None,
                    "reason": "Quoted response satisfies this scoped frozen criterion."
                    if passed
                    else judgment["missing_reason"],
                    "absence_review_scope": None if passed else "entire response",
                }
            )
        decision = "FULL_PASS" if all(x["status"] == "PASS" for x in scored) else "INCOMPLETE"
        conditions[(row["mode"], decision)] += 1
        turns.append(
            {
                "case_id": row["id"],
                "condition": row["mode"],
                "expected_skill": case["skill"],
                "frozen_input": case["input"],
                "executed_prompt": prompt,
                "response": response,
                "artifact_locator": attempt,
                "artifact_sha256": artifacts,
                "execution_status": row["status"],
                "original_evaluation_status": row["evaluation_status"],
                "activation_status": row["activation_status"],
                "availability": "AVAILABLE" if row["mode"] == "skills" else "UNAVAILABLE",
                "observed_skill_reads": parsed["observed_skill_reads"],
                "target_read_observed": any(
                    x["skill"] == case["skill"] for x in parsed["observed_skill_reads"]
                ),
                "instruction_adherence": "PROVISIONAL_REVIEW_ONLY",
                "criteria": scored,
                "critical_failures": [
                    {
                        "criterion": text,
                        "status": "NOT_OBSERVED",
                        "basis": "Entire recorded response reviewed against unchanged frozen criterion",
                    }
                    for text in case["critical_failure"]
                ],
                "decision": decision,
                "reviewer": judgments["reviewer"],
                "efficiency": {
                    "words": len(response.split()),
                    "characters": len(response),
                    "elapsed_seconds": (
                        datetime.fromisoformat(row["ended_at"])
                        - datetime.fromisoformat(row["started_at"])
                    ).total_seconds(),
                    "usage": row["usage"],
                },
            }
        )
    expected = {(case, mode) for case in criteria for mode in ("baseline", "skills")}
    if seen != expected or set(judgments["turns"]) != set(criteria):
        raise ValueError("Frozen paired review is incomplete")
    for case in criteria:
        pair = [x for x in turns if x["case_id"] == case]
        if pair[0]["artifact_sha256"]["prompt.txt"] != pair[1]["artifact_sha256"]["prompt.txt"]:
            raise ValueError("Paired prompts differ")
    return {
        "schema_version": 1,
        "original_revision": provenance["original_revision"],
        "original_run_id": original["run_id"],
        "evidence_integrity": {
            "status": "VERIFIED_AVAILABLE_ARTIFACTS",
            "turn_artifacts_verified": checked,
            "report_sha256": sha(raw),
            "criteria_sha256": sha(frozen_raw),
            "fixture_provenance_sha256": sha(provenance_raw),
            "behavioral_review_sha256": sha(read(evidence / "behavioral-review.txt")),
            "source_archive_sha256": sha(archive_raw),
            "input_sha256": original["input_hashes"],
            "skill_sha256": original["skill_hashes"],
            "unattributed_script_sha256": provenance["script_sha256"],
            "unattributed_script_status": "UNVERIFIED_FILE_NOT_LOCATED",
            "auxiliary_evidence": auxiliary_evidence(evidence, report_path, skills),
        },
        "configuration": {
            "requested_model": original["requested_model"],
            "resolved_model": original["resolved_model"],
            "reasoning_effort": None,
            "configuration_verification": "RESOLVED_MODEL_AND_EFFORT_UNVERIFIED",
            "historical_environment": "Windows MXC; Python 3.14.8; Codex CLI 0.168.0; ChatGPT",
        },
        "review_provenance": judgments["provenance"],
        "supplied_preliminary_adjudication": judgments["supplied_preliminary_adjudication"],
        "provisional_review_summary": {
            mode: {state: conditions[(mode, state)] for state in ("FULL_PASS", "INCOMPLETE")}
            for mode in ("baseline", "skills")
        },
        "turns": turns,
        "limitations": [
            "Unblinded AI-assisted review; independent human methodological validation pending",
            "New criterion-level reconstruction is separate from supplied original aggregate scores",
            "One sample per condition/case; no causal effectiveness or general performance inference",
            "File access does not establish activation or instruction following",
            "Original scientific evaluation status remains NOT_RUN",
            "Synthetic executable interoperability is not autonomous agent orchestration",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--judgments", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output; preserve existing review evidence")
    result = review(
        args.evidence, args.snapshot, args.source_archive, decode_json(args.judgments.read_bytes())
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["provisional_review_summary"]))


if __name__ == "__main__":
    main()
