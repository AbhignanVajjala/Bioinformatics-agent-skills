---
name: multiomics-integration
description: "Plan and validate integration of matched transcriptomic, proteomic or metabolomic assays with explicit identity, scale, missingness and leakage checks; use for defensible joint analysis, not unverified patient joins or naive incompatible-matrix concatenation."
metadata:
  maturity: experimental
---

# Multi-omics integration

## Required inputs and preflight
Require each modality's feature-by-sample table, assay/units, organism, specimen/timepoint and subject mapping, reference/feature namespaces, QC/missingness information, batch/covariates and research objective. Identify which labels are outcomes, which are covariates, and whether repeated specimens belong to one subject. Verify access permits any planned transfer; keep patient data local unless authorized. Estimate matrix memory and sample-to-feature ratio before selecting a model.

## Method selection
Choose the method to answer the question, not to maximize the number of assays in a plot. For shared unsupervised variation, consider MOFA-family factor models when their likelihood and missingness handling fit the data. For patient similarity/fusion, similarity network fusion requires defensible modality-specific distances and stable neighborhoods. Multiblock approaches require justified scaling and evaluation. For supervised prediction, use a simple regularized baseline and grouped nested evaluation before more complex models. Tiny fixtures support readiness and descriptive association only. Unmatched cohorts cannot be treated as paired specimens; cohort-level integration needs a distinct explicitly justified design.

## Procedure
1. Build a mapping table keyed by subject, specimen, timepoint and modality-specific sample ID. Check uniqueness, one-to-one assumptions and conflicting identity assignments. Report matched, missing and excluded specimens by reason; do not guess joins from row order or expression similarity.
2. Preserve each modality's feature namespace. Map gene/protein/metabolite IDs using versioned resources, retaining one-to-many and unmapped records. A protein accession is not automatically a gene ID; a mass feature is not automatically an identified metabolite. Cross-modality feature alignment must not silently drop ambiguity.
3. Apply modality-specific QC: library composition and count provenance for RNA, identification/inference confidence and intensity scale for proteomics, annotation confidence and batch/drift effects for metabolomics. Record missingness mechanisms; avoid a universal zero-fill strategy or indiscriminate quantile normalization across assays.
4. Define the analysis population and missing-data policy. A complete-case subset can change the target population; report who was excluded and potential selection bias. Use a method with appropriate missingness support only after checking assumptions.
5. Split by subject before preprocessing for prediction. Keep related specimens in one partition; fit imputation, scaling, feature selection and hyperparameters inside training folds. Prevent outcome-derived features, batch correction using held-out labels and repeated-measure leakage. Use external validation if available and report its cohort differences.
6. Select likelihood/transformation/scaling per modality. Track whether factors are dominated by assay size, total intensity, batch or missingness. Compare with single-modality baselines and inspect sensitivity to scaling, feature selection, excluded specimens and random seeds.
7. Evaluate unsupervised stability without claiming predictive performance; evaluate supervised performance with task-appropriate metrics, uncertainty and null/baseline comparisons. Small n/high p results are exploratory even when clusters look clear.
8. Interpret factor loadings or cross-assay associations with biological context and mapping uncertainty. Correlation does not establish regulation or causation; a coherent factor is not a validated biomarker.

## Executable readiness demonstration
From the repository root:

```bash
python examples/multiomics/run.py --output artifacts/multiomics
```

The synthetic example exercises overlap, identity/leakage checks and a limited descriptive computation. Inspect its report for what was actually integrated; do not label it a validated MOFA/SNF or predictive workflow unless that method was executed separately.

## Validation, stops and outputs
Stop paired integration for unresolved specimen mismatches, duplicate mapping keys or incompatible timepoints. Block predictive claims for patient overlap across train/test or preprocessing leakage until grouped evaluation is rerun. Output a reconciliation/exclusion table, feature-mapping audit, QC/scaling decisions, split manifest, results and exact run provenance. A report must retain unintegrated modalities and limitations rather than implying complete coverage.

## Examples, evaluation and definition of done
Positive: RNA/protein measurements from the same specimens with verified IDs and a descriptive shared-variation question. Negative: merge patients solely because row counts match, or place biopsies from one patient in both train and test. Test mismatched patient mappings and repeated-patient splits; both must block dependent analysis. Done means identity, modality preprocessing and evaluation choices are traceable, artifacts exist, and only the actually executed scope is claimed.

Read [method notes](references/methods.md) when choosing an integration model.
