"""Evidence/grade/resume contracts, using synthetic events and no model calls."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_benchmark as benchmark  # noqa: E402
import grade_agent_evals as grader  # noqa: E402
import run_agent_evals as runner  # noqa: E402


def definition():
    return json.loads((ROOT / "evals/benchmarks/phase9-v1.json").read_bytes())


def available():
    return {p.parent.name for p in (ROOT / ".agents/skills").glob("*/SKILL.md")}


def test_versioned_coverage_and_in_scope_safeguards():
    result, _ = benchmark.load_definition(ROOT / "evals/benchmarks/phase9-v1.json", available())
    development = [c for c in result["cases"] if c["split"] == "development"]
    assert len(development) == 68 and len(result["cases"]) == 78
    for skill in available():
        rows = [c for c in development if c["skill"] == skill]
        assert {r["trigger_class"] for r in rows} == benchmark.TRIGGERS
        assert all(r["expected_relevance"] for r in rows if r["trigger_class"] != "out_of_scope")
    assert len({c["input"] for c in result["cases"]}) == 78
    assert all(c["evaluation_status"] == "NOT_RUN" for c in result["cases"])


@pytest.mark.parametrize(
    "corruption", ["duplicate", "split-leak", "coverage", "invalid-negative", "empty"]
)
def test_malformed_definitions_rejected(tmp_path, corruption):
    data = definition()
    if corruption == "duplicate":
        data["cases"][1]["id"] = data["cases"][0]["id"]
    elif corruption == "split-leak":
        data["cases"][-1]["source_group"] = data["cases"][0]["source_group"]
    elif corruption == "coverage":
        data["cases"].pop(0)
    elif corruption == "invalid-negative":
        data["cases"][3]["expected_relevance"] = False
    else:
        data["cases"][0]["input"] = " "
    file = tmp_path / "definition.json"
    file.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        benchmark.load_definition(file, available())


def test_paired_repeats_are_reproducible_and_counterbalance_conditions():
    cases = {"x": ("trigger", b"same question"), "y": ("trigger", b"other question")}
    rows = benchmark.paired_plan(cases, ("baseline", "skills"), 4, 42)
    assert rows == benchmark.paired_plan(cases, ("baseline", "skills"), 4, 42)
    for case in cases:
        groups = [r for r in rows if r["id"] == case]
        assert len({r["prompt_sha256"] for r in groups}) == 1
        assert [r["mode"] for r in groups][::2].count("baseline") == 2
        assert len({(r["trial"], r["mode"]) for r in groups}) == 8


def fake_runtime(monkeypatch, tmp_path, incomplete=False):
    binary = tmp_path / "codex.exe"
    binary.write_bytes(b"synthetic executable identity; never launched")
    auth = tmp_path / "dedicated-auth"
    auth.mkdir()
    monkeypatch.setattr(runner.shutil, "which", lambda _: str(binary))
    monkeypatch.setattr(runner.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(runner, "preflight", lambda *args: ([], None))
    calls = []

    def invoke(command, cwd, env, stdout, stderr, timeout, prompt):
        calls.append((command, cwd, env, prompt, (cwd / ".agents/skills").is_dir()))
        assert b"HIDDEN_CRITERION" not in prompt
        assert not (cwd / "evals").exists() and not (cwd / "AGENTS.md").exists()
        assert all(p.relative_to(cwd).parts[0] == ".agents" for p in cwd.rglob("*") if p.is_file())
        assert not any(
            arg in command
            for arg in ("--resume", "resume", "--dangerously-bypass-approvals-and-sandbox")
        )
        final = Path(command[command.index("--output-last-message") + 1])
        final.write_bytes(b"Synthetic response")
        rows = [
            {"type": "thread.started", "thread_id": f"fresh-{len(calls)}"},
            {"type": "turn.started"},
        ]
        partial = incomplete and len(calls) == 1
        if not partial:
            rows += [
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "Synthetic response"},
                },
                {"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 2}},
            ]
        stdout.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
        stderr.write_bytes(b"")
        return {
            "command": command,
            "exit_status": None if partial else 0,
            "interrupted": partial,
            "started_at": "2026-11-24T00:00:00+00:00",
            "ended_at": "2026-11-24T00:00:01+00:00",
        }

    monkeypatch.setattr(runner, "invoke", invoke)
    return binary, auth, calls


def start_interrupted(monkeypatch, tmp_path):
    binary, auth, calls = fake_runtime(monkeypatch, tmp_path, incomplete=True)
    assert (
        runner.main(
            [
                "--execute",
                "--case",
                "research-specification-positive-1",
                "--model",
                "fake-model",
                "--codex-home",
                str(auth),
                "--output-dir",
                str(tmp_path / "reports"),
            ]
        )
        == 1
    )
    report = next((tmp_path / "reports").glob("*/report.json"))
    return binary, auth, calls, report


def test_interrupt_preserves_partial_and_resume_uses_fresh_sessions(monkeypatch, tmp_path, capsys):
    _, auth, calls, path = start_interrupted(monkeypatch, tmp_path)
    initial_bytes = path.read_bytes()
    initial = json.loads(initial_bytes)
    assert [r["status"] for r in initial["results"]] == ["INCOMPLETE", "NOT_RUN"]
    preserved = {p: p.read_bytes() for p in (path.parent / "attempt-001").iterdir()}
    assert runner.main(["--resume", str(path), "--execute", "--codex-home", str(auth)]) == 0
    report = json.loads(path.read_bytes())
    assert report["summary"] == {"COMPLETED": 2}
    assert report["attempt_summary"] == {"COMPLETED": 2, "INCOMPLETE": 1}
    assert report["resource_usage"]["attempts_without_verified_usage"] == 1
    assert (
        path.parent / report["resume_history"][0]["checkpoint_file"]
    ).read_bytes() == initial_bytes
    assert report["results"][0]["previous_attempts"][0]["status"] == "INCOMPLETE"
    assert [r["artifact_dir"] for r in report["results"]] == ["attempt-002", "attempt-003"]
    assert all(p.read_bytes() == value for p, value in preserved.items())
    assert len({str(c[1]) for c in calls}) == 3
    assert all(r["evaluation_status"] == "NOT_RUN" for r in report["results"])
    assert '"event": "progress"' in capsys.readouterr().err
    complete_bytes = path.read_bytes()
    (path.parent / "attempt-001/response.txt").write_bytes(b"tampered prior partial evidence")
    with pytest.raises(SystemExit) as error:
        runner.main(["--resume", str(path), "--execute", "--codex-home", str(auth)])
    assert error.value.code == 2 and len(calls) == 3 and path.read_bytes() == complete_bytes


@pytest.mark.parametrize("drift", ["model", "source", "artifact", "executable", "selection"])
def test_resume_fails_before_runtime_on_incompatible_evidence(monkeypatch, tmp_path, drift):
    binary, auth, calls, path = start_interrupted(monkeypatch, tmp_path)
    before = path.read_bytes()
    args = ["--resume", str(path), "--execute", "--codex-home", str(auth)]
    if drift == "model":
        args += ["--model", "different"]
    elif drift == "selection":
        args += ["--case", "another-case"]
    elif drift == "artifact":
        (path.parent / "attempt-001/response.txt").write_bytes(b"tampered")
    elif drift == "executable":
        binary.write_bytes(b"different runtime")
    else:
        original = runner.load_inputs

        def changed(root):
            cases, skills, hashes = original(root)
            hashes["scripts/run_agent_evals.py"] = "changed"
            return cases, skills, hashes

        monkeypatch.setattr(runner, "load_inputs", changed)
    with pytest.raises(SystemExit) as error:
        runner.main(args)
    assert error.value.code == 2 and len(calls) == 1
    # Reject before adding resume history or replacing the report.
    assert path.read_bytes() == before


def test_versioned_execution_stages_only_skills_and_matches_requested_configuration(
    monkeypatch, tmp_path
):
    _, auth, calls = fake_runtime(monkeypatch, tmp_path)
    data = definition()
    data["cases"][0]["criteria"][0]["text"] = "HIDDEN_CRITERION"
    manifest = tmp_path / "cases.json"
    manifest.write_text(json.dumps(data))
    assert (
        runner.main(
            [
                "--execute",
                "--benchmark",
                str(manifest),
                "--case",
                data["cases"][0]["id"],
                "--model",
                "fake-model",
                "--reasoning-effort",
                "low",
                "--trials",
                "2",
                "--seed",
                "7",
                "--codex-home",
                str(auth),
                "--output-dir",
                str(tmp_path / "reports"),
            ]
        )
        == 0
    )
    assert len(calls) == 4 and len({c[3] for c in calls}) == 1
    assert sum(c[4] for c in calls) == 2
    for command, cwd, env, _, _ in calls:
        assert 'model_reasoning_effort="low"' in command
        assert (
            'approval_policy="never"' in command
            and "permissions.agent-eval.network.enabled=false" in command
        )
        assert not any("require_mxc" in arg for arg in command)
        if sys.platform == "win32":
            assert 'windows.sandbox="mxc"' in command
        assert "OPENAI_API_KEY" not in env
    r = json.loads(next((tmp_path / "reports").glob("*/report.json")).read_bytes())
    assert r["resolved_model"] is None and r["resolved_reasoning_effort"] is None


@pytest.mark.parametrize("event", [KeyboardInterrupt, subprocess.TimeoutExpired])
def test_child_is_terminated_and_partial_stream_kept(monkeypatch, tmp_path, event):
    class Process:
        returncode = None
        terminated = False

        def communicate(self, input=None, timeout=None):
            if not self.terminated:
                if event is KeyboardInterrupt:
                    raise KeyboardInterrupt
                raise subprocess.TimeoutExpired(["fake"], 1)
            return None, None

        def terminate(self):
            self.terminated = True
            self.returncode = -15

    child = Process()
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: child)
    stdout, stderr = tmp_path / "events", tmp_path / "stderr"
    result = runner.invoke(["fake"], tmp_path, {}, stdout, stderr, 1, b"hello")
    assert child.terminated and result["exit_status"] is None
    assert result["child_exit_status"] == -15 and stdout.exists() and stderr.exists()
    assert result["interrupted"] == (event is KeyboardInterrupt)


def packet_and_grade():
    packet = {
        "blind_id": "opaque",
        "response": "Source reports an association. Evidence for causation is absent.",
        "criteria": [
            {"id": "c1", "dimension": "scientific_correctness", "text": "Limit causality"}
        ],
        "critical_failures": [{"id": "k1", "text": "Claim causation established"}],
    }
    quote = {"start": 0, "end": 30, "quote": packet["response"][:30]}
    review = {
        "blind_id": "opaque",
        "reviewer": {"identity": "synthetic reviewer", "independent": False},
        "reason": "Explicit provisional synthetic judgment",
        "criteria": [
            {"id": "c1", "status": "PASS", "reason": "Evidence-limited", "evidence": [quote]}
        ],
        "critical_failures": [
            {"id": "k1", "status": "NOT_OBSERVED", "reason": "Entire response reviewed"}
        ],
    }
    return packet, review


@pytest.mark.parametrize(
    "failure",
    ["wrong-quote", "no-evidence", "missing-criterion", "missing-critical", "unknown-status"],
)
def test_grades_need_complete_criteria_and_real_response_evidence(failure):
    packet, review = packet_and_grade()
    if failure == "wrong-quote":
        review["criteria"][0]["evidence"][0]["quote"] = "fabricated quote"
    elif failure == "no-evidence":
        review["criteria"][0]["evidence"] = []
    elif failure == "missing-criterion":
        review["criteria"] = []
    elif failure == "missing-critical":
        review["critical_failures"] = []
    else:
        review["criteria"][0]["status"] = "SUCCESS"
    with pytest.raises(ValueError):
        benchmark.grade_record(packet, review)


def test_omission_and_critical_failure_are_separate_from_execution():
    packet, review = packet_and_grade()
    assert benchmark.grade_record(packet, review)["verdict"] == "PASS"
    review["criteria"][0].update(
        status="MISSING",
        evidence=[],
        review_scope="entire_response",
        reason="Required evidence absent",
    )
    assert benchmark.grade_record(packet, review)["verdict"] == "INCOMPLETE"
    review["critical_failures"][0].update(
        status="OBSERVED",
        evidence=[{"start": 0, "end": 6, "quote": "Source"}],
        reason="Synthetic contradictory judgment tests critical precedence",
    )
    assert benchmark.grade_record(packet, review)["verdict"] == "FAIL"


def test_historical_review_is_separate_and_criterion_evidence_is_exact():
    report = json.loads((ROOT / "evals/reports/behavioral-audit-2026-11-24.json").read_bytes())
    assert report["evidence_integrity"]["turn_artifacts_verified"] == 160
    assert report["provisional_review_summary"] == {
        "baseline": {"FULL_PASS": 16, "INCOMPLETE": 4},
        "skills": {"FULL_PASS": 18, "INCOMPLETE": 2},
    }
    assert len(report["turns"]) == 40
    assert all(
        row["original_evaluation_status"] == "NOT_RUN"
        and row["activation_status"] == "UNOBSERVABLE"
        for row in report["turns"]
    )
    for row in report["turns"]:
        assert runner.digest(row["response"].encode()) == row["artifact_sha256"]["response.txt"]
        for criterion in row["criteria"]:
            if criterion["evidence"]:
                benchmark.verify_quote(row["response"], criterion["evidence"])
    assert (
        sum(x["target_read_observed"] for x in report["turns"] if x["condition"] == "skills") == 19
    )
    assert sum(len(x["observed_skill_reads"]) for x in report["turns"]) == 30
    assert not any(
        key in json.dumps(report) for key in ("C:\\\\Users\\\\kukka", '"command"', '"thread_id"')
    )


def test_blinded_export_grade_then_reveal_preserves_all_dimensions(monkeypatch, tmp_path):
    _, auth, _ = fake_runtime(monkeypatch, tmp_path)
    manifest = ROOT / "evals/benchmarks/phase9-v1.json"
    assert (
        runner.main(
            [
                "--execute",
                "--benchmark",
                str(manifest),
                "--case",
                definition()["cases"][0]["id"],
                "--model",
                "fake-model",
                "--reasoning-effort",
                "low",
                "--codex-home",
                str(auth),
                "--output-dir",
                str(tmp_path / "runs"),
            ]
        )
        == 0
    )
    report = next((tmp_path / "runs").glob("*/report.json"))
    original = report.read_bytes()
    reviewer = tmp_path / "reviewer"
    allocation = tmp_path / "private/allocation.json"
    assert (
        grader.main(
            [
                "blind",
                "--report",
                str(report),
                "--benchmark",
                str(manifest),
                "--reviewer-dir",
                str(reviewer),
                "--private-map",
                str(allocation),
            ]
        )
        == 0
    )
    packet_path = reviewer / "responses.json"
    packet = json.loads(packet_path.read_bytes())
    assert len(packet["responses"]) == 2
    assert all(
        set(row) == {"blind_id", "prompt", "response", "criteria", "critical_failures"}
        for row in packet["responses"]
    )
    assert not allocation.is_relative_to(reviewer)
    reviews = []
    for row in packet["responses"]:
        reviews.append(
            {
                "blind_id": row["blind_id"],
                "reviewer": {"identity": "synthetic protocol fixture", "independent": False},
                "reason": "Tests record validation, not real scientific correctness",
                "criteria": [
                    {
                        "id": c["id"],
                        "status": "PASS",
                        "reason": "Synthetic decision",
                        "evidence": [
                            {"start": 0, "end": len(row["response"]), "quote": row["response"]}
                        ],
                    }
                    for c in row["criteria"]
                ],
                "critical_failures": [
                    {
                        "id": c["id"],
                        "status": "NOT_OBSERVED",
                        "reason": "Whole response inspected in synthetic fixture",
                    }
                    for c in row["critical_failures"]
                ],
            }
        )
    judgments = tmp_path / "judgments.json"
    judgments.write_text(json.dumps({"responses": reviews}))
    grades = tmp_path / "grades.json"
    assert (
        grader.main(
            [
                "grade",
                "--packet",
                str(packet_path),
                "--judgments",
                str(judgments),
                "--output",
                str(grades),
            ]
        )
        == 0
    )
    result = tmp_path / "unblinded.json"
    assert (
        grader.main(
            [
                "unblind",
                "--grades",
                str(grades),
                "--private-map",
                str(allocation),
                "--output",
                str(result),
            ]
        )
        == 0
    )
    combined = json.loads(result.read_bytes())
    assert combined["execution_summary"] == {"COMPLETED": 2}
    assert {row["skill_availability"] for row in combined["responses"]} == {
        "AVAILABLE",
        "UNAVAILABLE",
    }
    assert all(
        not row["observed_target_read"] and row["activation_status"] == "UNOBSERVABLE"
        for row in combined["responses"]
    )
    assert all(
        row["usage"] == {"input_tokens": 3, "output_tokens": 2} for row in combined["responses"]
    )
    assert combined["provisional"] and combined["independent_human_validation"] == "PENDING"
    assert report.read_bytes() == original


def test_unresolved_grades_cannot_be_unblinded(tmp_path):
    grades = tmp_path / "grades.json"
    mapping = tmp_path / "map.json"
    grades.write_text(json.dumps({"grading_complete": False, "packet_sha256": "x"}))
    mapping.write_text(json.dumps({"packet_sha256": "x"}))
    output = tmp_path / "output.json"
    with pytest.raises(SystemExit) as error:
        grader.main(
            [
                "unblind",
                "--grades",
                str(grades),
                "--private-map",
                str(mapping),
                "--output",
                str(output),
            ]
        )
    assert error.value.code == 2 and not output.exists()


@pytest.mark.parametrize(
    "raw", ['{"status":"PASS","status":"FAIL"}', '{"x":{"id":1,"i\\u0064":2}}', '{"tokens":NaN}']
)
def test_duplicate_and_nonfinite_evidence_json_rejected(raw):
    with pytest.raises(ValueError):
        benchmark.decode_json(raw)


def test_uncheckpointed_running_turn_does_not_launch_duplicate_work(monkeypatch, tmp_path):
    _, auth, calls, path = start_interrupted(monkeypatch, tmp_path)
    report = json.loads(path.read_bytes())
    report["results"][0]["status"] = "RUNNING"
    path.write_text(json.dumps(report))
    before = path.read_bytes()
    with pytest.raises(SystemExit) as error:
        runner.main(["--resume", str(path), "--execute", "--codex-home", str(auth)])
    assert error.value.code == 2 and len(calls) == 1 and path.read_bytes() == before
