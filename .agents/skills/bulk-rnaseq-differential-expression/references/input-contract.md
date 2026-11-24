# Bulk RNA-seq input contract

Use UTF-8 tab-separated files. Counts have a first gene-ID column and one column
per library. Metadata has `sample_id`, `subject_id`, `condition` and, for the
batch design, `batch`. IDs must be unique, nonblank and matched explicitly.
A permuted sheet is rejected by default. Set `align_samples: true` in the
JSON config to request an audited in-memory ID-based order. Original files are
immutable.

The JSON config requires `organism`, `reference`, `count_generation`,
`measurement_type: raw_counts`, `design: unpaired|paired|batch`,
`reference_level` and `treatment_level`. Count-generation provenance is a
declaration to verify from upstream records. Integer-looking TPM can evade
value checks if its provenance is falsely declared.

A paired fixture requires exactly one library per donor per condition. Other
repeated structures require a separate justified workflow. Independent designs
reject repeated subject IDs. Both conditions need multiple independent subjects.
The minimum gate does not establish adequate power. Check model rank and
positive residual degrees of freedom before fitting.

Result exports distinguish `analysis_status: EXECUTED` from `NOT_RUN`.
Preserve configuration, test family, reference levels, filtering, missing-pair
policy, hashes, versions and exclusions. Controlled pre/post comparisons need
an estimand that separates treatment from time where the design permits it.

## Strict executable contract

Required configuration fields are non-null, nonblank scalar strings. Reject
duplicate JSON keys before object parsing (including escaped aliases), unknown
fields, unsupported enumerations and non-Boolean align_samples. No metadata
defaults manufacture provenance. TSVs are plain UTF-8 records: every data row
must have exactly the header width, with no implicit row names, duplicate/blank
headers or CSV multiline/quoting interpretation. All categorical fields remain
exact strings; only count cells are numeric. Preserve leading zeros, long IDs,
literal NA identifiers and distinct labels such as 01/1. Missingness is an empty
field, not an automatic conversion of the literal identifier NA.

Counts must be nonnegative finite integers <=2147483647 for the R recipes.
Text integrality is checked before floating conversion can hide fractional
digits or underflow. Exact integral decimal/exponent notation is supported.
Library totals before and after filtering must be finite, positive and within
the exact binary64 integer scope <=2^53-1. Generic Python check_counts retains
that wider scope; validate_counts additionally gates R readiness. Boolean counts,
duplicate metadata columns and mixed numeric/text identifiers reject predictably.

Model factor codes and their original-label mapping are explicit; original
metadata.tsv and contrast labels retain exact identities. design.tsv uses an
explicit sample_id column. The normalization table preserves sample headers and
its input gene-ID header. Native fit warnings/messages, actual dispersion type,
normalization factors, ignored covariates and known confounding are auditable.
Undefined DESeq2 ratio size factors stop rather than auto-switching methods.
Preflight rejection is NOT_RUN; a started analysis that fails is FAILED; only
complete verified output is EXECUTED. Readiness is not fitting or validation.
