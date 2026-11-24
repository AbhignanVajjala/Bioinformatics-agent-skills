"""Offline provider-shaped metadata and transport failure controls; no live requests."""

import base64
from copy import deepcopy
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
import jsonschema

from bioskills.retrieval import (
    metadata_plan,
    retrieve_metadata,
    public_json,
    retry_delay,
    RESPONSE_LIMIT,
)
from bioskills.science import ScientificValidationError


GENE = "ENSG00000141510"


def gene():
    return {"id": GENE, "object_type": "Gene", "species": "homo_sapiens", "version": 21}


def fetch_gene(data, identifier=GENE):
    return retrieve_metadata(
        "ensembl",
        identifier,
        dry_run=False,
        transport=lambda url: json.dumps(data).encode(),
        transport_kind="mock",
    )


def ncbi(source="geo", ids=None, count=2, start=0):
    ids = ["101", "102"] if ids is None else ids
    search = {
        "esearchresult": {
            "count": str(count),
            "retstart": str(start),
            "retmax": str(len(ids)),
            "idlist": ids,
        }
    }
    rows = {
        uid: (
            {"uid": uid, "accession": "GSE10072"}
            if i == 0
            else {"uid": uid, "accession": "GSM200", "gse": "10072;999"}
        )
        for i, uid in enumerate(ids)
    }
    if source == "sra":
        rows = {
            uid: {
                "uid": uid,
                "expxml": '<Experiment acc="SRX000005"/><Study acc="SRP000001"/>',
                "runs": '<Run acc="SRR000003"/>',
            }
            for uid in ids
        }
    return search, {"result": {"uids": ids.copy(), **rows}}


def fetch_ncbi(search, summary, source="geo", identifier=None, page=0):
    return retrieve_metadata(
        source,
        identifier or ("GSE10072" if source == "geo" else "SRP000001"),
        page=page,
        dry_run=False,
        transport=lambda url: json.dumps(search if "esearch" in url else summary).encode(),
        pause=lambda seconds: None,
        transport_kind="mock",
    )


@pytest.mark.parametrize(
    "source,identifier",
    [
        (None, "GSE10072"),
        ("unknown", "GSE10072"),
        ([], "GSE10072"),
        ("geo", None),
        ("geo", 1),
        ("geo", " "),
    ],
)
def test_input_types(source, identifier):
    with pytest.raises(ScientificValidationError):
        metadata_plan(source, identifier)


@pytest.mark.parametrize("flag", ["false", 0, 1, None, []])
def test_execution_flag_cannot_trigger_or_skip_network(flag):
    def transport(url):
        raise AssertionError("must not execute")

    with pytest.raises(ScientificValidationError, match="dry_run"):
        retrieve_metadata("geo", "GSE10072", dry_run=flag, transport=transport)


def test_dry_run_and_pagination():
    def transport(url):
        raise AssertionError("must not execute")

    assert retrieve_metadata("geo", "GSE10072", transport=transport)["download_status"] == "NOT_RUN"
    for page in [-1, True, 1.5]:
        with pytest.raises(ScientificValidationError):
            metadata_plan("geo", "GSE10072", page=page)
    with pytest.raises(ScientificValidationError):
        metadata_plan("ensembl", GENE, page=1)


@pytest.mark.parametrize(
    "change,status",
    [
        ({"id": "ENSG00000157764"}, "IDENTITY_MISMATCH"),
        ({"object_type": "Transcript"}, "IDENTITY_MISMATCH"),
        ({"error": "unavailable"}, "SERVICE_ERROR"),
        ({"version": True}, "MALFORMED_RESPONSE"),
        ({"species": " "}, "MALFORMED_RESPONSE"),
    ],
)
def test_ensembl_integrity(change, status):
    data = gene()
    data.update(change)
    assert fetch_gene(data)["download_status"] == status


def test_ensembl_version_and_empty_object():
    result = fetch_gene(gene(), GENE + ".21")
    assert result["download_status"] == "METADATA_RETRIEVED" and result["transport_kind"] == "mock"
    assert ".21?" not in result["url"] and result["requested_version"] == 21
    assert fetch_gene(gene(), GENE + ".20")["download_status"] == "IDENTITY_MISMATCH"
    assert fetch_gene({})["download_status"] == "MALFORMED_RESPONSE"
    assert fetch_gene({"id": GENE})["download_status"] == "MALFORMED_RESPONSE"


@pytest.mark.parametrize(
    "failure,status",
    [
        ("negative", "MALFORMED_RESPONSE"),
        ("duplicate-ids", "MALFORMED_RESPONSE"),
        ("missing-field", "MALFORMED_RESPONSE"),
        ("wrong-offset", "MALFORMED_RESPONSE"),
        ("wrong-uid", "IDENTITY_MISMATCH"),
        ("unrequested-uid", "IDENTITY_MISMATCH"),
        ("missing-uid", "PARTIAL_UNVERIFIED"),
        ("wrong-accession", "IDENTITY_MISMATCH"),
        ("summary-error", "SERVICE_ERROR"),
    ],
)
def test_ncbi_integrity(failure, status):
    search, summary = ncbi()
    if failure == "negative":
        search["esearchresult"]["count"] = "-1"
    elif failure == "duplicate-ids":
        search["esearchresult"]["idlist"] = ["101", "101"]
    elif failure == "missing-field":
        del search["esearchresult"]["count"]
    elif failure == "wrong-offset":
        search["esearchresult"]["retstart"] = "20"
    elif failure == "wrong-uid":
        summary["result"]["101"]["uid"] = "999"
    elif failure == "unrequested-uid":
        summary["result"]["uids"] = ["999"]
    elif failure == "missing-uid":
        del summary["result"]["101"]
    elif failure == "wrong-accession":
        summary["result"]["101"]["accession"] = "GSE999"
    else:
        summary = {"error": "bad summary"}
    assert fetch_ncbi(search, summary)["download_status"] == status


