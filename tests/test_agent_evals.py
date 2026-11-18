"""Exercise the agent harness with synthetic local events and no model calls."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "run_agent_evals", ROOT / "scripts/run_agent_evals.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def events(thread="test-thread", response="Synthetic response"):
    return [
        {"type": "thread.started", "thread_id": thread},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": response}},
        {"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 2}},
    ]


def write_events(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def report_in(output):
    reports = list(output.glob("*/report.json"))
    assert len(reports) == 1
    return reports[0], json.loads(reports[0].read_bytes())


def test_plan_expands_paired_cases_without_invoking_codex(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Planning touched the runtime")

    monkeypatch.setattr(runner.subprocess, "run", forbidden)
    assert runner.main(["--output-dir", str(tmp_path)]) == 0
    _, report = report_in(tmp_path)
    assert report["summary"] == {"NOT_RUN": 114}
    assert len({row["id"] for row in report["results"] if row["track"] == "trigger"}) == 52
    assert len({row["id"] for row in report["results"] if row["track"] == "scientific"}) == 5
    assert len(report["skill_hashes"]) == 16
    for baseline, enabled in zip(report["results"][::2], report["results"][1::2], strict=True):
        assert [baseline["mode"], enabled["mode"]] == ["baseline", "skills"]
        assert baseline["prompt_sha256"] == enabled["prompt_sha256"]
        assert baseline["evaluation_status"] == enabled["evaluation_status"] == "NOT_RUN"


def test_only_case_inputs_form_candidate_prompts(tmp_path):
    source = tmp_path / "source"
    for filename in (*runner.MANIFESTS, runner.RUBRIC):
        path = source / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if filename == runner.RUBRIC:
            path.write_bytes(b"RUBRIC_SECRET")
            continue
        row = {
            "id": "case-" + path.stem,
            "input": "Only this prompt",
            "skill": "example",
            "track": "agent",
            "expected_activation": "HIDDEN_LABEL",
            "expected_behavior": "HIDDEN_ANSWER",
            "scoring_rubric": "RUBRIC_SECRET",
        }
        path.write_text(json.dumps([row]), encoding="utf-8")
    skill = source / ".agents/skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_bytes(b"approved skill")
    (skill.parent / "answers.json").write_bytes(b"HIDDEN_ANSWER")
    (source / "AGENTS.md").write_bytes(b"parent instructions")

    cases, skills, _ = runner.load_inputs(source.resolve())
    assert set(cases) == {"case-triggers", "case-scientific"}
    assert cases["case-triggers"][1] == b"Only this prompt"
    for _, prompt in cases.values():
        assert b"Only this prompt" in prompt
        assert not any(
            marker in prompt for marker in (b"HIDDEN_ANSWER", b"HIDDEN_LABEL", b"RUBRIC_SECRET")
        )
    baseline, enabled = tmp_path / "baseline", tmp_path / "enabled"
    runner.stage_workspace(baseline, {})
    runner.stage_workspace(enabled, skills)
    assert not list(baseline.iterdir())
    assert [path.read_bytes() for path in enabled.rglob("*") if path.is_file()] == [
        b"approved skill"
    ]


def test_pilot_plan_has_five_cases_with_matched_prompts(tmp_path):
    assert runner.main(["--pilot", "--output-dir", str(tmp_path)]) == 0
    _, report = report_in(tmp_path)
    rows = report["results"]
    assert report["summary"] == {"NOT_RUN": 10}
    assert {row["id"] for row in rows} == {
        "research-specification-explicit-pilot",
        "research-specification-positive-1",
        "scientific-prompt-engineering-negative-2",
        "enrichment-background",
        "survival-censoring",
    }
    cases, _, _ = runner.load_inputs(ROOT)
    _, prompt = cases["research-specification-positive-1"]
    assert rows[0]["prompt_sha256"] == runner.digest(b"$research-specification " + prompt)
    for baseline, enabled in zip(rows[::2], rows[1::2], strict=True):
        assert baseline["id"] == enabled["id"]
        assert [baseline["mode"], enabled["mode"]] == ["baseline", "skills"]
        assert baseline["prompt_sha256"] == enabled["prompt_sha256"]
        assert baseline["evaluation_status"] == enabled["evaluation_status"] == "NOT_RUN"


def test_child_environment_is_allowlisted(tmp_path, monkeypatch):
    if sys.platform == "win32":
        monkeypatch.setenv("SystemDrive", Path("C:/").drive)
    for name in (
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "GH_TOKEN",
        "AWS_SESSION_TOKEN",
        "HTTP_PROXY",
        "CODEX_HOME",
        "PYTHONPATH",
        "HOME",
        "USERPROFILE",
        "APPDATA",
        "PATH",
    ):
        monkeypatch.setenv(name, "PRIVATE_SENTINEL")
    env = runner.isolated_env(tmp_path, None)
    assert "PRIVATE_SENTINEL" not in env.values()
    assert Path(env["HOME"]).is_relative_to(tmp_path)
    assert Path(env["CODEX_HOME"]).is_relative_to(tmp_path)
    assert Path(env["TEMP"]).is_dir()
    assert env["HOME"] == env["USERPROFILE"]
    if sys.platform == "win32":
        assert env["SystemDrive"] == Path("C:/").drive


@pytest.mark.parametrize(
    "alteration",
    [
        "empty",
        "bad-json",
        "missing-start",
        "extra-turn",
        "failed-turn",
        "late-message",
        "wrong-final",
        "empty-final",
    ],
)
def test_incomplete_protocol_is_rejected(tmp_path, alteration):
    stream, final = tmp_path / "events.jsonl", tmp_path / "response.txt"
    rows = events()
    response = "Synthetic response"
    if alteration == "empty":
        rows = []
    elif alteration == "missing-start":
        rows.pop(1)
    elif alteration == "extra-turn":
        rows += events()
    elif alteration == "failed-turn":
        rows[-1] = {"type": "turn.failed"}
    elif alteration == "late-message":
        rows[2], rows[3] = rows[3], rows[2]
    elif alteration == "wrong-final":
        response = "Unrelated response"
    elif alteration == "empty-final":
        response = ""
    if alteration == "bad-json":
        stream.write_bytes(b'{"type":')
    else:
        write_events(stream, rows)
    final.write_text(response, encoding="utf-8")
    parsed = runner.actions_in_stream(stream, final, tmp_path, {})
    assert "problem" in parsed


def test_skill_output_is_only_a_read_proxy(tmp_path):
    stream, final = tmp_path / "events.jsonl", tmp_path / "response.txt"
    skill = Path(".agents/skills/example/SKILL.md")
    rows = events(response=f"I used {skill}")
    for item_id, exit_code, body in (
        ("failed", 1, "test instructions"),
        ("just-a-filename", 0, "file found"),
        ("read", 0, "test instructions"),
    ):
        rows.insert(
            2,
            {
                "type": "item.completed",
                "item": {
                    "id": item_id,
                    "type": "command_execution",
                    "command": f"""powershell.exe -NoProfile -Command "Get-Content '{tmp_path / skill}'" """,
                    "exit_code": exit_code,
                    "aggregated_output": body,
                },
            },
        )
    write_events(stream, rows)
    final.write_text(f"I used {skill}", encoding="utf-8")
    parsed = runner.actions_in_stream(stream, final, tmp_path, {skill: b"test instructions"})
    assert "problem" not in parsed
    assert parsed["observed_skill_reads"] == [
        {
            "skill": "example",
            "file": skill.as_posix(),
            "item_id": "read",
            "jsonl_line": 3,
            "read_index": 1,
            "output_encoding": "utf-8",
        }
    ]
    assert parsed["skill_evidence"] == {
        "trace_status": "VERIFIED",
        "instruction_following_status": "NOT_ASSESSED",
        "ambiguous_item_ids": ["just-a-filename"],
        "by_skill": {"example": "SKILL_FILE_READ_OBSERVED"},
    }
    assert parsed["activation_status"] == "UNOBSERVABLE"


def command_item(command, output, *, exit_code=0, item_id="read"):
    return {
        "type": "item.completed",
        "item": {
            "type": "command_execution",
            "id": item_id,
            "status": "completed",
            "exit_code": exit_code,
            "command": command,
            "aggregated_output": output,
        },
    }


def test_replay_multiple_relative_powershell_reads(tmp_path):
    a = Path(".agents/skills/first/SKILL.md")
    b = Path(".agents/skills/second/SKILL.md")
    stream, final = tmp_path / "events.jsonl", tmp_path / "response.txt"
    script = (
        f""""C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -Command """
        f"""'Get-Content ./{a.as_posix()}; Get-Content {b.as_posix()}'"""
    )
    rows = events()
    # The original trace's PowerShell reads UTF-8 without a BOM as Windows-1252.
    rows.insert(2, command_item(script, "a\r\nb \u00e2\u20ac\u009d\r\n"))
    write_events(stream, rows)
    final.write_text("Synthetic response", encoding="utf-8")
    parsed = runner.actions_in_stream(
        stream,
        final,
        r"C:\scratch\workspace",
        {
            a: b"a\r\n",
            b: "b ”\r\n".encode(),
        },
    )
    assert "problem" not in parsed
    reads = parsed["observed_skill_reads"]
    assert [(r["file"], r["jsonl_line"], r["read_index"]) for r in reads] == [
        (a.as_posix(), 3, 1),
        (b.as_posix(), 3, 2),
    ]
    assert {r["output_encoding"] for r in reads} == {"windows-1252"}
    assert parsed["activation_status"] == "UNOBSERVABLE"


