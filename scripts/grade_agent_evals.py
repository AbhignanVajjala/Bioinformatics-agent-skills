#!/usr/bin/env python3
"""Export blinded responses, validate explicit reviewer grades, then unblind.

No model is called. Quote validity is checked deterministically; scientific
judgments remain provisional reviewer decisions, not keyword classifications.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from agent_benchmark import blinded_export, decode_json, grade_record, load_definition
from run_agent_evals import ROOT, actions_in_stream, digest, load_inputs


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    export = actions.add_parser("blind")
    export.add_argument("--report", type=Path, required=True)
    export.add_argument("--benchmark", type=Path, required=True)
    export.add_argument("--reviewer-dir", type=Path, required=True)
    export.add_argument("--private-map", type=Path, required=True)
    grade = actions.add_parser("grade")
    grade.add_argument("--packet", type=Path, required=True)
    grade.add_argument("--judgments", type=Path, required=True)
    grade.add_argument("--output", type=Path, required=True)
    reveal = actions.add_parser("unblind")
    reveal.add_argument("--grades", type=Path, required=True)
    reveal.add_argument("--private-map", type=Path, required=True)
    reveal.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "blind":
            _, skills, _ = load_inputs(ROOT)
            definition, source_hash = load_definition(
                args.benchmark, {p.parent.name for p in skills if p.name == "SKILL.md"}
            )
            report = decode_json(args.report.read_bytes())
            case_map = {case["id"]: case for case in definition["cases"]}
            if report["input_hashes"].get("benchmark_definition") != source_hash or report[
                "skill_hashes"
            ] != {p.as_posix(): digest(body) for p, body in skills.items()}:
                raise ValueError("Benchmark or skill snapshot changed; use the exact run snapshot")
            for row in report["results"]:
                if row["status"] != "COMPLETED":
                    continue
                directory = row["artifact_dir"]
                if not re.fullmatch(r"attempt-[0-9]+", directory):
                    raise ValueError("Unsafe evidence directory")
                folder = args.report.resolve().parent / directory
                if folder.resolve() != folder or row["exit_status"] != 0:
                    raise ValueError("Completed execution did not verify")
                for name in ("prompt.txt", "response.txt", "events.jsonl", "stderr.txt"):
                    file = folder / name
                    if (
                        file.resolve() != file
                        or digest(file.read_bytes()) != row["artifacts"][name]
                    ):
                        raise ValueError("Evidence hash mismatch")
                if (folder / "prompt.txt").read_bytes() != case_map[row["id"]]["input"].encode(
                    "utf-8"
                ) or row["prompt_sha256"] != row["artifacts"]["prompt.txt"]:
                    raise ValueError("Executed prompt differs from the frozen versioned case")
                command = row["command"]
                parsed = actions_in_stream(
                    folder / "events.jsonl",
                    folder / "response.txt",
                    command[command.index("--cd") + 1],
                    skills,
                    skills_enabled=row["mode"] == "skills",
                )
                if "problem" in parsed or parsed["thread_id"] != row["thread_id"]:
                    raise ValueError("Trace does not establish completed execution")
            count = blinded_export(args.report, definition, args.reviewer_dir, args.private_map)
            print(f"Exported {count} completed answers; condition allocation remains separate")
        elif args.action == "grade":
            packet_bytes = args.packet.read_bytes()
            packet = decode_json(packet_bytes)
            raw_judgments = args.judgments.read_bytes()
            judgments = decode_json(raw_judgments)
            by_id = {item["blind_id"]: item for item in packet["responses"]}
            reviews = judgments["responses"]
            if len(reviews) != len(by_id) or {x["blind_id"] for x in reviews} != set(by_id):
                raise ValueError("Every blinded answer requires one complete review")
            graded = [grade_record(by_id[item["blind_id"]], item) for item in reviews]
            write_new(
                args.output,
                {
                    "schema_version": 1,
                    "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
                    "judgments_sha256": hashlib.sha256(raw_judgments).hexdigest(),
                    "grading_complete": all(row["verdict"] != "BLOCKED" for row in graded),
                    "provisional": True,
                    "independent_human_validation": "PENDING",
                    "responses": graded,
                },
            )
            print("Reviewer decisions validated; no condition labels were loaded")
        else:
            grades = decode_json(args.grades.read_bytes())
            allocation = decode_json(args.private_map.read_bytes())
            if (
                not grades["grading_complete"]
                or grades["packet_sha256"] != allocation["packet_sha256"]
            ):
                raise ValueError("Complete frozen grading must precede unblinding")
            mapping = allocation["allocation"]
            if {x["blind_id"] for x in grades["responses"]} != set(mapping):
                raise ValueError("Blinded allocation does not match frozen grading")
            rows = [{**row, **mapping[row["blind_id"]]} for row in grades["responses"]]
            summary = {}
            for mode in ("baseline", "skills"):
                summary[mode] = dict(Counter(row["verdict"] for row in rows if row["mode"] == mode))
            critical = sum(
                item["status"] == "OBSERVED"
                for row in rows
                for item in row["judgment"]["critical_failures"]
            )
            write_new(
                args.output,
                {
                    "schema_version": 1,
                    "source_report_sha256": allocation["source_report_sha256"],
                    "frozen_grades_sha256": digest(args.grades.read_bytes()),
                    "responses": rows,
                    "scientific_summary": summary,
                    "critical_failures_observed": critical,
                    "execution_summary": allocation["execution_summary"],
                    "attempt_summary": allocation["attempt_summary"],
                    "resource_usage": allocation["resource_usage"],
                    "provisional": True,
                    "independent_human_validation": "PENDING",
                    "limitations": [
                        "Descriptive paired/repeated observations, not established causal effectiveness",
                        "Availability and reads do not establish activation or adherence",
                        "Content may reveal condition despite metadata blinding",
                    ],
                },
            )
            print(json.dumps({"scientific_summary": summary, "critical_failures": critical}))
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        parser.error("Invalid or incompatible benchmark, artifact, grading or output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
