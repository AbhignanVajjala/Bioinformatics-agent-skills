"""Public metadata requests with explicit source identity and bounded responses."""

from datetime import datetime, timezone
import hashlib
import json
import re
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bioskills.science import require


def metadata_plan(source, identifier, *, page=0):
    require(type(page) is int and page >= 0, "pagination", "Nonnegative page required.")
    if source == "geo":
        require(
            bool(re.fullmatch(r"GSE[0-9]+", identifier)),
            "accession",
            "GEO series accession required.",
        )
        database = "gds"
    elif source == "sra":
        require(
            bool(re.fullmatch(r"SR[APRX][0-9]+", identifier)),
            "accession",
            "Public SRA accession required.",
        )
        database = "sra"
    elif source == "ensembl":
        require(
            bool(re.fullmatch(r"ENS[A-Z]*G[0-9]{11}(?:\.[0-9]+)?", identifier)),
            "accession",
            "Ensembl stable gene identifier required.",
        )
        require(page == 0, "pagination", "Single Ensembl lookup has no pages.")
        return {
            "source": source,
            "identifier": identifier,
            "page": page,
            "url": "https://rest.ensembl.org/lookup/id/"
            + identifier
            + "?content-type=application/json",
            "download_status": "NOT_RUN",
            "scope": "public metadata only",
        }
    else:
        raise ValueError("Unsupported public source")
    query = urlencode(
        {
            "db": database,
            "term": identifier + "[ACCN]",
            "retmode": "json",
            "retstart": page * 20,
            "retmax": 20,
        }
    )
    return {
        "source": source,
        "identifier": identifier,
        "page": page,
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + query,
        "download_status": "NOT_RUN",
        "scope": "public metadata only",
    }


def public_json(url):
    """Fetch one bounded JSON response, with a single rate-limit retry."""
    request = Request(
        url, headers={"User-Agent": "BioinformaticsAgentSkills/0.2", "Accept": "application/json"}
    )
    for attempt in range(2):
        try:
            with urlopen(request, timeout=15) as response:
                raw = response.read(1024 * 1024 + 1)
            require(len(raw) <= 1024 * 1024, "response_size", "Metadata exceeds the 1 MiB limit.")
            json.loads(raw)
            return raw
        except HTTPError as error:
            if error.code != 429 or attempt:
                raise
            delay = error.headers.get("Retry-After", "1")
            time.sleep(min(max(float(delay), 0.34), 5))
    raise AssertionError("Unreachable request state")


def retrieve_metadata(
    source, identifier, *, page=0, dry_run=True, transport=public_json, pause=time.sleep
):
    plan = metadata_plan(source, identifier, page=page)
    if dry_run:
        return plan
    urls = [plan["url"]]
    raw = transport(urls[0])
    data = json.loads(raw)
    records = [{"url": urls[0], "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}]
    if source in {"geo", "sra"}:
        search = data["esearchresult"]
        ids = search["idlist"]
        require(
            isinstance(ids, list) and all(isinstance(i, str) and i.isdigit() for i in ids),
            "metadata",
            "Malformed public metadata identifiers.",
        )
        if ids:
            pause(0.34)  # Keep this two-request example below NCBI's unauthenticated rate limit.
            query = urlencode(
                {"db": "gds" if source == "geo" else "sra", "id": ",".join(ids), "retmode": "json"}
            )
            urls.append("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + query)
            summary = transport(urls[-1])
            data["summary"] = json.loads(summary)
            records.append(
                {
                    "url": urls[-1],
                    "bytes": len(summary),
                    "sha256": hashlib.sha256(summary).hexdigest(),
                }
            )
        total = int(search["count"])
        plan["has_next_page"] = (page + 1) * 20 < total
    return {
        **plan,
        "download_status": "METADATA_RETRIEVED",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "requests": records,
        "metadata": data,
        "limitations": [
            "Only metadata retrieved; no expression matrix or sequencing file downloaded",
            "Inspect organism, assay, relationships, reference and release before analysis",
            "Processed expression values cannot be assumed to be raw counts",
            "Controlled-access data and credentialed downloads are outside this implementation",
        ],
    }
