"""Valid and scientifically misleading fixtures for the new narrow capabilities."""

import gzip
import json

import numpy as np
import pandas as pd
import pytest

from bioskills.expanded import inspect_format, ora, pseudobulk
from bioskills.retrieval import metadata_plan, retrieve_metadata
from bioskills.science import ScientificValidationError


def test_pseudobulk_sums_and_replication():
    counts = pd.DataFrame([[1, 2, 3, 4, 5, 6, 7, 8]], columns=list("abcdefgh"), index=["g"])
    cells = pd.DataFrame(
        {
            "subject_id": np.repeat(list("ABCD"), 2),
            "specimen_id": np.repeat(list("abcd"), 2),
            "condition": ["c"] * 4 + ["t"] * 4,
            "timepoint": ["t0"] * 8,
            "batch": ["synthetic_batch"] * 8,
            "cell_type": ["x"] * 8,
        },
        index=counts.columns,
    )
    bulk, meta, audit = pseudobulk(
        counts, cells, organism="synthetic", reference="v1", count_generation="fixture"
    )
    assert bulk.iloc[0].tolist() == [3, 7, 11, 15]
    assert len(meta) == 4 and audit["differential_state"] == "NOT_RUN"
    assert set(meta.batch) == {"synthetic_batch"}
    assert audit["population_status"]["x"] == "READY_FOR_DESIGN_REVIEW"
    cells.subject_id = ["one"] * 8
    _, _, audit = pseudobulk(
        counts, cells, organism="synthetic", reference="v1", count_generation="fixture"
    )
    assert audit["population_status"]["x"] == "BLOCKED_POPULATION_INFERENCE"
    with pytest.raises(ScientificValidationError):
        pseudobulk(
            counts / 2, cells, organism="synthetic", reference="v1", count_generation="normalized"
        )
    with pytest.raises(ScientificValidationError):
        pseudobulk(
            counts,
            cells.iloc[::-1],
            organism="synthetic",
            reference="v1",
            count_generation="fixture",
        )


def enrichment_fixture():
    genes = [f"g{i}" for i in range(20)]
    return {
        "selected": genes[:5],
        "tested": genes,
        "mappings": [
            {"source": g, "target": g, "organism": "synthetic", "reference": "v1"} for g in genes
        ],
    }


def test_ora_known_fisher_result_and_bh_family():
    data = enrichment_fixture()
    result = ora(
        data,
        {"a": data["selected"], "b": data["tested"][10:]},
        organism="synthetic",
        reference="v1",
        database="synthetic",
        release="v1",
    )
    assert result["testing_family"] == 2
    hit = result["results"][0]
    assert hit["pvalue"] == pytest.approx(1 / 15504)
    assert hit["padj"] == pytest.approx(2 / 15504)
    assert result["results"][1]["pvalue"] == 1


@pytest.mark.parametrize("failure", ["background", "ambiguous", "species", "missing"])
def test_enrichment_rejects_invalid_science(failure):
    data = enrichment_fixture()
    if failure == "background":
        data["tested"] = data["selected"]
    elif failure == "ambiguous":
        data["mappings"][1]["target"] = "g0"
    elif failure == "species":
        data["mappings"][0]["organism"] = "other"
    else:
        data["selected"] = ["absent"]
    with pytest.raises(ScientificValidationError):
        ora(
            data,
            {"set": ["g0"]},
            organism="synthetic",
            reference="v1",
            database="synthetic",
            release="v1",
        )


@pytest.mark.parametrize(
    "text,format_",
    [
        ("@read\nACGT\n+\nIIII\n", "FASTQ"),
        (">sequence\nACGT\n", "FASTA"),
        ("chr1\t0\t10\n", "BED"),
        ("chr1\t0\t10\tpeak\t0\t+\t0\t10\t0\n", "BED"),
        ("chr1\tx\tgene\t1\t10\t.\t+\t.\tID=g1\n", "GTF_OR_GFF"),
        (
            "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t1\t.\tA\tC\t.\tPASS\t.\n",
            "VCF",
        ),
        (
            '<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" level="3" version="1"/>',
            "SBML",
        ),
        ("gene,a,b\ng1,1,2\ng2,3,4\n", "NUMERIC_TABLE"),
    ],
)
def test_format_content_inspection(tmp_path, text, format_):
    path = tmp_path / "unrelated.extension"
    path.write_text(text)
    assert inspect_format(path)["format"] == format_


def test_invalid_fastq_and_build_blocked(tmp_path):
    file = tmp_path / "file.fastq"
    file.write_text("@read\nACGT\n+\nI\n")
    with pytest.raises(ScientificValidationError):
        inspect_format(file)
    file.write_text(">sequence\nACGT\n")
    with pytest.raises(ScientificValidationError):
        inspect_format(file, reference="one", expected_reference="other")
    zipped = tmp_path / "file.gz"
    with gzip.open(zipped, "wb") as stream:
        stream.write(b"@read\nACGT\n+\nIIII\n")
    assert inspect_format(zipped)["compression"] == "gzip"


def test_metadata_dry_run_and_bounded_pagination():
    calls = []

    def transport(url):
        calls.append(url)
        return (
            json.dumps(
                {
                    "esearchresult": {
                        "idlist": [str(x) for x in range(123, 143)],
                        "count": "25",
                        "retstart": "0",
                        "retmax": "20",
                    }
                }
            ).encode()
            if "esearch" in url
            else json.dumps(
                {
                    "result": {
                        "uids": [str(x) for x in range(123, 143)],
                        **{str(x): {"uid": str(x), "accession": "GSE123"} for x in range(123, 143)},
                    }
                }
            ).encode()
        )

    assert retrieve_metadata("geo", "GSE123")["download_status"] == "NOT_RUN"
    result = retrieve_metadata(
        "geo", "GSE123", dry_run=False, transport=transport, pause=lambda n: None
    )
    assert len(calls) == 2 and result["has_next_page"]
    assert result["download_status"] == "METADATA_RETRIEVED"
    assert all(row["sha256"] for row in result["requests"])
    assert "retstart=20" in metadata_plan("sra", "SRP123", page=1)["url"]
    assert "lookup/id/ENSG00000141510" in metadata_plan("ensembl", "ENSG00000141510")["url"]
    with pytest.raises(ScientificValidationError):
        metadata_plan("sra", "controlled-secret")
    assert (
        retrieve_metadata(
            "geo", "GSE123", dry_run=False, transport=lambda url: b"{}", pause=lambda n: None
        )["download_status"]
        == "MALFORMED_RESPONSE"
    )
