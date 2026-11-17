import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_skills.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def skill(tmp_path, front, body="Instructions"):
    path = tmp_path / "valid-name" / "SKILL.md"
    path.parent.mkdir()
    path.write_text("---\n" + front + "\n---\n" + body)
    return path


@pytest.mark.parametrize(
    "front",
    [
        "name: Wrong\ndescription: test",
        'name: valid-name\ndescription: ""',
        "name: valid-name\ndescription: yes",
        "name: valid-name\ndescription: test\ncompose: [x]",
        "name: valid-name\ndescription: test\nmetadata: {version: 1}",
        "name: valid-name\ndescription: test\nname: other",
        "name: valid-name\ndescription: test\nallowed-tools: [Bash]",
    ],
)
def test_reject_invalid_metadata(tmp_path, front):
    with pytest.raises(ValueError):
        v.parse_skill(skill(tmp_path, front))


def test_valid_metadata(tmp_path):
    assert (
        v.parse_skill(skill(tmp_path, "name: valid-name\ndescription: Test a dataset."))["name"]
        == "valid-name"
    )


def test_missing_link(tmp_path):
    path = skill(tmp_path, "name: valid-name\ndescription: test", "[missing](references/absent.md)")
    assert v.broken_links(path)


def test_repo_structure():
    count, errors = v.validate()
    assert count >= 13
    assert errors == []


def test_trigger_cases_cover_each_skill_without_fabricated_runs():
    import json

    cases = json.loads((ROOT / "evals/cases/triggers.json").read_text())
    names = {p.parent.name for p in (ROOT / ".agents/skills").glob("*/SKILL.md")}
    assert {c["skill"] for c in cases} == names
    assert len({c["id"] for c in cases}) == len(cases)
    for name in names:
        group = [c for c in cases if c["skill"] == name]
        assert sum(c["expected_activation"] is True for c in group) >= 2
        assert sum(c["expected_activation"] is False for c in group) >= 2
        assert all(c["status"] == "NOT_RUN" and c["evidence"] is None for c in group)
