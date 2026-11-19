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
