# Executable metabolic recipe

Run this optional command from the full repository or executable toolkit after
installing COBRApy 0.29.1, GLPK and the example dependencies:

```text
python examples/domain-recipes/run.py metabolic --output new-metabolic-output
```

The single universal ZIP includes this implementation and its dependency manifest; install scientific dependencies explicitly.

| Input type | Question | Method | Software | Expected result | Failure conditions |
|---|---|---|---|---|---|
| Licensed SBML/FBC | Feasibility under declared medium | Read model, inspect objective, FBA | COBRApy/GLPK | Optimal status, residual and bounds audit | Empty objective, invalid bounds, solver failure |
| Feasible model | Parsimonious alternate solution | pFBA at fraction 1 | COBRApy | Original biomass flux and separate total-flux objective | Nonoptimal solve |
| Feasible model | Attainable reaction ranges | FVA at fraction 0.9 | COBRApy | Per-reaction bounds | Unbounded/infeasible state |
| GPR model | Gene versus reaction deletion | Gene knockout and reaction knockout separately | COBRApy | GPR-dependent flux changes | Ambiguous GPR or wrong identity |
| Synthetic product drain | Growth/product allocation | Product objective with biomass lower bounds | COBRApy | Feasible trade-off | Missing medium, units or growth requirement |

The recipe writes and reloads synthetic SBML, captures scoped Python warnings and COBRApy logging,
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

## Corrected synthetic fixture (0.2.3)

a_e/e extracellular exchanges through EX_a (-10,0); TRANSPORT (0,1000) converts a_e to a_c/c cytoplasm. BIOMASS and PRODUCT (0,1000) are intracellular demands, not exchanges. The shared base has three reactions/two metabolites; the domain adds PRODUCT and the OR GPR. Biomass remains ten; pFBA total absolute flux changes from 20 to 30 because transport carries ten. FVA90: EX_a [-10,-9], TRANSPORT [9,10], BIOMASS [9,10], PRODUCT [0,1]. Product maxima are 10/5/1 at growth minima 0/5/9 with uptake ten, and three at uptake seven/growth four.

validate_toy_structure asserts this fixture only; numerical feasibility is separate from model structure, biological plausibility and independent biological validation. warning_evidence records channel, stage and expected negative controls; parsing_warnings is loading-only and cannot describe all runtime warnings. knockout-controls.csv supplements the unchanged single-gene CSV with baseline, both single genes, double-gene and reaction controls, actual status and predicted biomass. Zero growth can be optimal. The deliberate unbounded control opens uptake, transport and biomass; normal execution still rejects infinite bounds.
