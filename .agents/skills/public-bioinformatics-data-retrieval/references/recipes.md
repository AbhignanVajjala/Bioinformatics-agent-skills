# Public bioinformatics data retrieval recipes

The universal ZIP includes these executable recipes and shared resources.
Keep the entire extraction and install the documented toolkit dependencies.
Copying only .agents/skills supplies instructions without executable dependencies.

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
For public metadata, use the bundled Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. NCBI E-utilities documentation encountered a browser verification page on 2026-11-19. Ensembl lookup documentation returned 403. Those earlier releases remain historically NOT_RUN. On 2026-11-24, three live requests were observed at source 98a9456132fb474996f4c5d566065925ed79551b. Phase 8 separately records new scoped live identity checks; see the maintainer review.
[Official method reference](https://www.ncbi.nlm.nih.gov/books/NBK25501/).
