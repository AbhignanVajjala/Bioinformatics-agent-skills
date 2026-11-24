# Bioinformatics file formats maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Human-directed maintainer self-review with
ChatGPT-assisted scripts in Codespaces, not independent external peer review.
Independent methodological and biological validation remain incomplete.

## Supplied historical evidence

Source `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2, November 24,
2026. Environment: Python 3.12.3, NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3.
Original directories: `artifacts/my-combined-domain-audit-qAgil0` and
`artifacts/my-final-domain-audit-9j6Ml3`. Original files are unavailable here;
no original hashes or execution records are reconstructed. The supplied first
batch was 51 checks (26 PASS/16 INVESTIGATE/9 ASSESS); the second was 49
(18/19/12). Combined **100: 44 PASS/35 INVESTIGATE/21 ASSESS** across four
skills, not per-skill totals, accuracy rates or distinct defect counts.
Assessment-only cases also exposed confirmed numerical defects.

Accepted invalid records included empty FASTQ IDs, mismatched plus-line IDs,
digit sequences, empty VCF REF/ALT, invalid GTF strand and duplicate/blank table
headers. Numeric IDs "0001"/"1" collapsed during CSV inference. Identical gzip
content behaved differently under .csv.gz versus .dat. Malformed XML, corrupt
gzip and invalid UTF-8 raised uncontrolled ParseError/EOFError/UnicodeDecodeError.

Duplicate FASTA identifiers were accepted; Phase 8 explicitly rejects them under
a first-token uniqueness policy. Zero-length BED was rejected historically;
UCSC specifies insertion-style start=end records, now accepted with a downstream
compatibility warning. Root-only SBML was correctly XML_STRUCTURE_ONLY, and
four-byte BAM magic correctly required OPTIONAL_PYSAM_REQUIRED. Neither is full
format validation. Reference mismatch, incomplete FASTQ, invalid intervals and
missing numeric expression values continue to reject.

## Correction and regression evidence

[Bounded parser](../../src/bioskills/formats.py) checks raw table headers/widths,
keeps exact string IDs and parses already decompressed text. Source/decompressed
limits are 8/4 MiB. Gzip magic is independent of extension. Malformed gzip,
UTF-8/XML fail through controlled scientific validation. DTD/entity constructs
are unsupported.

| Criterion | New evidence / acceptance condition |
|---|---|
| FASTQ/FASTA | Nonblank/repeated IDs, declared IUPAC/protein alphabet, four-line and length checks; FASTA IDs unique |
| VCF | Required alleles/positions/widths with supported symbolic, star, missing and breakend representations |
| Annotation/BED | Scoped coordinates/strands/phase; GFF '?' allowed; zero-length BED warning |
| Tables | Raw header/width validation; exact "0001"/"1" identities; missing/nonfinite values reject |
| Compression/errors | Same gzip bytes work under .dat; malformed/bounded failures controlled |
| Partial formats | XML_STRUCTURE_ONLY and optional binary parser statuses remain explicit |

Regressions are in tests/test_format_integrity.py and integration tests;
[implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md) records actual execution.
VCF genotype semantics, annotation attributes, GFF FASTA sections, full BED block
semantics, binary parsing and biological/reference identity are outside scope.

## Newly consulted primary specifications — 2026-11-24

[UCSC BED format](https://www.genome.ucsc.edu/FAQ/FAQformat.html) documents
zero-length insertion positions. [HTS specifications](https://samtools.github.io/hts-specs/)
include VCF's symbolic/star/breakend representations and parser scope.
[NCBI FASTA guidance](https://www.ncbi.nlm.nih.gov/genbank/fastaformat/)
requires unique sequence identifiers and defines ambiguity symbols.
[Sequence Ontology GFF3 specification](https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md)
defines one-based coordinates and permitted strands. Consultation is source
grounding, not independent review or complete conformance certification.
