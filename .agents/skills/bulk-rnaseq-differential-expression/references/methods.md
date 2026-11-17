# RNA-seq method notes

Authoritative documentation targets (bibliographic suggestions, not a claim that these pages were retrieved in this skill-authoring run):

- [DESeq2 Bioconductor package and vignette](https://bioconductor.org/packages/release/bioc/html/DESeq2.html): use the vignette corresponding to the installed release for design, contrast, count import, size factors, dispersion and shrinkage behavior.
- [edgeR Bioconductor package](https://bioconductor.org/packages/release/bioc/html/edgeR.html): consult the installed User's Guide for filtering, TMM normalization, dispersion and quasi-likelihood workflows.
- [limma Bioconductor package](https://bioconductor.org/packages/release/bioc/html/limma.html): distinguish voom's mean–variance weights from arbitrary log-count t-tests.
- [tximport Bioconductor package](https://bioconductor.org/packages/release/bioc/html/tximport.html): follow supported transcript import and gene aggregation; preserve transcript-to-gene mapping/version.

These links are official source targets; verify the relevant page and installed-version behavior before citing specific claims. No primary-literature identifiers are invented here. The demonstration is limited to count/design readiness and QC. Full DE requires actual R/Bioconductor execution evidence, diagnostic inspection and a separately recorded model run.

A minimum-replicate gate is a guard against clearly unsupported inference, not a power calculation or assurance of reliable dispersion estimation. Balanced batches improve identifiability but do not establish randomization or causal identification. A full-rank design can still have weak support, influential points, nonlinear covariate effects or inappropriate independence assumptions.
