"""Bounded public metadata with explicit transport, schema and relationship evidence."""

import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import math
from pathlib import Path
import platform
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from bioskills.inputs import require_text, strict_json
from bioskills.science import ScientificValidationError, require

RESPONSE_LIMIT = 1024 * 1024


class ResponseValidationError(ScientificValidationError):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def response_require(condition, status, message):
    if not condition:
        raise ResponseValidationError(status, message)


def metadata_plan(source, identifier, *, page=0):
    require(
        isinstance(source, str) and source in {"geo", "sra", "ensembl"},
        "source",
        "Supported scalar source geo/sra/ensembl required.",
    )
    require_text(identifier, "accession")
    require(type(page) is int and page >= 0, "pagination", "Nonnegative integer page required.")
    result = {
        "source": source,
        "identifier": identifier,
        "page": page,
        "download_status": "NOT_RUN",
        "scope": "public metadata only",
    }
    if source == "ensembl":
        match = re.fullmatch(r"(ENS[A-Z]*G[0-9]{11})(?:\.([1-9][0-9]*))?", identifier)
        require(bool(match), "accession", "Ensembl stable gene identifier required.")
        require(page == 0, "pagination", "Single Ensembl lookup has no pages.")
        result.update(
            stable_id=match[1],
            requested_version=int(match[2]) if match[2] else None,
            url="https://rest.ensembl.org/lookup/id/" + match[1] + "?content-type=application/json",
        )
    else:
        pattern = r"GSE[0-9]+" if source == "geo" else r"SR[APRX][0-9]+"
        require(
            bool(re.fullmatch(pattern, identifier)),
            "accession",
            "Unsupported accession for this source.",
        )
        result["url"] = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urlencode(
            {
                "db": "gds" if source == "geo" else "sra",
                "term": identifier + "[ACCN]",
                "retmode": "json",
                "retstart": page * 20,
                "retmax": 20,
            }
        )
    return result


def retry_delay(value):
    try:
        delay = float(value)
    except (ValueError, TypeError):
        try:
            timestamp = parsedate_to_datetime(value)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            delay = (timestamp - datetime.now(timezone.utc)).total_seconds()
        except (ValueError, TypeError, OverflowError):
            delay = 1.0
    if not math.isfinite(delay):
        delay = 1.0
    return min(max(delay, 0.34), 5.0)


class HTTPPayload(bytes):
    """Bytes-compatible payload carrying observed minimal HTTP metadata."""


def public_json(url):
    require(
        urlsplit(url).scheme == "https"
        and urlsplit(url).hostname in {"eutils.ncbi.nlm.nih.gov", "rest.ensembl.org"},
        "endpoint",
        "Only supported public HTTPS metadata hosts allowed.",
    )
    request = Request(
        url, headers={"User-Agent": "BioinformaticsAgentSkills/0.2", "Accept": "application/json"}
    )
    for attempt in range(2):
        try:
            with urlopen(request, timeout=15) as response:
                raw = response.read(RESPONSE_LIMIT + 1)
                status = response.getcode()
                content_type = response.headers.get("Content-Type")
            require(len(raw) <= RESPONSE_LIMIT, "response_size", "Metadata exceeds 1 MiB.")
            payload = HTTPPayload(raw)
            payload.http_status = status
            payload.content_type = content_type
            payload.attempts = attempt + 1
            return payload
        except HTTPError as error:
            if error.code != 429 or attempt:
                error.attempts = attempt + 1
                raise
            time.sleep(retry_delay(error.headers.get("Retry-After", "1")))


def _integer(value, field):
    valid = type(value) is int or (isinstance(value, str) and bool(re.fullmatch(r"[0-9]+", value)))
    response_require(valid, "MALFORMED_RESPONSE", f"{field}: nonnegative integer required.")
    number = int(value)
    response_require(number >= 0, "MALFORMED_RESPONSE", f"{field}: negative count.")
    return number


