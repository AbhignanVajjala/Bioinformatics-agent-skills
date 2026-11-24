# Executable cross-view baseline

From the full repository or executable toolkit with Python example dependencies:

```text
python examples/domain-recipes/run.py multiomics --output new-multiomics-output
```

The universal ZIP includes the Python implementation and synthetic resources;
install its declared dependencies before running. The example writes synthetic RNA
counts and protein log2 intensities and reloads their matrices and mappings.
It computes actual Pearson associations between explicitly mapped features
after specimen reconciliation. RNA is transformed with log2(CPM+1) for this
descriptive calculation. Protein values retain their declared log2 scale.
Missing or nonfinite values block this baseline. No universal zero-fill is used.

| Input type | Question | Method | Software | Expected result | Failure conditions |
|---|---|---|---|---|---|
| Matched assays and known feature map | Cross-view concordance | Descriptive Pearson correlation | NumPy/pandas baseline | Actual correlations and exclusion audit | Identity, scale, timepoint or mapping ambiguity |
| Compatible transformed blocks | Shared sample geometry | Concatenation with justified view weighting | External workflow | Descriptive embedding | Dominant assay size or incompatible scales |
| Matched views | Shared latent factors | MOFA2 | Optional external MOFA2 | Fitted factors and diagnostics | Unverified likelihood/missingness assumptions |
| Matched sample distances | Similarity fusion | SNF | Optional external implementation | Fused similarities and sensitivity | Unjustified distances or unstable neighborhoods |
| Labeled matched views | Prediction | Supervised multiblock model | Optional external established method | Grouped held-out estimates | Leakage or preprocessing outside training folds |

Only the cross-view baseline is implemented here. MOFA2, SNF, concatenation
and supervised fitting are NOT_RUN. The baseline reports no prediction accuracy.
For supervised work, split subjects before learning imputation, scaling,
feature selection or model parameters. The present workflow audits declared
partitions and performs no supervised fitting.
