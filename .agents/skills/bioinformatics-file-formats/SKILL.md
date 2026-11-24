---
name: bioinformatics-file-formats
description: "Inspect small bioinformatics text records and binary signatures with explicit parser and reference limits; use for FASTQ/FASTA/VCF/BED/GTF/GFF/tables/SBML triage, not extension-only certification or filename-derived sample identity."
metadata:
  maturity: experimental
---

# Bioinformatics file formats and provenance

## Execution modes

Use QUICK for bounded questions and FULL for reproducible execution. Follow the
[mode policy](references/modes.md). Essential safeguards apply in both modes.

## Inputs and preflight

Immutable file, intended analysis, reference/assembly when relevant, sample metadata and format expectations.

## Method selection and procedure

1. Preserve the input and record its hash, encoding, compression and declared
   provenance. Use file content for recognition. Filename extensions alone do
   not validate format or biological suitability.
2. Inspect supported small FASTQ, FASTA, VCF, BED, GTF/GFF, numeric tables and
   SBML records with the scoped baseline. It enforces 8 MiB source and 4 MiB
   decompressed limits; gzip detection and parsing use bounded content. Preserve
   exact table IDs and inspect raw headers/widths before numeric conversion.
   Declare FASTQ/FASTA sequence alphabet; retain IUPAC ambiguity symbols. Reject
   blank/mismatched FASTQ identifiers and duplicate FASTA identifiers under the
   supported uniqueness policy. Malformed compression/encoding/XML must fail
   through controlled scientific validation.
3. Recognize BAM, CRAM, BCF and HDF5 signatures separately from parsing. Require
   pysam/samtools for BAM/CRAM/BCF and an H5AD-aware parser for AnnData structure.
   CRAM needs the correct reference. A generic HDF5 signature does not identify
   an H5AD assay.
4. Keep BED zero-based half-open coordinates distinct from GTF/GFF/VCF
   conventions. Compare declared reference builds before joins. Record unsupported
   or unreadable inputs as blocked with the required parser. BED insertion-style
   zero-length intervals are allowed with a downstream compatibility warning.
   Validate scoped alleles, coordinates and strand fields; request format_hint
   for ambiguous tables. Root-only SBML is XML_STRUCTURE_ONLY, not a model.
5. Match scientific input type to the intended workflow. A valid expression
   table does not establish raw counts, and filenames do not prove sample identity.

## Validation and evidence

Stop dependent analysis for failed input, identity, scale or design gates.
Record actual execution status and preserve inputs. Obtain qualified human
methodological review before high-stakes interpretation. All fixtures are synthetic.

## Recipes and limitations

Read the [input contract](references/input-contract.md),
[recipes](references/recipes.md) and [troubleshooting](references/troubleshooting.md).

Example invocation follows.

> $bioinformatics-file-formats inspect the file content, reference convention and parser requirements before analysis.
