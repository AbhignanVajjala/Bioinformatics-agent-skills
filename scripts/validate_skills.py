"""Offline structural checks; not a claim of agent behavior or scientific validity."""

from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def parse_skill(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)\Z", text, re.S)
    if not match:
        raise ValueError("missing YAML frontmatter")
    meta = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(meta, dict):
        raise ValueError("frontmatter must be a mapping")
    if set(meta) - FIELDS:
        raise ValueError(f"unsupported fields: {set(meta) - FIELDS}")
    name = meta.get("name")
    if (
        not isinstance(name, str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
        or len(name) > 64
        or name != path.parent.name
    ):
        raise ValueError("invalid name or directory mismatch")
    for key, limit, required in [("description", 1024, True), ("compatibility", 500, False)]:
        value = meta.get(key)
        if required or key in meta:
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise ValueError(f"invalid {key}")
    for key in ("license", "allowed-tools"):
        if key in meta and not isinstance(meta[key], str):
            raise ValueError(f"{key} must be a string")
    if "metadata" in meta:
        values = meta["metadata"]
        if not isinstance(values, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) for k, v in values.items()
        ):
            raise ValueError("metadata must map strings to strings")
    if not match[2].strip():
        raise ValueError("empty instruction body")
    return meta


def broken_links(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    errors = []
    for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
        if re.match(r"[a-zA-Z]+:", target) or target.startswith("#"):
            continue
        target = target.split("#")[0]
        if target and not (path.parent / target).exists():
            errors.append(
                f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: missing {target}"
            )
    return errors


def validate(root=ROOT):
    errors = []
    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("no skills discovered")
    for path in skills:
        try:
            parse_skill(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{path}: {exc}")
    for path in root.rglob("*.md"):
        if any(
            part in {"artifacts", "build", "dist", "__pycache__"}
            for part in path.relative_to(root).parts
        ):
            continue  # Generated evidence/extractions are not repository documentation.
        if not any(
            part.startswith(".") and part != ".agents" and part != ".github"
            for part in path.relative_to(root).parts
        ):
            errors.extend(broken_links(path))
    return len(skills), errors


if __name__ == "__main__":
    count, errors = validate()
    print(f"{count} skills checked; {len(errors)} structural/link errors")
    print("\n".join(errors))
    sys.exit(bool(errors))
