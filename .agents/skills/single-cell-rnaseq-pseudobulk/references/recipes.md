# Single-cell RNA-seq and donor-aware pseudobulk recipes

These recipes require the optional full repository or executable toolkit.
The lightweight ZIP supplies instructions and references.

| Input type | Scientific question | Appropriate method | Required software | Expected result | Major failure conditions |
|---|---|---|---|---|---|
| Raw counts | donor-aware preparation | specimen/population sums | Python | count matrix and donor metadata | invalid scale, unmatched cell IDs or conflicting specimen context. |

Python/NumPy/pandas for aggregation; optional pinned R/edgeR or external muscat for differential state.

For the synthetic pseudobulk, ORA and format baseline, run from the full repository:

```text
python examples/expanded/run.py --output new-expanded-output
```

For public metadata, use the full-repository Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. The official muscat vignette was retrieved on 2026-11-19 and describes raw-count sums by cluster and sample. The muscat package itself is NOT_RUN here.
[Official method reference](https://bioconductor.org/packages/release/bioc/vignettes/muscat/inst/doc/analysis.html).