def _object(data):
    response_require(isinstance(data, dict), "MALFORMED_RESPONSE", "JSON object response required.")
    response_require(
        not any(key in data for key in ["error", "ERROR", "errorlist"]),
        "SERVICE_ERROR",
        "Provider returned an API error object.",
    )


def _uids(value):
    response_require(
        isinstance(value, list)
        and all(isinstance(x, str) and re.fullmatch(r"[1-9][0-9]*", x) for x in value)
        and len(value) == len(set(value)),
        "MALFORMED_RESPONSE",
        "Unique positive UID strings required.",
    )
    return value


def _geo_members(value, prefix):
    if value in (None, ""):
        return set()
    items = (
        value
        if isinstance(value, list)
        else re.split(r"[;,\s]+", value)
        if isinstance(value, str)
        else [value]
    )
    result = set()
    for item in items:
        if type(item) is int and item >= 0:
            item = str(item)
        response_require(
            isinstance(item, str) and bool(re.fullmatch(r"(?:" + prefix + r")?[0-9]+", item)),
            "MALFORMED_RESPONSE",
            "Malformed GEO accession relationship.",
        )
        result.add(item if item.startswith(prefix) else prefix + item)
    return result


def _sra_relationship(row, identifier):
    targets = {
        "SRP": {"Study"},
        "SRX": {"Experiment"},
        "SRR": {"Run"},
        "SRA": {"Submitter", "Submission"},
    }
    requested_tags = targets[identifier[:3]]
    candidates = []
    for field in ("expxml", "runs"):
        fragment = row.get(field, "")
        response_require(
            isinstance(fragment, str), "MALFORMED_RESPONSE", "SRA XML fragment must be text."
        )
        if not fragment:
            continue
        response_require(
            "<!DOCTYPE" not in fragment.upper() and "<!ENTITY" not in fragment.upper(),
            "MALFORMED_RESPONSE",
            "SRA DTD/entities unsupported.",
        )
        try:
            tree = ET.fromstring("<metadata>" + fragment + "</metadata>")
        except ET.ParseError as error:
            raise ResponseValidationError(
                "MALFORMED_RESPONSE", "Malformed SRA XML fragment."
            ) from error
        for node in tree.iter():
            if node.tag.split("}")[-1] in requested_tags:
                accession = node.get("acc", node.get("accession"))
                if accession:
                    candidates.append(accession)
    if identifier in candidates:
        return "VERIFIED", "SRA_TYPED_XML_RELATIONSHIP"
    return (
        "IDENTITY_MISMATCH" if candidates else "UNVERIFIED"
    ), "SRA_REQUESTED_RELATIONSHIP_NOT_VERIFIED"


