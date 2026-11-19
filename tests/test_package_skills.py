"""Check portable ZIP layout, deterministic builds, freshness and safe contents offline."""

import io
from pathlib import Path
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def packager(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import package_skills

    return package_skills


@pytest.fixture
def collection(tmp_path):
    for name in ("first-skill", "second-skill"):
        directory = tmp_path / ".agents/skills" / name
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test a skill.\n"
            "metadata:\n  maturity: experimental\n---\n"
            "Read [method notes](references/methods.md).\n",
            encoding="utf-8",
        )
        reference = directory / "references/methods.md"
        reference.parent.mkdir()
        reference.write_text("# Methods\n\nA reference with Unicode →.\n", encoding="utf-8")
    (tmp_path / "INSTALL.md").write_text("Install the collection. [License](LICENSE).\n")
    (tmp_path / "LICENSE").write_text("Fixture license\n")
    return tmp_path


def test_complete_repository_archive_and_extraction(packager):
    expected = packager.package_files(ROOT)
    names = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".agents/skills").rglob("*")
        if path.is_file()
    }
    assert set(expected) == names | {"INSTALL.md", "LICENSE"}
    assert sum(name.endswith("/SKILL.md") for name in names) == 13
    assert sum(name.endswith("/references/methods.md") for name in names) == 3
    archive = (ROOT / packager.ARCHIVE_NAME).read_bytes()
    packager.validate_archive(archive, expected)
    assert archive == packager.archive_bytes(expected)


def test_new_skill_is_discovered_without_a_packaging_list(packager, collection):
    directory = collection / ".agents/skills/new-skill"
    directory.mkdir()
    (directory / "SKILL.md").write_text(
        "---\nname: new-skill\ndescription: A new valid skill.\n"
        "metadata: {maturity: experimental}\n---\nDo the task.\n"
    )
    files = packager.package_files(collection)
    assert sum(name.endswith("/SKILL.md") for name in files) == 3
    assert ".agents/skills/new-skill/SKILL.md" in files


def test_build_ignores_filesystem_order_and_text_newlines(packager, collection):
    files = packager.package_files(collection)
    first = packager.archive_bytes(files)
    assert first == packager.archive_bytes(dict(reversed(list(files.items()))))
    for name in files:
        path = collection / name
        path.write_bytes(files[name].replace(b"\n", b"\r\n"))
        path.touch()
    rebuilt = packager.archive_bytes(packager.package_files(collection))
    assert first == rebuilt
    packager.validate_archive(rebuilt, files)


@pytest.mark.parametrize("change", ["skill", "reference", "install", "license", "missing-zip"])
def test_freshness_check_detects_stale_inputs(packager, collection, monkeypatch, change):
    monkeypatch.setattr(packager, "ROOT", collection)
    assert packager.main([]) == 0
    assert packager.main(["--check"]) == 0
    targets = {
        "skill": ".agents/skills/first-skill/SKILL.md",
        "reference": ".agents/skills/first-skill/references/methods.md",
        "install": "INSTALL.md",
        "license": "LICENSE",
    }
    archive = collection / packager.ARCHIVE_NAME
    if change == "missing-zip":
        archive.unlink()
    else:
        with (collection / targets[change]).open("a", encoding="utf-8") as stream:
            stream.write("An updated instruction.\n")
    with pytest.raises(SystemExit) as failure:
        packager.main(["--check"])
    assert failure.value.code == 1


def test_broken_reference_and_escape_are_rejected(packager, collection):
    skill = collection / ".agents/skills/first-skill/SKILL.md"
    (collection / "outside.md").write_text("Outside the package.")
    with skill.open("a", encoding="utf-8") as stream:
        stream.write("[outside](../../../outside.md)\n")
    with pytest.raises(ValueError, match="Unbundled"):
        packager.package_files(collection)


def test_links_from_reference_files_are_checked(packager, collection):
    reference = collection / ".agents/skills/first-skill/references/methods.md"
    reference.write_text("[notes][missing]\n\n[missing]: missing-notes.md\n")
    with pytest.raises(ValueError, match="missing-notes.md"):
        packager.package_files(collection)


@pytest.mark.parametrize("unwanted", ["credentials.pem", ".env", "__pycache__/cached.pyc"])
def test_unexpected_skill_resources_fail_the_build(packager, collection, unwanted):
    path = collection / ".agents/skills/first-skill/references" / unwanted
    path.parent.mkdir(exist_ok=True)
    path.write_text("This content must not enter the archive.")
    with pytest.raises(ValueError, match="Unexpected skill resource"):
        packager.package_files(collection)


def test_unrelated_repository_content_is_excluded(packager, collection):
    for name in (".env", ".git/config", "tests/test_x.py", "evals/reports/run.json"):
        path = collection / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Excluded content.")
    assert len(packager.package_files(collection)) == 6


def test_invalid_skill_is_reported_instead_of_silently_omitted(packager, collection):
    skill = collection / ".agents/skills/first-skill/SKILL.md"
    skill.write_text("---\nname: wrong-name\ndescription: Test\n---\nBody\n")
    with pytest.raises(ValueError, match="directory mismatch"):
        packager.package_files(collection)


@pytest.mark.parametrize(
    "tamper", ["missing", "unexpected", "duplicate", "content", "metadata", "truncated"]
)
def test_archive_integrity_rejects_changes(packager, collection, tamper):
    expected = packager.package_files(collection)
    data = packager.archive_bytes(expected)
    if tamper == "truncated":
        data = data[:-30]
    else:
        buffer = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(buffer, "w") as target:
            for index, info in enumerate(source.infolist()):
                if index == 0 and tamper == "missing":
                    continue
                body = source.read(info)
                if index == 0 and tamper == "content":
                    body = b"tampered"
                if index == 0 and tamper == "metadata":
                    info.date_time = (2020, 1, 1, 0, 0, 0)
                target.writestr(info, body)
            if tamper == "unexpected":
                target.writestr("../unexpected.txt", b"unexpected")
            elif tamper == "duplicate":
                with pytest.warns(UserWarning, match="Duplicate name"):
                    target.writestr("INSTALL.md", expected["INSTALL.md"])
        data = buffer.getvalue()
    with pytest.raises((ValueError, zipfile.BadZipFile)):
        packager.validate_archive(data, expected)
