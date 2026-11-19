# Bioinformatics file formats and provenance recipes

These recipes require the optional full repository or executable toolkit.
The lightweight ZIP supplies instructions and references.

| Input type | Scientific question | Appropriate method | Required software | Expected result | Major failure conditions |
|---|---|---|---|---|---|
| Bioinformatics file | compatibility triage | content records or signatures | Python/optional parser | scoped inspection report | malformed record, reference mismatch or unsupported binary parser. |

Python text/gzip/XML/pandas baseline; optional pysam/samtools or AnnData parsers.

For the synthetic pseudobulk, ORA and format baseline, run from the full repository:

```text
python examples/expanded/run.py --output new-expanded-output
```

For public metadata, use the full-repository Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. Use the official hts-specs for complex binary and coordinate-sensitive work. The baseline tests text records and signatures only. Optional binary parsing is NOT_RUN.
[Official method reference](https://samtools.github.io/hts-specs/).
