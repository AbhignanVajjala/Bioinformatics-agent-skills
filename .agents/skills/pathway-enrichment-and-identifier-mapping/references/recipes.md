# Pathway enrichment and gene identifier mapping recipes

The universal ZIP includes these executable recipes and shared resources.
Keep the entire extraction and install the documented toolkit dependencies.
Copying only .agents/skills supplies instructions without executable dependencies.

| Input type | Scientific question | Appropriate method | Required software | Expected result | Major failure conditions |
|---|---|---|---|---|---|
| Eligible selected/tested genes | over-representation | one-sided Fisher plus BH | SciPy | overlap/p-value/FDR table | biased universe, ambiguous mapping or missing multiplicity policy. |

Python, pandas and SciPy 1.15.3 Fisher exact/BH functions.

For the synthetic pseudobulk, ORA and format baseline, run from the repository or complete universal extraction:

```text
python examples/expanded/run.py --output new-expanded-output
```

For public metadata, use the bundled Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. SciPy 1.15.3 Fisher exact and false_discovery_control API pages were retrieved on 2026-11-19. The implementation includes a known-result Fisher/BH synthetic regression. Ranked enrichment is NOT_RUN.
[Official method reference](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.fisher_exact.html).
