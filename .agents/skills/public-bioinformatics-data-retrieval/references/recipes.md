# Public bioinformatics data retrieval recipes

These recipes require the optional full repository or executable toolkit.
The lightweight ZIP supplies instructions and references.

| Input type | Scientific question | Appropriate method | Required software | Expected result | Major failure conditions |
|---|---|---|---|---|---|
| Public accession | study discovery | source-specific lookup | Python urllib | metadata plus checksums | malformed identifiers, HTTP failure, controlled access or unverified data scale. |

Python standard library; official public HTTP endpoints for live metadata.

From the full repository, plan metadata retrieval with no network request:

```text
python examples/public-metadata/run.py geo GSE10072 --output geo-plan.json
```

Add `--live` to perform the bounded public metadata request. The other sources
accept `sra SRP000001` and `ensembl ENSG00000141510`, respectively.
For public metadata, use the full-repository Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. NCBI E-utilities documentation encountered a browser verification page on 2026-11-19. Ensembl lookup documentation returned 403. Endpoint procedures are implemented with offline mocks, and live retrieval remains NOT_RUN until a recorded request succeeds.
[Official method reference](https://www.ncbi.nlm.nih.gov/books/NBK25501/).