def _summaries(source, identifier, data, ids, evidence):
    _object(data)
    result = data.get("result")
    _object(result)
    response_require("uids" in result, "PARTIAL_UNVERIFIED", "Summary UID inventory missing.")
    returned = _uids(result["uids"])
    response_require(
        set(returned) <= set(ids), "IDENTITY_MISMATCH", "Summary includes unrequested UIDs."
    )
    response_require(
        set(returned) == set(ids), "PARTIAL_UNVERIFIED", "Requested summaries incomplete."
    )
    platforms, samples = set(), set()
    for uid in returned:
        response_require(
            uid in result and isinstance(result[uid], dict),
            "PARTIAL_UNVERIFIED",
            "Missing UID summary.",
        )
        row = result[uid]
        _object(row)
        response_require("uid" in row, "MALFORMED_RESPONSE", "Required summary UID missing.")
        response_require(
            row.get("uid") == uid, "IDENTITY_MISMATCH", "Summary UID differs from requested UID."
        )
        if source == "geo" and row.get("accession") == identifier:
            platforms |= _geo_members(row.get("gpl"), "GPL")
            sample_records = row.get("samples", [])
            response_require(
                isinstance(sample_records, list),
                "MALFORMED_RESPONSE",
                "Malformed GEO sample inventory.",
            )
            for sample in sample_records:
                response_require(
                    isinstance(sample, dict) and isinstance(sample.get("accession"), str),
                    "MALFORMED_RESPONSE",
                    "Malformed GEO sample relationship.",
                )
                samples.add(sample["accession"])
    for uid in returned:
        row = result[uid]
        if source == "sra":
            state, relationship = _sra_relationship(row, identifier)
        else:
            accession = row.get("accession")
            response_require(
                isinstance(accession, str)
                and bool(re.fullmatch(r"G(?:SE|SM|PL|DS)[0-9]+", accession)),
                "MALFORMED_RESPONSE",
                "Valid GEO record accession required.",
            )
            if accession == identifier:
                state, relationship = "VERIFIED", "DIRECT_GEO_SERIES"
            elif identifier in _geo_members(row.get("gse"), "GSE"):
                state, relationship = "VERIFIED", "GEO_SERIES_MEMBERSHIP"
            elif accession in platforms | samples:
                state, relationship = "VERIFIED", "GEO_SERIES_EXPLICIT_LINK"
            else:
                state = "IDENTITY_MISMATCH" if accession.startswith("GSE") else "UNVERIFIED"
                relationship = "GEO_RELATIONSHIP_NOT_VERIFIED"
        evidence.append({"uid": uid, "state": state, "relationship": relationship})
    response_require(
        not any(row["state"] == "IDENTITY_MISMATCH" for row in evidence),
        "IDENTITY_MISMATCH",
        "Returned metadata contradicts the requested accession relationship.",
    )
    response_require(
        all(row["state"] == "VERIFIED" for row in evidence),
        "PARTIAL_UNVERIFIED",
        "Some related records lack verifiable accession relationships.",
    )
    return evidence


