# Metabolic troubleshooting

- Confirm GLPK availability before running any solve. A missing solver is a
  blocked dependency and supplies no biological result.
- Inspect biomass, maintenance, exchanges and reaction orientation for
  infeasibility. Do not silently open every exchange or delete requirements.
- Capture COBRApy logging as well as Python warnings when loading real SBML.
  Syntactic import cannot establish biochemical consistency.
- Check restored bounds and objective after every temporary perturbation.
- Gene knockout evaluates the GPR Boolean expression. An OR rule can retain
  activity after one gene is removed. Reaction knockout removes the reaction.
- Add independent model-quality and biological checks for real organisms.
  Steady-state flux is a model prediction and requires experimental validation.

Use version-matched official
[COBRApy simulation documentation](https://cobrapy.readthedocs.io/en/latest/simulating.html)
and [deletion documentation](https://cobrapy.readthedocs.io/en/latest/deletions.html).
Version-specific 0.29.1 documentation retrieval was unavailable on 2026-11-19.
Record the installed version and actual execution evidence separately.

A PASS solve with compartment-identification logs is not a structure certificate. Inspect exchange versus transport/demand classification. The synthetic e/c structure gate fails mismatches instead of silencing warnings. Expected infeasible-control warnings are labeled separately. Scoped handlers are removed after execution; logging policy is not globally reconfigured.
