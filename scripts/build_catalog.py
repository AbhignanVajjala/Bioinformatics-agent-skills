"""Generate the skill index from canonical metadata."""

import argparse
from validate_skills import ROOT, parse_skill


def render():
    lines = [
        "# Skill catalog",
        "",
        "All skills are experimental; structural checks do not establish agent reliability.",
        "",
        "| Skill | Trigger |",
        "|---|---|",
    ]
    for path in sorted((ROOT / ".agents/skills").glob("*/SKILL.md")):
        meta = parse_skill(path)
        lines.append(
            f"| [{meta['name']}](../{path.relative_to(ROOT).as_posix()}) | {meta['description'].replace('|', '/')} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "docs/catalog.md"
    result = render()
    if args.check:
        if not path.exists() or path.read_text() != result:
            raise SystemExit("catalog stale: run python scripts/build_catalog.py")
    else:
        path.write_text(result)