@pytest.mark.parametrize(
    ("command", "output", "exit_code", "ambiguous"),
    [
        ("Write-Output '.agents/skills/example/SKILL.md'", "expected text", 0, True),
        ("Get-Content ../.agents/skills/example/SKILL.md", "expected text", 0, True),
        ("Get-Content .agents/skills/example/SKILL.md.bak", "expected text", 0, True),
        (
            "Get-Content .agents/skills/example/SKILL.md | Select-Object -First 1",
            "expected text",
            0,
            True,
        ),
        ("Get-Content .agents/skills/example/SKILL.md", "partial output", 0, True),
        ("Get-Content .agents/skills/example/SKILL.md", "", 1, False),
        ("Get-ChildItem", ".agents/skills/example/SKILL.md", 0, False),
    ],
)
def test_reads_require_literal_staged_path_and_matching_complete_output(
    tmp_path, command, output, exit_code, ambiguous
):
    stream, final = tmp_path / "events.jsonl", tmp_path / "response.txt"
    rows = events(response="I used the example skill.")
    rows.insert(
        2,
        command_item(
            f'powershell.exe -NoProfile -Command "{command}"', output, exit_code=exit_code
        ),
    )
    write_events(stream, rows)
    final.write_text("I used the example skill.", encoding="utf-8")
    catalog = {Path(".agents/skills/example/SKILL.md"): b"expected text"}
    parsed = runner.actions_in_stream(stream, final, tmp_path, catalog)
    assert parsed["observed_skill_reads"] == []
    assert parsed["skill_evidence"]["ambiguous_item_ids"] == (["read"] if ambiguous else [])
    assert parsed["skill_evidence"]["by_skill"] == {"example": "AVAILABLE_NO_OBSERVED_READ"}
    unavailable = runner.actions_in_stream(stream, final, tmp_path, catalog, skills_enabled=False)
    assert unavailable["skill_evidence"]["by_skill"] == {"example": "UNAVAILABLE"}