def test_no_records_empty_page_and_incomplete_page():
    search, summary = ncbi(ids=[], count=0)
    assert fetch_ncbi(search, summary)["download_status"] == "NO_MATCHING_RECORDS"
    search, summary = ncbi(ids=[], count=1, start=20)
    assert fetch_ncbi(search, summary, page=1)["download_status"] == "EMPTY_PAGE"
    search, summary = ncbi(ids=["101"], count=25)
    assert fetch_ncbi(search, summary)["download_status"] == "PARTIAL_UNVERIFIED"


def test_legitimate_geo_related_accessions_and_raw_evidence():
    search, summary = ncbi()
    summary["result"]["101"]["gpl"] = "96"
    summary["result"]["102"] = {"uid": "102", "accession": "GPL96"}
    before = deepcopy((search, summary))
    result = fetch_ncbi(search, summary)
    assert result["download_status"] == "METADATA_RETRIEVED"
    assert {x["relationship"] for x in result["relationship_evidence"]} == {
        "DIRECT_GEO_SERIES",
        "GEO_SERIES_EXPLICIT_LINK",
    }
    for record in result["requests"]:
        raw = base64.b64decode(record["body_base64"])
        assert len(raw) == record["bytes"] and hashlib.sha256(raw).hexdigest() == record["sha256"]
    assert (search, summary) == before


@pytest.mark.parametrize("identifier", ["SRP000001", "SRX000005", "SRR000003"])
def test_sra_xml_relationships(identifier):
    search, summary = ncbi("sra")
    assert (
        fetch_ncbi(search, summary, source="sra", identifier=identifier)["download_status"]
        == "METADATA_RETRIEVED"
    )
    summary["result"]["101"]["expxml"] = '<Study acc="SRP999999"/>'
    if identifier.startswith("SRP"):
        assert (
            fetch_ncbi(search, summary, source="sra", identifier=identifier)["download_status"]
            == "IDENTITY_MISMATCH"
        )


def test_sra_malformed_xml_and_partial_relationship():
    search, summary = ncbi("sra")
    summary["result"]["101"]["expxml"] = "<Study"
    assert fetch_ncbi(search, summary, source="sra")["download_status"] == "MALFORMED_RESPONSE"
    summary["result"]["101"]["expxml"] = "<Summary/>"
    assert fetch_ncbi(search, summary, source="sra")["download_status"] == "PARTIAL_UNVERIFIED"


@pytest.mark.parametrize(
    "raw",
    [b"{}", b"{bad", b"not JSON", b'{"id":1,"id":2}', b"\xff", b"x" * (RESPONSE_LIMIT + 1)],
    ids=["empty-object", "bad-syntax", "text", "duplicate-key", "encoding", "over-limit"],
)
def test_malformed_bounded_responses(raw):
    result = retrieve_metadata(
        "ensembl", GENE, dry_run=False, transport=lambda url: raw, transport_kind="mock"
    )
    assert result["download_status"] == "MALFORMED_RESPONSE"


def test_network_failure_is_not_metadata_success():
    def transport(url):
        raise URLError("synthetic offline failure")

    result = retrieve_metadata("ensembl", GENE, dry_run=False, transport=transport)
    assert (
        result["download_status"] == "NETWORK_ERROR" and result["validation_status"] == "UNVERIFIED"
    )
    assert result["failed_request"]["url"] == result["url"]


@pytest.mark.parametrize(
    "header", ["not-a-number", "nan", "inf", "-100", "100", "Wed, 21 Oct 2015 07:28:00 GMT"]
)
def test_retry_after_is_bounded(header):
    assert math.isfinite(retry_delay(header)) and 0.34 <= retry_delay(header) <= 5


def test_actual_http_boundary_single_retry_and_size(monkeypatch):
    import bioskills.retrieval as module

    calls = []
    sleeps = []

    class Response:
        headers = {"Content-Type": "application/json"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, n):
            return b"{}"

        def getcode(self):
            return 200

    def urlopen(request, timeout):
        calls.append((request.full_url, timeout))
        if len(calls) == 1:
            raise HTTPError(
                request.full_url, 429, "limited", {"Retry-After": "garbage"}, io.BytesIO()
            )
        return Response()

    monkeypatch.setattr(module, "urlopen", urlopen)
    monkeypatch.setattr(module.time, "sleep", sleeps.append)
    raw = public_json(metadata_plan("ensembl", GENE)["url"])
    assert raw == b"{}" and raw.attempts == 2 and raw.http_status == 200
    assert len(calls) == 2 and all(timeout == 15 for _, timeout in calls) and len(sleeps) == 1
    monkeypatch.setattr(Response, "read", lambda self, n: b"x" * n)
    with pytest.raises(ScientificValidationError, match="response_size"):
        public_json(metadata_plan("ensembl", GENE)["url"])


def test_retrieval_schema_validates_observed_status_and_evidence():
    schema = json.loads(Path("schemas/metadata_retrieval.schema.json").read_bytes())
    report = fetch_gene(gene())
    jsonschema.validate(report, schema)
    jsonschema.validate(fetch_gene({"error": "synthetic"}), schema)
    jsonschema.validate(retrieve_metadata("geo", "GSE10072"), schema)
    report["relationship_evidence"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(report, schema)
    report["relationship_evidence"] = [{"state": "VERIFIED", "relationship": "synthetic"}]
    report["validation_status"] = "UNVERIFIED"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(report, schema)
