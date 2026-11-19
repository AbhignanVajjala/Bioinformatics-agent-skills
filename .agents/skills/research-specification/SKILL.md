---
name: research-specification
description: "Define a testable research question, experimental unit, estimand, analysis plan and acceptance gates before analysis; use for new or changed studies, not to retrospectively label exploration as preregistered confirmation."
metadata:
  maturity: experimental
---

# Research specification

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Inputs and preflight
Require the biological question, organism/material, assay and reference, available cohorts, independent experimental units, intervention/exposure, outcome, covariates and resource/access limits. Distinguish technical replicates from independent subjects. If these are unknown, produce a blocked specification with targeted missing-information requests, not invented values.

## Method selection and procedure
1. State whether the task is descriptive, exploratory, confirmatory, predictive or causal. Translate the question into an estimand, e.g. treatment-associated gene expression difference conditional on batch, with explicit numerator/reference group.
2. Draw the unit hierarchy: patient → specimen → library → measurement. Record repeated measures, pairing, randomization, controls and recruitment. Define the population to which inference could apply.
3. Separate primary endpoints/contrasts from exploratory analyses before examining outcomes. Predeclare inclusion/exclusion, missingness handling, low-information filters, covariates and multiple-testing families. A later change is a documented amendment.
4. Inspect design identifiability: every proposed effect needs informative variation. Perfect treatment–batch confounding blocks an adjusted treatment effect. Small sample size does not become adequate by counting genes, cells or repeated aliquots as replicates.
5. Choose a method appropriate to the data scale: raw gene counts support count-aware RNA-seq models; censored survival requires event/censoring variables and appropriate survival methods; supervised prediction requires grouped held-out evaluation. Do not substitute a generic t-test or ordinary regression by convenience.
6. Plan diagnostics, effect sizes and uncertainty, sensitivity analyses and expert review. For power, use justified expected effect/dispersion or simulations, report assumptions, and avoid post-hoc observed power as evidence of validity.
7. Define acceptable claims and rejection gates. Include technical readiness separately from statistical validity and biological interpretation. Record planned files and commands as NOT_RUN until executed.

## Validation and stops
Cross-check sample numbers against the manifest and check design rank before modeling. Reject a survival plan that treats censored observations as observed death times. Halt confirmatory inference with unidentified experimental units, unrecoverable confounding or no independent replication. Permit clearly labeled descriptive summaries when appropriate, with limitations.

## Outputs and interpretation
Write `research-spec.json`, `analysis-plan.md`, and `acceptance-checks.json`. Include intended claims, risks, alternatives, amendments and reviewer identity. An association-oriented study cannot establish therapeutic efficacy or causation solely through significance.

## Examples and definition of done
Positive: plan a paired pre/post patient RNA-seq comparison with subject blocking and explicit time contrast. Negative: claim six libraries from one donor provide six biological replicates.
Done means each planned inference has a defined unit, estimand, suitable data/method, diagnostics and failure gate. Evaluate confounding, pseudoreplication and ignored-censoring plans; approving any of them without qualification is failure.