@pytest.mark.parametrize(
    "malformation", ["duplicate", "missing-output", "boolean-exit", "broken-json"]
)
def test_invalid_trace_does_not_retain_an_earlier_read(tmp_path, malformation):
    stream, final = tmp_path / "events.jsonl", tmp_path / "response.txt"
    command = 'powershell.exe -NoProfile -Command "Get-Content .agents/skills/example/SKILL.md"'
    rows = events()
    rows.insert(2, command_item(command, "expected text"))
    if malformation != "broken-json":
        extra = command_item(command, "expected text", item_id="another")
        if malformation == "duplicate":
            extra["item"]["id"] = "read"
        elif malformation == "missing-output":
            del extra["item"]["aggregated_output"]
        else:
            extra["item"]["exit_code"] = False
        rows.insert(3, extra)
    write_events(stream, rows)
    if malformation == "broken-json":
        with stream.open("a", encoding="utf-8") as file:
            file.write('{"type":\n')
    final.write_text("Synthetic response", encoding="utf-8")
    parsed = runner.actions_in_stream(
        stream, final, tmp_path, {Path(".agents/skills/example/SKILL.md"): b"expected text"}
    )
    assert "problem" in parsed
    assert parsed["observed_skill_reads"] == []
    assert parsed["skill_evidence"]["trace_status"] == "INVALID"
    assert parsed["skill_evidence"]["by_skill"] == {"example": "AVAILABLE_TRACE_UNVERIFIED"}


