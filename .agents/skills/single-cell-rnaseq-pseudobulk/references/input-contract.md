# Single-cell RNA-seq and donor-aware pseudobulk input contract

Raw counts, cell-to-specimen/donor/timepoint/condition/population mapping, organism, reference, upstream count-generation and QC records.

Python/NumPy/pandas for aggregation; optional pinned R/edgeR or external muscat for differential state.

Use the API documented in the full repository. Keep specimen, donor, assay,
reference and unit declarations explicit. Protect private metadata and never
infer unrecorded identity or provenance. Reject malformed or scientifically
incompatible inputs before downstream inference.

The API is `bioskills.expanded.pseudobulk(counts, cells, organism=...,
reference=..., count_generation=..., paired=False)`. Counts are a pandas
gene-by-cell DataFrame. Cell metadata has exactly aligned cell IDs as its index
and nonblank `subject_id`, `specimen_id`, `condition`, `timepoint` and
`cell_type` columns. Preserve batch separately for downstream design review.
Specimen context must be consistent. Two conditions are required by this
baseline. The returned count matrix and metadata use generated pseudobulk
sample IDs, with original specimen/donor/population relationships retained.
The audit reports missing donor-condition combinations and per-population
readiness. It leaves differential-state fitting NOT_RUN.
