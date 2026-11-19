# Public bioinformatics data retrieval input contract

Source name, accession, page and explicit dry-run versus live metadata intent.

Python standard library; official public HTTP endpoints for live metadata.

Use the API documented in the full repository. Keep specimen, donor, assay,
reference and unit declarations explicit. Protect private metadata and never
infer unrecorded identity or provenance. Reject malformed or scientifically
incompatible inputs before downstream inference.

`bioskills.retrieval.retrieve_metadata(source, identifier, page=0, dry_run=True)`
accepts sources `geo`, `sra` or `ensembl`. GEO uses GSE accessions and SRA
uses public SRP/SRA/SRX/SRR accession syntax. Ensembl accepts stable gene IDs.
A nonnegative page selects twenty-record NCBI pages. Retain request provenance
and raw returned JSON. Fields unavailable from metadata remain unknown.
The function performs no sequencing or expression-file download.
