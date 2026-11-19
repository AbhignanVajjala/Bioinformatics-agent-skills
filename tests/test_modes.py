"""Verify synchronized mode contracts without claiming model compliance."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_every_skill_exposes_same_mode_contract():
    policy = (ROOT / "docs/execution-modes.md").read_text(encoding="utf-8")
    assert "Create no mandatory files" in policy
    assert "commands, versions, hashes" in policy
    assert "Replicate minima supply no power guarantee" in policy
    for skill in (ROOT / ".agents/skills").glob("*/SKILL.md"):
        body = skill.read_text(encoding="utf-8")
        assert "[mode policy](references/modes.md)" in body
        assert "QUICK" in body and "FULL" in body
        assert (skill.parent / "references/modes.md").read_text(encoding="utf-8") == policy
