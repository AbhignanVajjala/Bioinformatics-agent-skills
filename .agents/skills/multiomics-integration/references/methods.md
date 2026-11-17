# Integration method notes

Authoritative documentation targets (not asserted retrieved during this skill-authoring run):

- [MOFA2 project documentation](https://biofam.github.io/MOFA2/): inspect data types, likelihood, missingness and view weighting for the selected version. A latent factor model requires model assessment; successful fitting is not validation of biology.
- [mixOmics documentation](https://mixomics.org/): consult the chosen multiblock method's design, scaling and validation requirements.
- [scikit-learn cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html): use group-aware splitters for repeated specimens and nested evaluation when tuning.
- [scikit-learn leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html): fit preprocessing only on training data through a pipeline; unsupervised preprocessing can still leak held-out distributional information.

Verify exact installed-version behavior before execution. No MOFA, SNF or multiblock analysis is claimed by the synthetic readiness example. SNF may be considered only after consulting a verified implementation and choosing appropriate distances; this repository does not supply an unverified SNF recipe.

Same patient is not always same specimen: timepoint, tissue and treatment can differ. A matching subject ID alone does not justify specimen-level cross-assay correlation. Gene–protein correspondence is often many-to-many, and metabolite annotations have graded confidence. Preserve these uncertainties in mapping and interpretation.
