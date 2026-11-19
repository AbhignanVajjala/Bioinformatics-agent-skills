# Multi-omics input contract

Each matrix has unique feature rows and assay sample columns. Each matching
metadata table has assay sample IDs as its index and `specimen_id`,
`subject_id`, `timepoint` and `split` columns. Preserve exact matrix/metadata
sample order. Reconcile by explicit specimen IDs across views, never by row
position. Conflicting subject or timepoint assignments block analysis.

Declare modality, scale, feature namespace and annotation release per view.
RNA raw counts additionally require count-generation provenance. The current
baseline accepts RNA raw counts and declared protein/metabolite log2 intensities.
It rejects other scales and nonfinite values. Cross-view features require a
known one-to-one map. Real many-to-many annotation needs a separate audited
policy before using this baseline.

Keep modality-only specimens in the exclusion audit. Partial assay coverage
and missing values can change the analysis population. The finite complete-case
baseline makes no missing-at-random claim and performs no imputation.
