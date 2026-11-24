# Bounded file-format input contract

`bioskills.expanded.inspect_format(path, reference=None, expected_reference=None,
format_hint=None, sequence_alphabet="nucleotide")` reads immutable pathlib input.
Limits: 8 MiB source, 4 MiB decompressed content; gzip recognized by magic bytes,
not extension. Parse the bounded decompressed UTF-8 text once. Invalid gzip,
encoding and XML produce controlled ScientificValidationError. Report source and
decompressed SHA-256. Declared reference mismatches reject; declarations are not
authenticated reference identity. Use format_hint for ambiguous numeric/BED/GFF text.

Numeric CSV/TSV checks raw unique nonblank headers and exact record widths before
pandas; categorical row/column IDs remain exact strings, including "0001"/"1".
Missing/nonfinite numeric values reject. This does not establish raw counts.
FASTQ is four-line records: nonblank read ID, consistent optional repeated ID,
sequence/quality lengths and ASCII quality. Declared dna/rna/nucleotide alphabets
allow their IUPAC ambiguity symbols; protein is explicit. FASTA requires unique
first-token IDs and supported sequence text; gaps are permitted in FASTA.

VCF checks fixed headers, widths, positive positions, nonempty REF/ALT and scoped
base/symbolic/star/missing/breakend alleles, not genotype semantics. GTF/GFF checks
nine nonempty fields, one-based intervals, phase and strand (GFF additionally '?').
BED checks consistent 3–12 field records, zero-based start<=end, scoped score,
strand and thick interval. Zero-length insertion-style BED is allowed with a
compatibility warning; full block semantics and downstream suitability are untested.
Annotation attributes and embedded GFF FASTA are outside scope.

SBML root inspection returns XML_STRUCTURE_ONLY, including a root-only document;
this is not an SBML model check. DTD/entity constructs are unsupported. BAM/CRAM/
BCF/HDF5 signature recognition explicitly requires optional parsers; four bytes
of BAM magic do not validate BAM. This entire interface is triage, not complete
format conformance, specimen identity or biological validation.
