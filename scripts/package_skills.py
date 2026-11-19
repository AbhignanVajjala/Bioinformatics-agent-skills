#!/usr/bin/env python3
"""Build or check the reproducible skills-only ZIP without running an agent."""

from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path
import posixpath
import re
import stat
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

import yaml

from validate_skills import ROOT, parse_skill


ARCHIVE_NAME = "Bioinformatics-Agent-Skills-Complete.zip"
TOOLKIT_NAME = "Bioinformatics-Agent-Skills-Toolkit.zip"
LIGHT_DOCUMENTS = ("INSTALL.md", "LICENSE", "START_HERE.md", "SKILL_INDEX.md", "RELEASE.json")
TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = (stat.S_IFREG | 0o644) << 16


def source_bytes(path: Path) -> bytes:
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"Expected a regular, unlinked source file: {path.name}")
    # Git checkouts may use CRLF on Windows and LF in CI. Preserve the text,
    # while fixing its newline encoding for identical ZIPs on both platforms.
    return path.read_text(encoding="utf-8").encode("utf-8")


def package_files(root: Path, *, toolkit=False) -> dict[str, bytes]:
    root = root.resolve()
    skill_root = root / ".agents/skills"
    if skill_root.resolve() != skill_root or not skill_root.is_dir():
        raise ValueError("Missing or linked canonical skills directory")
    files = {name: source_bytes(root / name) for name in LIGHT_DOCUMENTS}
    directories = sorted(skill_root.iterdir())
    if not directories:
        raise ValueError("No skills discovered")
    for directory in directories:
        if directory.resolve() != directory or not directory.is_dir():
            raise ValueError(f"Unexpected skills entry: {directory.name}")
        skill = directory / "SKILL.md"
        source_bytes(skill)
        meta = parse_skill(skill)
        if meta.get("metadata", {}).get("maturity") != "experimental":
            raise ValueError(f"Expected experimental maturity: {directory.name}")
        for path in sorted(directory.rglob("*")):
            if path.resolve() != path:
                raise ValueError(f"Linked skill resource: {path.name}")
            relative = path.relative_to(directory)
            if path.is_dir() and relative.parts[0] == "references":
                continue
            if relative != Path("SKILL.md") and not (
                len(relative.parts) >= 2
                and relative.parts[0] == "references"
                and all(not part.startswith(".") for part in relative.parts)
                and path.suffix == ".md"
            ):
                raise ValueError(
                    f"Unexpected skill resource: {directory.name}/{relative.as_posix()}"
                )
            files[path.relative_to(root).as_posix()] = source_bytes(path)
    if toolkit:
        for name in (
            "pyproject.toml",
            "requirements-toolkit.txt",
            "TOOLKIT_INSTALL.md",
            "docs/validators.md",
        ):
            files[name] = source_bytes(root / name)
        for folder, extensions in (
            ("src/bioskills", {".py"}),
            ("examples", {".py", ".md"}),
            ("recipes/rnaseq", {".R", ".json"}),
            ("schemas", {".json"}),
            ("templates", {".json", ".md"}),
        ):
            directory = root / folder
            if directory.resolve() != directory or not directory.is_dir():
                raise ValueError(f"Missing or linked toolkit resource directory: {folder}")
            for path in sorted(directory.rglob("*")):
                if "__pycache__" in path.relative_to(directory).parts:
                    continue
                if path.resolve() != path:
                    raise ValueError(f"Linked toolkit resource: {path.name}")
                if path.is_dir():
                    continue
                if path.suffix not in extensions or path.name.startswith("."):
                    raise ValueError(f"Unexpected toolkit resource: {path.name}")
                files[path.relative_to(root).as_posix()] = source_bytes(path)
    if len({name.casefold() for name in files}) != len(files):
        raise ValueError("Package paths collide on case-insensitive filesystems")
    validate_links(files)
    return files


def validate_links(files: dict[str, bytes]) -> None:
    """Check bundled Markdown targets, including links from reference notes."""
    for name, contents in files.items():
        if not name.endswith(".md"):
            continue
        text = re.sub(r"```.*?```", "", contents.decode("utf-8"), flags=re.S)
        inline = re.findall(r"\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)", text)
        definitions = re.findall(r"(?m)^ {0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?", text)
        for target in inline + definitions:
            url = urlsplit(target)
            if url.scheme in {"https", "http", "mailto"} or target.startswith("#"):
                continue
            local = unquote(url.path)
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), local))
            if url.scheme or url.netloc or local.startswith("/") or resolved not in files:
                raise ValueError(f"Unbundled or invalid reference in {name}: {target}")


def archive_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    # Stored members avoid compression-library differences across Python builds.
    # The complete instruction collection is small enough for this ZIP format.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, contents in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=TIMESTAMP)
            info.create_system = 3
            info.external_attr = FILE_MODE
            archive.writestr(info, contents)
    return buffer.getvalue()


def validate_archive(data: bytes, expected: dict[str, bytes]) -> None:
    """Verify the exact inventory, deterministic bytes and extracted resources."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.namelist() != sorted(expected) or archive.testzip() is not None:
            raise ValueError("Archive inventory or CRC mismatch")
        for info in archive.infolist():
            if (
                info.date_time != TIMESTAMP
                or info.create_system != 3
                or info.external_attr != FILE_MODE
                or info.compress_type != zipfile.ZIP_STORED
                or info.extra
                or info.comment
                or archive.read(info) != expected[info.filename]
            ):
                raise ValueError(f"Archive content or metadata mismatch: {info.filename}")
        if archive.comment or data != archive_bytes(expected):
            raise ValueError("Archive encoding is not canonical")
        # Inventory equality above admits only the explicitly bundled paths.
        with tempfile.TemporaryDirectory(prefix="bioskills-package-") as directory:
            extracted = Path(directory)
            archive.extractall(extracted)
            actual = {
                path.relative_to(extracted).as_posix(): path.read_bytes()
                for path in extracted.rglob("*")
                if path.is_file()
            }
            if actual != expected:
                raise ValueError("Extracted package differs from the expected files")
            for skill in sorted((extracted / ".agents/skills").glob("*/SKILL.md")):
                parse_skill(skill)
            validate_links(actual)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the tracked ZIP is stale")
    args = parser.parse_args(argv)
    try:
        checksums = []
        for name, toolkit in ((ARCHIVE_NAME, False), (TOOLKIT_NAME, True)):
            files = package_files(ROOT, toolkit=toolkit)
            generated = archive_bytes(files)
            output = ROOT / name
            if args.check:
                if not output.is_file() or output.read_bytes() != generated:
                    raise ValueError(
                        f"{name} missing or stale. Run python scripts/package_skills.py"
                    )
            validate_archive(generated, files)
            if not args.check:
                pending = output.with_suffix(".zip.tmp")
                pending.write_bytes(generated)
                pending.replace(output)
            sha = hashlib.sha256(generated).hexdigest()
            checksums.append(f"{sha}  {name}\n")
            count = sum(path.endswith("/SKILL.md") for path in files)
            print(
                f"{name}: {count} skills, {len(files)} files, {len(generated)} bytes, SHA-256 {sha}"
            )
        checksum_file = ROOT / "SHA256SUMS"
        checksum_text = "".join(checksums)
        if args.check:
            if (
                not checksum_file.is_file()
                or checksum_file.read_text(encoding="utf-8") != checksum_text
            ):
                raise ValueError("SHA256SUMS missing or stale")
        else:
            checksum_file.write_text(checksum_text, encoding="utf-8", newline="\n")
    except (OSError, ValueError, yaml.YAMLError, zipfile.BadZipFile) as error:
        parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