@pytest.mark.parametrize("tampered", [False, True])
def test_inspect_report_replays_offline_and_enforces_hashes(
    tmp_path, monkeypatch, capsys, tampered
):
    def forbidden(*args, **kwargs):
        pytest.fail("Evidence replay tried to start a subprocess")

    monkeypatch.setattr(runner.subprocess, "run", forbidden)
    _, skills, hashes = runner.load_inputs(ROOT)
    evidence = tmp_path / "attempt-001"
    evidence.mkdir()
    (evidence / "prompt.txt").write_bytes(b"test prompt")
    (evidence / "response.txt").write_bytes(b"Synthetic response")
    write_events(evidence / "events.jsonl", events())
    artifact_hashes = {path.name: runner.digest(path.read_bytes()) for path in evidence.iterdir()}
    report = tmp_path / "report.json"
    runner.save_json(
        report,
        {
            "schema_version": 1,
            "run_id": "synthetic",
            "input_hashes": hashes,
            "skill_hashes": {
                path.as_posix(): runner.digest(contents) for path, contents in skills.items()
            },
            "results": [
                {
                    "id": "smoke",
                    "mode": "baseline",
                    "status": "COMPLETED",
                    "thread_id": "test-thread",
                    "artifact_dir": evidence.name,
                    "artifacts": artifact_hashes,
                    "prompt_sha256": artifact_hashes["prompt.txt"],
                    "command": ["codex", "--cd", str(tmp_path)],
                }
            ],
        },
    )
    original = report.read_bytes()
    if tampered:
        (evidence / "response.txt").write_bytes(b"Changed content")
        with pytest.raises(SystemExit) as error:
            runner.main(["--inspect-report", str(report)])
        assert error.value.code == 2
        assert "failed hash verification" in capsys.readouterr().err
    else:
        assert runner.main(["--inspect-report", str(report)]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["source_report_sha256"] == runner.digest(original)
        turn = result["results"][0]
        assert turn["skill_evidence"]["trace_status"] == "VERIFIED"
        assert set(turn["skill_evidence"]["by_skill"].values()) == {"UNAVAILABLE"}
        assert str(tmp_path) not in json.dumps(result)
    assert report.read_bytes() == original


def test_real_subprocess_receives_stdin_without_shell(tmp_path):
    command = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"]
    stdout, stderr = tmp_path / "stdout", tmp_path / "stderr"
    message = 'A "quote", a newline\n and a unicode β'.encode()
    result = runner.invoke(
        command, tmp_path, runner.isolated_env(tmp_path, None), stdout, stderr, 10, message
    )
    assert result["exit_status"] == 0
    assert stdout.read_bytes() == message


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired(["codex"], 1)])
def test_launch_failures_have_timestamps_and_stream_files(tmp_path, monkeypatch, failure):
    def fail(*args, **kwargs):
        raise failure

    monkeypatch.setattr(runner.subprocess, "run", fail)
    stdout, stderr = tmp_path / "stdout", tmp_path / "stderr"
    result = runner.invoke(["codex"], tmp_path, {}, stdout, stderr, 1)
    assert result["exit_status"] is None
    assert result["problem"]
    assert result["started_at"] <= result["ended_at"]
    assert stdout.is_file() and stderr.is_file()


@pytest.mark.parametrize(
    "scenario,expected",
    [
        ("ok", ["COMPLETED", "COMPLETED"]),
        ("duplicate-thread", ["COMPLETED", "FAILED"]),
        ("nonzero", ["FAILED", "BLOCKED"]),
        ("preflight-blocked", ["BLOCKED", "BLOCKED"]),
    ],
)
def test_batch_statuses_and_session_isolation(tmp_path, monkeypatch, scenario, expected):
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(runner.shutil, "which", lambda name: str(tmp_path / "codex.exe"))
    calls = []

    def fake_preflight(*args):
        return [], "probe failed" if scenario == "preflight-blocked" else None

    def fake_invoke(command, cwd, env, stdout, stderr, timeout, prompt):
        calls.append((cwd, env["HOME"], prompt))
        assert cwd.parent.parent == tmp_path
        assert not (cwd / "evals").exists()
        assert not (cwd / "AGENTS.md").exists()
        assert "--ignore-user-config" in command and "--ephemeral" in command
        assert "--strict-config" in command
        assert command[-1] == "-" and prompt.decode() not in command
        assert str(cwd) in command
        assert (cwd / ".agents").exists() == (len(calls) == 2)
        assert all("positive-1" not in arg for arg in command)
        thread = "same" if scenario == "duplicate-thread" else f"thread-{len(calls)}"
        write_events(stdout, events(thread))
        stderr.write_bytes(b"")
        Path(command[command.index("--output-last-message") + 1]).write_bytes(b"Synthetic response")
        return {"command": command, "exit_status": 4 if scenario == "nonzero" else 0}

    monkeypatch.setattr(runner, "preflight", fake_preflight)
    monkeypatch.setattr(runner, "invoke", fake_invoke)
    auth = tmp_path / "auth"
    auth.mkdir()
    output = tmp_path / "reports"
    status = runner.main(
        [
            "--execute",
            "--case",
            "scientific-prompt-engineering-positive-1",
            "--model",
            "mock-model",
            "--codex-home",
            str(auth),
            "--output-dir",
            str(output),
        ]
    )
    report_path, report = report_in(output)
    assert [row["status"] for row in report["results"]] == expected
    assert all(row["evaluation_status"] == "NOT_RUN" for row in report["results"])
    assert status == (scenario != "ok")
    assert len(calls) == sum(row in {"COMPLETED", "FAILED"} for row in expected)
    if len(calls) == 2:
        assert calls[0][:2] != calls[1][:2]
        assert calls[0][2] == calls[1][2]
        for row in report["results"]:
            folder = report_path.parent / row["artifact_dir"]
            assert row["artifacts"]["prompt.txt"] == row["prompt_sha256"]
            assert row["artifacts"]["response.txt"] == runner.digest(
                (folder / "response.txt").read_bytes()
            )