def retrieve_metadata(
    source,
    identifier,
    *,
    page=0,
    dry_run=True,
    transport=public_json,
    pause=time.sleep,
    transport_kind=None,
):
    require(type(dry_run) is bool, "dry_run", "dry_run must be Boolean.")
    require(
        transport_kind is None
        or (isinstance(transport_kind, str) and transport_kind in {"live", "mock", "custom"}),
        "transport",
        "Transport kind must be live/mock/custom.",
    )
    require(
        callable(transport) and callable(pause),
        "transport",
        "Callable transport and pause required.",
    )
    plan = metadata_plan(source, identifier, page=page)
    if dry_run:
        return {**plan, "transport_status": "NOT_RUN", "validation_status": "NOT_RUN"}
    kind = transport_kind or ("live" if transport is public_json else "custom")
    result = {
        **plan,
        "report_version": 2,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "transport_kind": kind,
        "transport_declaration": "builtin" if transport is public_json else "caller_supplied",
        "requests": [],
        "transport_status": "NOT_RUN",
        "validation_status": "NOT_RUN",
        "metadata": {},
        "relationship_evidence": [],
        "software": {"python": platform.python_version()},
        "source_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("retrieval.py", "inputs.py")
        },
        "limitations": [
            "Metadata/schema/relationship verification does not authenticate biology or every annotation",
            "Only public metadata; no raw sequencing, expression files, controlled data or credentials",
            "Custom/mock transport evidence does not demonstrate live retrieval",
            "A validated page is not a complete study, eligible count matrix or verified assay provenance",
        ],
    }

    active_url = plan["url"]

    def fetch(url):
        nonlocal active_url
        active_url = url
        raw = transport(url)
        response_require(
            isinstance(raw, bytes) and len(raw) <= RESPONSE_LIMIT,
            "MALFORMED_RESPONSE",
            "Bounded response bytes required.",
        )
        result["requests"].append(
            {
                "url": url,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "body_base64": base64.b64encode(raw).decode("ascii"),
                "http_status": getattr(raw, "http_status", None),
                "content_type": getattr(raw, "content_type", None),
                "attempts": getattr(raw, "attempts", None),
                "transport_kind": kind,
            }
        )
        result["transport_status"] = "COMPLETED"
        return strict_json(raw)

    try:
        data = fetch(plan["url"])
        result["metadata"] = data
        _object(data)
        if source == "ensembl":
            response_require(bool(data), "MALFORMED_RESPONSE", "Empty Ensembl object.")
            response_require(
                {"id", "object_type", "species", "version"} <= data.keys(),
                "MALFORMED_RESPONSE",
                "Required Ensembl fields missing.",
            )
            response_require(
                data.get("id") == plan["stable_id"] and data.get("object_type") == "Gene",
                "IDENTITY_MISMATCH",
                "Ensembl stable gene identity/type mismatch.",
            )
            response_require(
                isinstance(data.get("species"), str)
                and bool(data["species"].strip())
                and type(data.get("version")) is int
                and data["version"] > 0,
                "MALFORMED_RESPONSE",
                "Ensembl species and positive integer version required.",
            )
            response_require(
                plan["requested_version"] is None or data["version"] == plan["requested_version"],
                "IDENTITY_MISMATCH",
                "Ensembl requested version differs from current lookup version.",
            )
            result["relationship_evidence"] = [
                {
                    "state": "VERIFIED",
                    "relationship": "ENSEMBL_GENE_ID_TYPE_VERSION",
                    "stable_id": data["id"],
                    "returned_version": data["version"],
                }
            ]
        else:
            search = data.get("esearchresult")
            _object(search)
            response_require(
                {"idlist", "count", "retstart", "retmax"} <= search.keys(),
                "MALFORMED_RESPONSE",
                "Required search/pagination fields missing.",
            )
            ids = _uids(search["idlist"])
            total, start, size = (_integer(search[k], k) for k in ("count", "retstart", "retmax"))
            response_require(
                start == page * 20 and size <= 20 and len(ids) <= size,
                "MALFORMED_RESPONSE",
                "Search pagination is inconsistent with request.",
            )
            result.update(
                search_count=total, returned_uids=ids, has_next_page=(page + 1) * 20 < total
            )
            if not ids:
                response_require(
                    total == 0 or start >= total,
                    "PARTIAL_UNVERIFIED",
                    "Available search window has no returned records.",
                )
                result.update(
                    download_status="NO_MATCHING_RECORDS" if total == 0 else "EMPTY_PAGE",
                    validation_status="VALID_NO_RECORDS",
                )
                return result
            response_require(
                total >= start + len(ids), "MALFORMED_RESPONSE", "UID count exceeds declared total."
            )
            response_require(
                len(ids) == min(20, total - start),
                "PARTIAL_UNVERIFIED",
                "Search page is incomplete.",
            )
            pause(0.34)
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urlencode(
                {"db": "gds" if source == "geo" else "sra", "id": ",".join(ids), "retmode": "json"}
            )
            summary = fetch(url)
            data["summary"] = summary
            _summaries(source, identifier, summary, ids, result["relationship_evidence"])
        result.update(download_status="METADATA_RETRIEVED", validation_status="VERIFIED_SCOPE")
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        result["failed_request"] = {
            "url": active_url,
            "http_status": getattr(error, "code", None),
            "attempts": getattr(error, "attempts", None),
            "error_type": type(error).__name__,
        }
        result.update(
            download_status="NETWORK_ERROR",
            transport_status="PARTIAL" if result["requests"] else "FAILED",
            validation_status="UNVERIFIED",
            reason=type(error).__name__,
            http_status=getattr(error, "code", None),
        )
    except ScientificValidationError as error:
        result.update(
            download_status=getattr(error, "status", "MALFORMED_RESPONSE"),
            validation_status="FAIL",
            reason=str(error),
        )
    return result
