# Bioinformatics file formats and provenance recipes

The universal ZIP includes these executable recipes and shared resources.
Keep the entire extraction and install the documented toolkit dependencies.
Copying only .agents/skills supplies instructions without executable dependencies.

| Input type | Scientific question | Appropriate method | Required software | Expected result | Major failure conditions |
|---|---|---|---|---|---|
| Bioinformatics file | compatibility triage | content records or signatures | Python/optional parser | scoped inspection report | malformed record, reference mismatch or unsupported binary parser. |

Python text/gzip/XML/pandas baseline; optional pysam/samtools or AnnData parsers.

For the synthetic pseudobulk, ORA and format baseline, run from the repository or complete universal extraction:

```text
python examples/expanded/run.py --output new-expanded-output
```

For public metadata, use the bundled Python API `bioskills.retrieval.retrieve_metadata`.
It defaults to `dry_run=True`. A manual live example is
`retrieve_metadata("geo", "GSE10072", dry_run=False)`. Inspect its returned
status and preserve the metadata before claiming retrieval. The regular tests
mock public endpoints and make no live requests.

Primary reference follows. Use the official hts-specs for complex binary and coordinate-sensitive work. The baseline tests text records and signatures only. Optional binary parsing is NOT_RUN.
[Official method reference](https://samtools.github.io/hts-specs/).
