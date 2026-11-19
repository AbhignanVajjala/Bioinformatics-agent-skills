---
name: single-cell-rnaseq-pseudobulk
description: "Aggregate verified raw single-cell counts by specimen and cell population with donor-aware readiness checks; use for pseudobulk preparation, not cell-level population inference or embeddings as counts."
metadata:
  maturity: experimental
---

# Single-cell RNA-seq and donor-aware pseudobulk

## Execution modes

Use QUICK for bounded questions and FULL for reproducible execution. Follow the
[mode policy](references/modes.md). Essential safeguards apply in both modes.

## Inputs and preflight

Raw counts, cell-to-specimen/donor/timepoint/condition/population mapping, organism, reference, upstream count-generation and QC records.

## Method selection and procedure

1. Require gene-by-cell raw counts and an exact cell metadata table with donor,
   specimen, condition, timepoint, batch and cell population. Verify upstream
   cell QC, doublets, ambient RNA and annotation quality before aggregation.
2. Preserve original cell records. Sum raw counts by specimen and cell population
   using the implemented baseline. Record cell totals and missing donor-condition
   combinations. Keep technical libraries distinguishable from biological subjects.
3. Evaluate independent subjects and paired structure per population. Validate the
   design matrix and residual degrees of freedom before testing. Missing replication
   blocks population inference and can permit labeled descriptive aggregation.
4. For differential state, use a prespecified donor-level edgeR or muscat workflow.
   Define filtering, contrasts, gene/cell-population testing families and FDR.
   Aggregation alone leaves differential-state modeling NOT_RUN.
5. Export actual pseudobulk counts, sample metadata, exclusions and limitations.
   Keep condition changes and cell-type annotation uncertainty explicit.

## Validation and evidence

Stop dependent analysis for failed input, identity, scale or design gates.
Record actual execution status and preserve inputs. Obtain qualified human
methodological review before high-stakes interpretation. All fixtures are synthetic.

## Recipes and limitations

Read the [input contract](references/input-contract.md),
[recipes](references/recipes.md) and [troubleshooting](references/troubleshooting.md).

Example invocation follows.

> $single-cell-rnaseq-pseudobulk aggregate these raw counts by donor specimen and cell type before design review.
