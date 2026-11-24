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

## Executable baseline version 2

Matrices, mappings and declarations must have exactly the same two assay keys.
Require DataFrames, nonempty finite numeric matrices, unique metadata columns,
and all four mapping fields before selecting them. Identifiers are homogeneous
nonblank strings or finite numeric labels, preserved exactly. Mixed string/number
identities are rejected, never coerced or trimmed. Timepoints can be nonblank
categories or finite numbers, consistently typed across assays; no universal
date format is imposed. Per-assay modality, scale, namespace and reference must
be nonblank strings; RNA count_generation must also be a nonblank string.
Ordinary Python mappings cannot retain duplicate keys: loaders must reject
duplicate serialized fields before constructing those mappings.

RNA declarations additionally require `count_universe: complete_supplied_matrix`
and a nonblank `normalization_scope` describing the complete intended input.
Preselected count subsets and external `library_sizes` are unsupported. Supply
the complete intended count universe, not only correlated genes. Every supplied
RNA row contributes to exact integer column sums before selecting feature pairs;
unmatched samples also undergo integrity/zero-library checks. Record sample IDs,
denominators, feature count, scope and denominator source. Declared provenance
cannot authenticate the count universe or distinguish integer-looking TPM from
real counts. Counts and totals must not exceed 2^53-1 (exact binary64 integer
scope). Nonnegative integer appearance alone is insufficient evidence of origin.

The feature map must be nonempty, have unique assay columns and nonmissing,
nonblank, existing, one-to-one features. Only mapped pairs need variable features;
whole-matrix numeric/finiteness checks still apply. At least three matched
specimens are required for this descriptive baseline (not a power guarantee).
Undefined mapped pairs reject the whole analysis; no partial EXECUTED report.

Pearson uses exact power-of-two scaling before shifted compensated centering,
rescaled centered unit vectors and compensated dot sums. Maximum centered scaled
variation <=64*binary64 epsilon is rejected as cancellation-sensitive. Results
must be within [-1,1] allowing 16*epsilon roundoff only. Extreme dynamic ranges
causing underflow are unsupported and rejected. Local NumPy error contexts and
RuntimeWarning handling fail closed and restore caller settings. Numerical
failures attach NOT_RUN and structured stage/category/message evidence to the
ScientificValidationError; success reports contain numerical policy and events.
These conservative thresholds bound this implementation, not universal biology.

Report specimen and distinct-subject counts, specimens per subject, timepoints,
and specimen/subject counts by contributing partition. Single-subject and
longitudinal descriptions are allowed with warnings; population inference and
predictive validation remain NOT_RUN. All matched partitions contribute;
examining held-out observations may influence and compromise future confirmation.
