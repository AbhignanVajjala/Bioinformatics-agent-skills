"""Offline lineage contracts; native R checks execute in the pinned R CI job."""

import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pandas as pd
import pytest

from bioskills.expanded import inspect_format, ora, pseudobulk
from bioskills.retrieval import retrieve_metadata
from bioskills.science import validate_counts
from bioskills.validators import read_table


def fixture_files(tmp_path):
    cells = pd.DataFrame(
        {
            "subject_id": ["0001", "1", "d3", "d4"],
            "specimen_id": ["s1", "s2", "s3", "s4"],
            "condition": ["control", "control", "treated", "treated"],
            "timepoint": ["baseline"] * 4,
            "cell_type": ["T"] * 4,
            "batch": ["one"] * 4,
        },
        index=["0001", "1", "c3", "c4"],
    )
    counts = pd.DataFrame(
        np.arange(80).reshape(20, 4) % 11 + 20,
        index=["0001", "1"] + [f"g{i}" for i in range(18)],
        columns=cells.index,
    )
    bulk, metadata, audit = pseudobulk(
        counts, cells, organism="synthetic", reference="v1", count_generation="fixture"
    )
    file = tmp_path / "counts.tsv"
    meta = tmp_path / "samples.tsv"
    bulk.to_csv(file, sep="\t", index_label="gene_id")
    metadata.to_csv(meta, sep="\t")
    return file, meta, audit


def test_pseudobulk_to_bulk_and_format_contract(tmp_path):
    file, meta, audit = fixture_files(tmp_path)
    parsed = read_table(file)
    assert list(parsed.index)[:2] == ["0001", "1"]
    assert (
        validate_counts(
            parsed, read_table(meta), scale="raw_counts", organism="synthetic", reference="v1"
        )["status"]
        == "PASS"
    )
    assert inspect_format(file, format_hint="numeric_table")["details"]["row_ids"] == list(
        parsed.index
    )
    assert audit["differential_state"] == "NOT_RUN"


def test_native_R_input_contract(tmp_path):
    if os.environ.get("BIOSKILLS_NATIVE_R_TESTS") != "1":
        pytest.skip("Native R contract is explicitly enabled in the pinned R job")
    executable = shutil.which("Rscript")
    assert executable is not None, "Pinned native R job requires Rscript"
    file, meta, _ = fixture_files(tmp_path)
    code = 'source("recipes/rnaseq/validation.R"); a<-commandArgs(trailingOnly=TRUE); x<-read_tsv_exact(a[1]); m<-read_tsv_exact(a[2]); stopifnot(identical(x[[1]][1:2],c("0001","1")),identical(names(x)[-1],m$sample_id)); count_matrix(x); cat("PASS: native exact-ID count import")'
    completed = subprocess.run(
        [executable, "-e", code, str(file), str(meta)], capture_output=True, text=True, timeout=60
    )
    assert completed.returncode == 0, completed.stderr
    assert "PASS: native exact-ID count import" in completed.stdout


def test_native_DE_output_to_enrichment():
    folder = Path("artifacts/rnaseq-phase7/deseq2-identity")
    file = folder / "output/results.tsv"
    if not file.is_file():
        assert os.environ.get("BIOSKILLS_NATIVE_R_TESTS") != "1", "Native DE output missing"
        pytest.skip("Real native DE evidence is produced in the separate pinned R job")
    before = file.read_bytes()
    result = read_table(file)
    assert list(result.index)[:5] == ["0001", "1", "0002", "0003", "123456789012345678901234567890"]
    adjusted = pd.to_numeric(result.padj.replace("NA", None), errors="raise")
    selected = result.index[adjusted < 0.05].tolist()
    tested = result.index.tolist()
    config = json.loads((folder / "config.json").read_bytes())
    data = {
        "selected": selected,
        "tested": tested,
        "mappings": [
            {
                "source": g,
                "target": g,
                "organism": config["organism"],
                "reference": config["reference"],
            }
            for g in tested
        ],
    }
    report = ora(
        data,
        {"synthetic_first_five": tested[:5], "synthetic_last_five": tested[-5:]},
        organism=config["organism"],
        reference=config["reference"],
        database="synthetic_roundtrip_control",
        release="v1",
    )
    assert report["analysis_status"] == "EXECUTED"
    assert report["results"][0]["overlap"] == len(set(tested[:5]) & set(selected))
    assert file.read_bytes() == before


def test_verified_mock_identity_in_downstream_provenance():
    response = (
        b'{"id":"ENSG00000141510","object_type":"Gene","species":"homo_sapiens","version":21}'
    )
    report = retrieve_metadata(
        "ensembl",
        "ENSG00000141510",
        dry_run=False,
        transport=lambda url: response,
        transport_kind="mock",
    )
    provenance = {
        "identifier": report["relationship_evidence"][0]["stable_id"],
        "transport_kind": report["transport_kind"],
        "response_sha256": report["requests"][0]["sha256"],
        "scope": report["validation_status"],
    }
    assert provenance["identifier"] == "ENSG00000141510" and provenance["transport_kind"] == "mock"
    assert (
        provenance["response_sha256"]
        == hashlib.sha256(base64.b64decode(report["requests"][0]["body_base64"])).hexdigest()
    )


def test_invalid_metadata_cannot_supply_verified_downstream_identity():
    report = retrieve_metadata(
        "ensembl",
        "ENSG00000141510",
        dry_run=False,
        transport=lambda url: b'{"error":"bad ID"}',
        transport_kind="mock",
    )
    assert report["validation_status"] == "FAIL" and report["relationship_evidence"] == []
