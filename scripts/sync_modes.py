"""Keep every portable skill's mode reference synchronized with the common policy."""

import argparse

from validate_skills import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    policy = (ROOT / "docs/execution-modes.md").read_text(encoding="utf-8")
    stale = []
    for skill in sorted((ROOT / ".agents/skills").glob("*/SKILL.md")):
        target = skill.parent / "references/modes.md"
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != policy:
                stale.append(skill.parent.name)
        else:
            target.parent.mkdir(exist_ok=True)
            target.write_text(policy, encoding="utf-8")
    if stale:
        parser.exit(1, "Mode references stale: " + ", ".join(stale) + "\n")


if __name__ == "__main__":
    main()
