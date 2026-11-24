# Public metadata input, response and provenance contract

`bioskills.retrieval.retrieve_metadata(source, identifier, page=0, dry_run=True)`
requires scalar supported source (geo/sra/ensembl), string accession, genuine
Boolean dry_run and nonnegative integer page (not Boolean). GEO uses GSE, SRA
public SRP/SRA/SRX/SRR syntax. NCBI pages have 20 records; Ensembl pagination is
unsupported. Ensembl gene IDs may specify a positive version: lookup uses the
base stable ID and validates the returned current version against the request.
Dry runs make no network call and retain NOT_RUN execution status.

Live requests use official public HTTPS endpoints, 15-second timeouts, <=1 MiB
responses, at most one bounded HTTP 429 retry, and a 0.34-second search-summary
pause. Retry-After supports seconds and HTTP dates, clamped to 0.34–5 seconds;
malformed/nonfinite values use a bounded fallback. No private credentials or raw datasets.
Custom transports must be callable; transport_kind explicitly identifies mocks.

Validate response structures and API error objects. Ensembl requires requested
stable ID, Gene object type, nonblank species and positive integer version.
NCBI requires nonnegative count/start/size, requested pagination, unique returned
UIDs and complete summary UID inventory matching the requested IDs. Verify each
GEO series/related-record relationship using accession, gse membership or explicit
series sample/platform links. SRA study/experiment/run/submitter relationships
are parsed from bounded XML fragments. Related accessions need not equal the query.
Missing relationship evidence is PARTIAL_UNVERIFIED; contradictions fail identity.

Statuses: NOT_RUN, METADATA_RETRIEVED (VERIFIED_SCOPE), NO_MATCHING_RECORDS,
EMPTY_PAGE, PARTIAL_UNVERIFIED, MALFORMED_RESPONSE, IDENTITY_MISMATCH,
SERVICE_ERROR and NETWORK_ERROR. Transport status is separate. Verified scope
means only the implemented fields/page/relationships, not complete annotation
correctness or assay provenance. Zero records is not retrieved study metadata.

Preserve retrieval time, request URLs, HTTP status/attempts when observable,
transport type, source hashes, byte counts, raw response base64 and SHA-256.
Decode and independently hash bounded bodies to verify evidence. A mock response
can pass schema/identity checks without demonstrating live retrieval. The schema
and template describe evidence structure, never certify truth. Unavailable
organism/assembly/release/measurement metadata stays unknown; dependent scientific
gates must still pass. No sequencing or expression-file download is performed.
