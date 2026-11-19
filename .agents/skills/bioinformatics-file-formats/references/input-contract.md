# Bioinformatics file formats and provenance input contract

Immutable file, intended analysis, reference/assembly when relevant, sample metadata and format expectations.

Python text/gzip/XML/pandas baseline; optional pysam/samtools or AnnData parsers.

Use the API documented in the full repository. Keep specimen, donor, assay,
reference and unit declarations explicit. Protect private metadata and never
infer unrecorded identity or provenance. Reject malformed or scientifically
incompatible inputs before downstream inference.

`bioskills.expanded.inspect_format(path, reference=None,
expected_reference=None)` accepts a pathlib Path. It reads at most 4 MiB of
decompressed data. Text uses UTF-8. FASTQ support is the four-line form,
FASTA support checks basic sequence text, VCF checks basic headers and positions,
BED checks zero-based half-open intervals, and GTF/GFF checks one-based
intervals. Numeric tables require finite values and unique IDs. SBML inspection
checks XML structure only. BAM/CRAM/BCF/HDF5 signature results explicitly require
additional parsers. These scopes supply compatibility triage rather than full
format or assay certification.
