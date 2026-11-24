"""Check portable ZIP layout, deterministic builds, freshness and safe contents offline."""

import io
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sysconfig
import venv
import zipfile

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def packager(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import package_skills

    return package_skills


@pytest.fixture
def collection(tmp_path, packager):
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
    for name in (
        *packager.DOCUMENTS,
        *packager.REQUIRED_RESOURCES,
        "src/bioskills/example.py",
        "examples/example.py",
        "recipes/rnaseq/run.R",
        "schemas/check.schema.json",
        "templates/check.json",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("Fixture resource\n")
    return tmp_path


def test_complete_repository_archive_and_extraction(packager):
    expected = packager.package_files(ROOT)
    names = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".agents/skills").rglob("*")
        if path.is_file()
    }
    toolkit_names = {
        path.relative_to(ROOT).as_posix()
        for folder, _ in packager.TOOLKIT_TREES
        for path in (ROOT / folder).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert set(expected) == names | set(packager.DOCUMENTS) | toolkit_names
    assert sorted(path.name for path in ROOT.glob("*.zip")) == [packager.ARCHIVE_NAME]
    assert sum(name.endswith("/SKILL.md") for name in names) == len(
        list((ROOT / ".agents/skills").glob("*/SKILL.md"))
    )
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


@pytest.mark.parametrize(
    "change",
    ["skill", "reference", "install", "license", "script", "dependency", "missing-zip", "checksum"],
)
def test_freshness_check_detects_stale_inputs(packager, collection, monkeypatch, change):
    monkeypatch.setattr(packager, "ROOT", collection)
    assert packager.main([]) == 0
    assert packager.main(["--check"]) == 0
    targets = {
        "skill": ".agents/skills/first-skill/SKILL.md",
        "reference": ".agents/skills/first-skill/references/methods.md",
        "install": "INSTALL.md",
        "license": "LICENSE",
        "script": "src/bioskills/example.py",
        "dependency": "requirements-toolkit.txt",
        "checksum": "SHA256SUMS",
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
    with pytest.raises(ValueError, match="Unexpected skill resource|Credential-like"):
        packager.package_files(collection)


def test_unrelated_repository_content_is_excluded(packager, collection):
    expected = packager.package_files(collection)
    for name in (".env", ".git/config", "tests/test_x.py", "evals/reports/run.json"):
        path = collection / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Excluded content.")
    assert packager.package_files(collection) == expected


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


def test_universal_extracts_installs_and_first_use_executes(packager, tmp_path):
    tmp_path = tmp_path.resolve()
    files = packager.package_files(ROOT)
    archive = (ROOT / packager.ARCHIVE_NAME).read_bytes()
    packager.validate_archive(archive, files)
    assert not any(name.startswith(("tests/", "evals/", ".git/")) for name in files)
    extracted = tmp_path / "universal"
    with zipfile.ZipFile(io.BytesIO(archive)) as zip_file:
        zip_file.extractall(extracted)
    for name, content in files.items():
        if name.endswith(".md"):
            for script in re.findall(
                r"(?:python|Rscript) ([\w/-]+\.(?:py|R))", content.decode("utf-8")
            ):
                assert (extracted / script).is_file(), (name, script)
    # Reuse installed third-party dependencies for an offline test, but install
    # this distribution normally in a new venv. -I ignores repository PYTHONPATH.
    # CI also installs all dependencies into a fully isolated, clean environment.
    environment = tmp_path / "installed"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env.update(
        PYTHONUTF8="1",
        PIP_NO_INDEX="1",
        PIP_DISABLE_PIP_VERSION_CHECK="1",
        XDG_CACHE_HOME=str(tmp_path / "cache"),
        MPLCONFIGDIR=str(tmp_path / "mpl"),
    )
    installed_site = Path(
        subprocess.check_output(
            [str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            text=True,
            env=env,
            cwd=extracted,
        ).strip()
    )
    # Add dependency files only. Unlike addsitedir, a path line does not execute
    # the parent environment's editable-install .pth hooks into the repository.
    (installed_site / "offline-dependencies.pth").write_text(
        sysconfig.get_path("purelib") + "\n", encoding="utf-8"
    )

    def run(*args, code=0):
        result = subprocess.run(
            [str(python), "-I", *args],
            cwd=extracted,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == code, result.stdout + result.stderr
        return result

    run(
        "-m",
        "pip",
        "install",
        "--no-index",
        "--no-deps",
        "--no-build-isolation",
        "--ignore-installed",
        ".",
    )
    probe = run(
        "-c",
        "import bioskills, importlib, json; from pathlib import Path; "
        "names=['science','validators','expanded','retrieval','domain_workflows','inputs','aggregation','enrichment','formats']; "
        "print(json.dumps([str(Path(bioskills.__file__).resolve())] + "
        "[str(Path(importlib.import_module('bioskills.'+n).__file__).resolve()) for n in names]))",
    )
    assert all(Path(path).is_relative_to(environment) for path in json.loads(probe.stdout))
    names = (
        "check_counts",
        "check_sample_ids",
        "check_design_rank",
        "check_replication",
        "check_fba_status",
        "check_leakage",
        "check_enrichment_background",
    )
    help_output = run("-m", "bioskills", "--help").stdout
    for name in names:
        assert name in help_output
        run("-m", "bioskills", name, "--help")
    run("examples/expanded/run.py", "--output", "first-use")
    assert (extracted / "first-use/pseudobulk.csv").is_file()
    assert (extracted / "first-use/results.json").is_file()
    assert (extracted / "first-use/analysis_run.json").is_file()
    evidence = json.loads((extracted / "first-use/analysis_run.json").read_bytes())
    schema = json.loads((extracted / "schemas/analysis_run.schema.json").read_bytes())
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        evidence
    )
    assert evidence["exit_status"] == 0
    assert evidence["git_revision"] is None
    for item in evidence["inputs"] + evidence["outputs"]:
        path = Path(item["path"])
        assert hashlib.sha256((extracted / path).read_bytes()).hexdigest() == item["sha256"]
        assert not (extracted / path).resolve().is_relative_to(ROOT / "src")
    result = json.loads((extracted / "first-use/results.json").read_bytes())
    assert result["synthetic"] is True
    assert len(result["ora"]["results"]) == 2
    config = extracted / "counts-config.json"
    config.write_text(
        json.dumps(
            {
                "scale": "raw_counts",
                "organism": "synthetic",
                "reference": "v1",
                "count_generation": "Poisson seed731",
            }
        )
    )
    run(
        "-m",
        "bioskills",
        "check_counts",
        "--input",
        "first-use/pseudobulk.csv",
        "--config",
        str(config),
        "--output",
        "count-check.json",
    )
    report_schema = json.loads((extracted / "schemas/validator_report.schema.json").read_bytes())
    report = json.loads((extracted / "count-check.json").read_bytes())
    jsonschema.validate(report, report_schema)
    assert report["status"] == "PASS"
    config.write_text(
        json.dumps(
            {
                "scale": "TPM",
                "organism": "synthetic",
                "reference": "v1",
                "count_generation": "scientifically invalid declared input",
            }
        )
    )
    run(
        "-m",
        "bioskills",
        "check_counts",
        "--input",
        "first-use/pseudobulk.csv",
        "--config",
        str(config),
        "--output",
        "invalid-check.json",
        code=2,
    )
    invalid = json.loads((extracted / "invalid-check.json").read_bytes())
    jsonschema.validate(invalid, report_schema)
    assert invalid["status"] == "FAIL"
    for script, args in (
        ("examples/bulk-rnaseq/run.py", ["--output", "bulk-output"]),
        ("examples/multiomics/run.py", ["--output", "multiomics-output"]),
        ("examples/domain-recipes/run.py", ["multiomics", "--output", "cross-view-output"]),
        ("examples/public-metadata/run.py", ["geo", "GSE12345", "--output", "metadata-plan.json"]),
    ):
        run(script, *args)
    for name in ("run.R", "test.R", "install.R", "environment.json"):
        assert (extracted / "recipes/rnaseq" / name).is_file()
    dependencies = (extracted / "requirements-toolkit.txt").read_text()
    assert "cobra==0.29.1" in dependencies
    assert "R 4.4.3" in (extracted / "TOOLKIT_INSTALL.md").read_text()


def test_binary_resources_preserve_every_byte(packager, collection):
    content = b"\x89PNG\r\n\x1a\n\x00\xff\xfe\r\n"
    path = collection / ".agents/skills/first-skill/references/diagram.png"
    path.write_bytes(content)
    files = packager.package_files(collection)
    assert files[path.relative_to(collection).as_posix()] == content
    packager.validate_archive(packager.archive_bytes(files), files)


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "/absolute",
        "C:/drive",
        "a\\b",
        "a//b",
        "a/./b",
        "a/../b",
        "CON.txt",
        "a/LPT1",
        "a/trailing.",
        "a/trailing ",
        "a/file:stream",
        "a/\x00bad",
        "a/.env",
        "a/credentials.json",
        "a/private.key",
    ],
)
def test_unsafe_and_credential_paths_rejected_before_extraction(packager, name):
    with pytest.raises(ValueError):
        packager.archive_bytes({name: b"data"})
    with pytest.raises(ValueError):
        packager.validate_archive(b"not yet a zip", {name: b"data"})


@pytest.mark.parametrize(
    "body",
    [b"-----BEGIN PRIVATE KEY-----", b"ghp_" + b"x" * 32, b"Authorization: Bearer " + b"x" * 32],
)
def test_credential_content_rejected_without_echoing_it(packager, collection, body):
    (collection / "src/bioskills/example.py").write_bytes(body)
    with pytest.raises(ValueError, match="Credential-like source content") as failure:
        packager.package_files(collection)
    assert body.decode() not in str(failure.value)


def test_case_collisions_rejected(packager, collection):
    with pytest.raises(ValueError, match="collide"):
        packager.archive_bytes({"a.md": b"one", "A.md": b"two"})
    if os.name == "nt":
        return  # The dictionary above exercises this policy on case-insensitive systems.
    path = collection / ".agents/skills/first-skill/references/METHODS.md"
    path.write_text("Conflicting path")
    with pytest.raises(ValueError, match="collide"):
        packager.package_files(collection)


def test_symlink_resources_rejected(packager, collection):
    link = collection / ".agents/skills/first-skill/references/linked.md"
    try:
        link.symlink_to(collection / "LICENSE")
    except OSError:
        pytest.skip("Symlink creation is unavailable for this test account")
    with pytest.raises(ValueError, match="Linked"):
        packager.package_files(collection)


@pytest.mark.parametrize("name", ["Bioinformatics-Agent-Skills-Toolkit.zip", "unreviewed.ZIP"])
def test_only_one_archive_can_be_built_or_checked(packager, collection, monkeypatch, name):
    monkeypatch.setattr(packager, "ROOT", collection)
    assert packager.main([]) == 0
    assert {path.name for path in collection.glob("*.zip")} == {packager.ARCHIVE_NAME}
    assert len((collection / "SHA256SUMS").read_text().splitlines()) == 1
    (collection / name).write_bytes(b"unwanted")
    for arguments in ([], ["--check"]):
        with pytest.raises(SystemExit) as failure:
            packager.main(arguments)
        assert failure.value.code == 1


def test_documented_missing_executable_rejected(packager, collection):
    with (collection / "INSTALL.md").open("a") as stream:
        stream.write("Run `python examples/not-bundled.py`.\n")
    with pytest.raises(ValueError, match="Unbundled executable"):
        packager.package_files(collection)


@pytest.mark.parametrize(
    "name", ["src/bioskills/validators.py", "recipes/rnaseq/install.R", "examples/expanded/run.py"]
)
def test_missing_required_runtime_resource_rejected(packager, collection, name):
    (collection / name).unlink()
    with pytest.raises(ValueError, match="Missing required executable"):
        packager.package_files(collection)


@pytest.mark.parametrize(
    "name",
    [
        "examples/hidden.exe",
        "examples/nested.zip",
        "src/bioskills/.env",
        "recipes/rnaseq/credentials.json",
    ],
)
def test_unexpected_toolkit_resources_rejected(packager, collection, name):
    (collection / name).write_text("Unreviewed content")
    with pytest.raises(ValueError, match="Unexpected toolkit|Credential-like"):
        packager.package_files(collection)
