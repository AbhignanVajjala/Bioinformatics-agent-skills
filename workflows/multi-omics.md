# Paired multi-omics workflow

Entry: a prespecified question, per-modality matrices, assay scales, subject/specimen mapping, covariates, reference versions and access permission. Follow the [execution contract](README.md). Demonstration: `python examples/multiomics/run.py --output artifacts/multiomics` from repository root; its scope is limited to the actual generated report.

| Stage / owner | Inputs/tools | Output and gate | Recovery / next |
|---|---|---|---|
| Identity / curator | Explicit patient-specimen-assay mapping; join validation | Paired set, excluded samples with reasons, duplicate/conflict report | Resolve aliases from authoritative metadata; never pair by row order; conflicts block integration |
| Modality QC / computational biologist | Per-assay units, missingness, features, reference; modality diagnostics | QC summary, documented filtering and namespace mapping | Fix incompatible identifiers/scales; preserve modality-specific exclusions |
| Design / biostatistician | Unit, covariates, phenotype, study goal | Batch/confounding report and grouped split plan for prediction | Leakage requires rebuilding splits and refitting preprocessing; no reuse of contaminated performance |
| Preprocess / analyst | Accepted QC and training split | Assay-specific normalization/transformation, parameters and train-fitted transforms | Investigate missingness mechanism; avoid universal zero-fill; insufficient data blocks fitting |
| Select and integrate / analyst | Scientific goal, sample size, missing modalities | Justified method: latent factors for exploratory shared variation, network fusion for sample similarity, or a supervised model with nested validation | Do not concatenate incomparable scales blindly; tiny examples remain descriptive, not validated prediction |
| Sensitivity / biostatistician | Fitted artifacts and design | Sensitivity to scaling, batch, missingness and mapping; held-out evidence where valid | Instability limits claims; revise plan or require additional cohorts |
| Interpret and audit / biologist + auditor | Diagnostics, commands/hashes and external evidence | Claim ledger, methods, validation report and reproducible handoff | Association is not mechanism; no generalization claim without appropriate external validation |

Feature identifiers need not overlap across modalities to integrate samples. A shared feature label alone does not prove equivalent molecular measurement. Report what was actually integrated, sample losses and whether a full integration model was fitted.
