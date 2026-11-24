"""Offline benchmark contracts, pairing and evidence-based grading utilities.

These functions validate records; they do not infer scientific truth from text.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import random
import re
import uuid


DIMENSIONS = (
    "trigger_appropriateness",
    "instruction_adherence",
    "scientific_correctness",
    "methodological_completeness",
    "evidence_grounding",
)
TRIGGERS = {"legitimate", "out_of_scope", "adversarial", "invalid_in_scope"}


def decode_json(raw):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key in evaluation evidence")
            result[key] = value
        return result

    def finite(value):
        raise ValueError("Nonfinite JSON constant in evaluation evidence")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=finite)


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def load_definition(path, available_skills):
    raw = path.read_bytes()
    definition = decode_json(raw)
    if not isinstance(definition, dict) or not isinstance(definition.get("cases"), list):
        raise ValueError("A benchmark object with a case list is required")
    if definition.get("schema_version") != 2 or not re.fullmatch(
        r"[a-z0-9][a-z0-9-]+", definition.get("benchmark_id", "")
    ):
        raise ValueError("Unsupported benchmark definition")
    seen, groups, coverage = set(), {}, Counter()
    for case in definition["cases"]:
        case_id = case["id"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]+", case_id) or case_id in seen:
            raise ValueError("Invalid/duplicate benchmark case ID")
        seen.add(case_id)
        if (
            case["skill"] not in available_skills
            or case["trigger_class"] not in TRIGGERS
            or case["split"] not in {"development", "heldout"}
            or type(case["expected_relevance"]) is not bool
            or case["expected_relevance"] != (case["trigger_class"] != "out_of_scope")
            or not isinstance(case["input"], str)
            or not case["input"].strip()
        ):
            raise ValueError("Invalid trigger, split, prompt or skill contract")
        group = case["source_group"]
        if (
            not isinstance(group, str)
            or not group
            or groups.get(group, case["split"]) != case["split"]
        ):
            raise ValueError("A source group cannot cross development and held-out splits")
        groups[group] = case["split"]
        identifiers = set()
        for criterion in case["criteria"]:
            if (
                criterion["id"] in identifiers
                or not criterion["text"].strip()
                or criterion["dimension"] not in DIMENSIONS
            ):
                raise ValueError("Invalid grading criterion")
            identifiers.add(criterion["id"])
        if not identifiers or not case["critical_failures"]:
            raise ValueError("Explicit criteria and critical failure rules required")
        if case["split"] == "development":
            coverage[(case["skill"], case["trigger_class"])] += 1
    if len(available_skills) != 17 or any(
        coverage[(skill, kind)] < 1 for skill in available_skills for kind in TRIGGERS
    ):
        raise ValueError(
            "Development coverage must include all four trigger classes for all 17 skills"
        )
    return definition, hashlib.sha256(raw).hexdigest()


def paired_plan(cases, modes, trials=1, seed=0):
    if type(trials) is not int or not 1 <= trials <= 100 or type(seed) is not int:
        raise ValueError("Trials must be 1–100 and seed must be an integer")
    rng = random.Random(seed)
    rows = []
    for trial in range(1, trials + 1):
        for case_id, (track, prompt) in cases.items():
            order = list(modes)
            if trials > 1:
                # Random starting condition, then reverse within each case across repeats.
                first = random.Random(f"{seed}:{case_id}").randrange(2)
                if (first + trial) % 2:
                    order.reverse()
            elif seed:
                rng.shuffle(order)
            for mode in order:
                rows.append(
                    {
                        "id": case_id,
                        "track": track,
                        "mode": mode,
                        "trial": trial,
                        "status": "NOT_RUN",
                        "evaluation_status": "NOT_RUN",
                        "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
                    }
                )
    return rows


def attempt_records(rows):
    return [
        attempt
        for row in rows
        for attempt in [row, *row.get("previous_attempts", [])]
        if attempt.get("artifact_dir")
    ]


def resource_summary(attempts):
    counters, known, unknown = Counter(), 0, 0
    fields = {
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "reasoning_output_tokens",
    }
    for attempt in attempts:
        usage = attempt.get("usage")
        if (
            not isinstance(usage, dict)
            or not fields.intersection(usage)
            or any(
                type(value) is not int or value < 0 for key, value in usage.items() if key in fields
            )
        ):
            unknown += 1
            continue
        known += 1
        counters.update({key: value for key, value in usage.items() if key in fields})
    return {
        "observed_counters": dict(counters),
        "attempts_with_usage": known,
        "attempts_without_verified_usage": unknown,
        "partial_accounting": bool(unknown),
    }


def verify_quote(response, evidence):
    start, end, quote = (evidence.get(key) for key in ("start", "end", "quote"))
    if (
        type(start) is not int
        or type(end) is not int
        or not 0 <= start < end <= len(response)
        or not isinstance(quote, str)
        or response[start:end] != quote
    ):
        raise ValueError("Supporting quote/offset does not match the immutable response")


def grade_record(packet, judgment):
    """Check explicit reviewer decisions and evidence; never auto-classify prose."""
    response = packet["response"]
    if not response.strip() or not judgment.get("reviewer") or not judgment.get("reason"):
        raise ValueError("Response and adjudication provenance required")
    expected = {x["id"]: x for x in packet["criteria"]}
    decisions = judgment["criteria"]
    if len(decisions) != len(expected) or {x["id"] for x in decisions} != set(expected):
        raise ValueError("Exactly one decision per criterion required")
    dimensions = {}
    for item in decisions:
        if item["status"] not in {"PASS", "MISSING", "FAIL", "UNRESOLVED"} or not item.get(
            "reason"
        ):
            raise ValueError("Explicit criterion status/reason required")
        evidence = item.get("evidence", [])
        if item["status"] in {"PASS", "FAIL"} and not evidence:
            raise ValueError("Supported or contradicted criterion requires quoted evidence")
        for quote in evidence:
            verify_quote(response, quote)
        if item["status"] == "MISSING" and item.get("review_scope") != "entire_response":
            raise ValueError("Missing evidence requires an explicit whole-response review")
        dimensions.setdefault(expected[item["id"]]["dimension"], []).append(item["status"])
    critical = judgment["critical_failures"]
    if len(critical) != len(packet["critical_failures"]) or {item["id"] for item in critical} != {
        item["id"] for item in packet["critical_failures"]
    }:
        raise ValueError("Every frozen critical failure needs an adjudication")
    for item in critical:
        if item["status"] not in {"NOT_OBSERVED", "OBSERVED", "UNRESOLVED"} or not item.get(
            "reason"
        ):
            raise ValueError("Invalid critical failure decision")
        if item["status"] == "OBSERVED" and not item.get("evidence"):
            raise ValueError("Observed critical failure requires response evidence")
        for quote in item.get("evidence", []):
            verify_quote(response, quote)
    statuses = [x["status"] for x in decisions]
    critical_states = [x["status"] for x in critical]
    verdict = (
        "FAIL"
        if "FAIL" in statuses or "OBSERVED" in critical_states
        else "BLOCKED"
        if "UNRESOLVED" in statuses + critical_states
        else "INCOMPLETE"
        if "MISSING" in statuses
        else "PASS"
    )
    return {
        "blind_id": packet["blind_id"],
        "verdict": verdict,
        "dimensions": {
            dimension: next((s for s in ("FAIL", "UNRESOLVED", "MISSING") if s in values), "PASS")
            for dimension, values in dimensions.items()
        },
        "judgment": judgment,
        "response_sha256": hashlib.sha256(response.encode()).hexdigest(),
        "provisional": True,
        "independent_human_validation": "PENDING",
    }


def blinded_export(report_path, definitions, reviewer_dir, private_map):
    """Export completed answers without condition/read/usage/runtime metadata.

    Content itself can reveal skill use. Metadata blinding is not a guarantee of
    successful reviewer blinding, and public development cases are not held out.
    """
    report_path, reviewer_dir, private_map = (
        p.resolve() for p in (report_path, reviewer_dir, private_map)
    )
    if reviewer_dir.exists() or private_map.exists() or private_map.is_relative_to(reviewer_dir):
        raise ValueError("Use a new reviewer directory and a separate private allocation file")
    rows, allocation = [], {}
    case_map = {case["id"]: case for case in definitions["cases"]}
    for turn in report_path.parent.iterdir():
        if turn.is_symlink():
            raise ValueError("Linked evidence is unsupported")
    report_bytes = report_path.read_bytes()
    report = decode_json(report_bytes)
    for row in report["results"]:
        if row["status"] != "COMPLETED":
            continue
        if not re.fullmatch(r"attempt-[0-9]+", row["artifact_dir"]):
            raise ValueError("Unsafe attempt path")
        folder = report_path.parent / row["artifact_dir"]
        if folder.resolve() != folder:
            raise ValueError("Linked evidence is unsupported")
        texts = {}
        for name in ("prompt.txt", "response.txt"):
            file = folder / name
            if file.resolve() != file:
                raise ValueError("Linked response is unsupported")
            raw = file.read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["artifacts"][name]:
                raise ValueError("Export artifact hash mismatch")
            texts[name] = raw.decode("utf-8")
        case = case_map[row["id"]]
        blind_id = uuid.uuid4().hex
        rows.append(
            {
                "blind_id": blind_id,
                "prompt": texts["prompt.txt"],
                "response": texts["response.txt"],
                "criteria": case["criteria"],
                "critical_failures": case["critical_failures"],
            }
        )
        allocation[blind_id] = {key: row[key] for key in ("id", "mode", "trial", "artifact_dir")}
        allocation[blind_id].update(
            {
                "skill_availability": "AVAILABLE" if row["mode"] == "skills" else "UNAVAILABLE",
                "expected_skill": case["skill"],
                "observed_target_read": any(
                    r["skill"] == case["skill"] for r in row.get("observed_skill_reads", [])
                ),
                "activation_status": row.get("activation_status", "UNOBSERVABLE"),
                "execution_status": row["status"],
                "usage": row.get("usage"),
                "started_at": row.get("started_at"),
                "ended_at": row.get("ended_at"),
            }
        )
    if not rows:
        raise ValueError("No completed responses to export")
    random.SystemRandom().shuffle(rows)
    reviewer_dir.mkdir(parents=True)
    private_map.parent.mkdir(parents=True, exist_ok=True)
    packet = {
        "schema_version": 1,
        "blinding": "CONDITION_METADATA_HIDDEN_CONTENT_MAY_REVEAL",
        "responses": rows,
    }
    (reviewer_dir / "responses.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    private_map.write_text(
        json.dumps(
            {
                "source_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
                "packet_sha256": hashlib.sha256(
                    (reviewer_dir / "responses.json").read_bytes()
                ).hexdigest(),
                "allocation": allocation,
                "execution_summary": dict(Counter(row["status"] for row in report["results"])),
                "attempt_summary": report.get("attempt_summary", {}),
                "resource_usage": report.get("resource_usage", {}),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return len(rows)