def test_missing_cli_blocks_smoke(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    auth = tmp_path / "auth"
    auth.mkdir()
    assert (
        runner.main(
            [
                "--execute",
                "--smoke",
                "--model",
                "mock-model",
                "--codex-home",
                str(auth),
                "--output-dir",
                str(tmp_path),
            ]
        )
        == 1
    )
    _, report = report_in(tmp_path)
    assert report["summary"] == {"BLOCKED": 1}
    assert report["results"][0]["evaluation_status"] == "NOT_RUN"
    assert report["preflight"] == []


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-native preflight")
def test_windows_overrides_use_cli_compatible_mxc_selection(tmp_path):
    args = runner.overrides(tmp_path)
    assert args[::2] == ["-c"] * (len(args) // 2)
    settings = dict(arg.split("=", 1) for arg in args[1::2])
    # Codex CLI 0.168.0 rejects requirements-level keys in strict config overrides.
    assert {key for key in settings if key.startswith("windows.")} == {"windows.sandbox"}
    assert settings["windows.sandbox"] == '"mxc"'
    assert settings["default_permissions"] == '"agent-eval"'
    assert settings["permissions.agent-eval.filesystem"] == (
        f'{{ ":minimal" = "read", {json.dumps(str(tmp_path), ensure_ascii=False)} = "read" }}'
    )
    assert settings["permissions.agent-eval.network.enabled"] == "false"
    assert settings["approval_policy"] == '"never"'
    assert "sandbox_mode" not in settings


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-native preflight")
@pytest.mark.parametrize(
    ("isolation_exit", "isolation_output", "isolation_ok"),
    [
        (1, b"ISOLATION_OK\n", False),
        (0, b"unexpected output\n", False),
        (0, b"ISOLATION_OK\n", True),
    ],
    ids=["mxc-rejected", "missing-canary", "isolated"],
)
def test_preflight_refuses_unsafe_runtime_without_persisting_login_output(
    tmp_path, monkeypatch, isolation_exit, isolation_output, isolation_ok
):
    def fake_invoke(command, cwd, env, stdout, stderr, timeout):
        result = b"codex-cli 0.168.0\n"
        exit_code = 0
        if command[1] == "sandbox":
            assert 'windows.sandbox="mxc"' in command
            assert 'shell_environment_policy.inherit="none"' in command
            system_root_arg = next(
                arg for arg in command if arg.startswith("shell_environment_policy.set.SYSTEMROOT=")
            )
            assert json.loads(system_root_arg.split("=", 1)[1]) == env["SystemRoot"]
            assert "--include-managed-config" in command
            assert (cwd / "inside.txt").is_file()
            assert (cwd.parent / "outside.txt").is_file()
            result = isolation_output
            exit_code = isolation_exit
        stdout.write_bytes(result)
        stderr.write_bytes(b"")
        return {"command": command, "exit_status": exit_code}

    def login(command, **kwargs):
        assert isolation_ok
        assert command[1:3] == ["login", "status"]
        assert kwargs["env"]["CODEX_HOME"] == str(tmp_path / "auth")
        return subprocess.CompletedProcess(command, 0, b"Logged in using an API key", b"SECRET")

    monkeypatch.setattr(runner, "invoke", fake_invoke)
    monkeypatch.setattr(runner.subprocess, "run", login)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    steps, blocker = runner.preflight(
        "codex.exe", tmp_path / "probe", evidence, tmp_path / "auth", False
    )
    assert blocker and ("login" in blocker if isolation_ok else "isolation" in blocker)
    assert [step["name"] for step in steps] == (
        ["version", "isolation", "chatgpt_login"] if isolation_ok else ["version", "isolation"]
    )
    assert "SECRET" not in json.dumps(steps)
    assert all(b"SECRET" not in path.read_bytes() for path in evidence.iterdir())
