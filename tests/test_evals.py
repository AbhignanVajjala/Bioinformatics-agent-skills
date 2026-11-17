"""Test that evaluation reporting cannot turn skipped or empty runs into success."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_evals", ROOT / "scripts/run_evals.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@pytest.mark.parametrize(
    "xml,code,status",
    [
        ('<testsuites><testsuite><testcase name="x"/></testsuite></testsuites>', 0, "PASS"),
        ("<testsuites><testsuite/></testsuites>", 0, "FAIL"),
        ("<testsuite><testcase><skipped/></testcase></testsuite>", 0, "BLOCKED"),
        ("<testsuite><testcase><failure/></testcase></testsuite>", 1, "FAIL"),
        ("<testsuite><testcase><error/></testcase></testsuite>", 0, "FAIL"),
        ("<testsuite><testcase/></testsuite>", 2, "FAIL"),
        ("not xml", 0, "FAIL"),
    ],
)
def test_truthful_status(tmp_path, xml, code, status):
    path = tmp_path / "results.xml"
    path.write_text(xml)
    assert runner.classify_junit(path, code)[0] == status


def test_missing_result_is_failure(tmp_path):
    assert runner.classify_junit(tmp_path / "absent.xml", 0)[0] == "FAIL"


def test_agent_case_is_not_scored_as_passing(tmp_path):
    result = runner.run_case({"id": "citation", "track": "agent"}, tmp_path)
    assert result["status"] == "NOT_RUN"
    assert "command" not in result


def test_case_inventory():
    cases = json.loads((ROOT / "evals/cases/scientific.json").read_text())
    assert len(cases) == 12
    assert len({case["id"] for case in cases}) == 12
    for case in cases:
        for field in ["input", "expected_behavior", "failure_behavior", "test_method", "rubric"]:
            assert case[field]
        if case["track"] == "tool":
            assert case["test_nodes"]
