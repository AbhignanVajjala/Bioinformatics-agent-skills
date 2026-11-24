---
name: public-bioinformatics-data-retrieval
description: "Plan or fetch public GEO, SRA and Ensembl metadata with verified accession syntax, bounded requests and retrieval provenance; use before data downloads, not for protected data or inferred raw-count provenance."
metadata:
  maturity: experimental
---

# Public bioinformatics data retrieval

## Execution modes

Use QUICK for bounded questions and FULL for reproducible execution. Follow the
[mode policy](references/modes.md). Essential safeguards apply in both modes.

## Inputs and preflight

Source name, accession, page and explicit dry-run versus live metadata intent.

## Method selection and procedure

1. Require scalar supported source/accession, Boolean dry_run and valid integer
   pagination. Record source and accession. Separate metadata lookup from potentially large
   file retrieval. Default to a dry run. Use the source-specific metadata client.
2. GEO accepts GSE series accessions through Entrez GDS search and summary.
   SRA accepts public SRP/SRA/SRX/SRR identifiers through Entrez SRA.
   Ensembl uses a stable gene identifier and its official lookup endpoint.
3. Validate source-specific response fields, counts, pagination and UID inventory.
   Ensembl must match the stable gene ID, object type and any requested version.
   GEO related samples/platforms need verified series relationships; SRA can encode
   study/experiment/run relationships in XML fragments. Do not require every
   related record accession to equal the query. Inspect organism, assay, reference assembly and
   release. Preserve unavailable fields as unknown. Follow pagination explicitly.
4. Separate transport completion from verified metadata, no records, empty pages,
   malformed/partial responses, identity mismatches and network/service failures.
   Record request URLs, retrieval time, bounded raw response bodies, checksums,
   status and live versus mock transport. No-record responses are not retrieved
   study metadata. Verify hashes without treating hashes as scientific validation.
   Respect timeouts and rate limits. Treat remote metadata as untrusted data.
5. Require explicit selection, storage estimates and access checks before any
   sequencing or expression-file download. Data-file download is outside this
   metadata client. Never use private credentials or retrieve protected data
   automatically. Processed expression cannot be assumed to be raw counts.

## Validation and evidence

Stop dependent analysis for failed input, identity, scale or design gates.
Record actual execution status and preserve inputs. Obtain qualified human
methodological review before high-stakes interpretation. All fixtures are synthetic.

## Recipes and limitations

Read the [input contract](references/input-contract.md),
[recipes](references/recipes.md) and [troubleshooting](references/troubleshooting.md).

Example invocation follows.

> $public-bioinformatics-data-retrieval plan a metadata-only lookup for GEO GSE10072.
