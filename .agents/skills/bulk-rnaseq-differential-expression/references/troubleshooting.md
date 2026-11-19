# Bulk RNA-seq troubleshooting

- Rank deficiency blocks the affected effect. Inspect the condition-by-batch
  table and donor allocation. Batch correction cannot identify a missing contrast.
- Duplicate libraries or technical replicates require aggregation justified by
  assay provenance. They do not create new biological units.
- Check declared measurement type before converting data. Never reconstruct raw
  counts by rounding TPM, FPKM or transformed expression.
- A failed library or absent paired condition changes the population and design.
  Document the exclusion and reassess the contrast.
- Inspect dispersion and normalized-count diagnostics. An NA adjusted p-value
  can arise from native independent filtering or outlier handling. Do not replace
  it with a fabricated significance value.
- Version mismatches block these pinned recipes. Install the historical
  R/Bioconductor release explicitly in an isolated environment.
- Insufficient replication may permit labeled descriptive summaries, with no
  confirmatory DE claim. Seek qualified review for real study interpretation.

Primary API sources consulted on 2026-11-19 include the official
[DESeq2 manual](https://new.bioconductor.org/packages/release/bioc/manuals/DESeq2/man/DESeq2.pdf)
(the retrieved snapshot identifies DESeq2 1.46.0, Bioconductor 3.20) and
[edgeR introduction](https://bioconductor.org/packages/release/bioc/vignettes/edgeR/inst/doc/intro.html).
Historical package pages returned unavailable through the documentation browser.
The pinned installation checks installed versions and CI saves session info.
