# Executable metabolic recipe

Run this optional command from the full repository or executable toolkit after
installing COBRApy 0.29.1, GLPK and the example dependencies:

```text
python examples/domain-recipes/run.py metabolic --output new-metabolic-output
```

The lightweight ZIP provides the instructions. The command requires the
external repository/toolkit implementation.

| Input type | Question | Method | Software | Expected result | Failure conditions |
|---|---|---|---|---|---|
| Licensed SBML/FBC | Feasibility under declared medium | Read model, inspect objective, FBA | COBRApy/GLPK | Optimal status, residual and bounds audit | Empty objective, invalid bounds, solver failure |
| Feasible model | Parsimonious alternate solution | pFBA at fraction 1 | COBRApy | Original biomass flux and separate total-flux objective | Nonoptimal solve |
| Feasible model | Attainable reaction ranges | FVA at fraction 0.9 | COBRApy | Per-reaction bounds | Unbounded/infeasible state |
| GPR model | Gene versus reaction deletion | Gene knockout and reaction knockout separately | COBRApy | GPR-dependent flux changes | Ambiguous GPR or wrong identity |
| Synthetic product drain | Growth/product allocation | Product objective with biomass lower bounds | COBRApy | Feasible trade-off | Missing medium, units or growth requirement |

The recipe writes and reloads synthetic SBML, captures Python parsing warnings,
records reaction/metabolite/gene counts and compartments, medium and exchange
bounds, and runs FBA, pFBA, FVA and single-gene deletion. It checks an OR GPR,
double-gene deletion and a separate biomass-reaction knockout. Temporary
constraints use `with model:` and are verified restored. Its deliberately
infeasible and unbounded models are rejected before interpretation.

FVA ranges are marginal feasible ranges and may not be jointly attainable.
The pFBA total-flux objective differs from the original biomass objective.
All quantities here use arbitrary toy flux units. Supply calibrated units,
licensed organism-specific models, growth requirements and media before using
a trade-off for real research. Bound increases do not model gene overexpression.
