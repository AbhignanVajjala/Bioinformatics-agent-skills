# Constraint-based metabolic modeling workflow

Entry: model version/license, organism, compartments, objective question, flux units, medium and solver environment. Follow the [execution contract](README.md). Demonstration: `python examples/metabolic-modeling/run.py --output artifacts/metabolic-modeling` from repository root.

| Stage / owner | Inputs/tools | Output and gate | Recovery / next |
|---|---|---|---|
| Read / curator | SBML/FBC or documented synthetic construction; COBRApy parser | Model hash/version, reaction/metabolite inventory, source restrictions | Reject malformed or incompatible model; preserve original |
| Inspect / computational biologist | Bounds, objective coefficients, exchange conventions, medium, GPR | Explicit constraints/objective table, balance and boundary checks | Missing objective or inconsistent bounds block solving; do not silently invent medium |
| Feasibility / analyst | Accepted model and solver; FBA | Solver status, objective, numerical residual checks | Infeasible/unbounded/failed runs yield no optimized-flux claim; isolate inconsistent constraints |
| Alternatives / analyst | Feasible optimum and biological question; pFBA/FVA | Parsimonious solution and/or flux ranges with objective fraction recorded | Retain solver/tolerance settings; alternative optima limit single-flux interpretation |
| Perturbation / computational biologist | Defined GPR-aware gene intervention or reaction-bound hypothesis | Baseline/intervention comparison and growth-production tradeoff | A reaction knockout is not automatically a gene knockout; infeasible intervention remains a failed prediction |
| Sensitivity / biostatistician | Medium/bound/objective uncertainty | Responses to justified parameter changes with exact values | Sensitivity to arbitrary constraints limits claims; do not optimize assumptions after seeing results |
| Interpret/audit / biologist + auditor | All runs, model hashes and constraints | Prediction ledger, methods, validation report and rerun command | Steady-state feasible flux is not measured flux, rate regulation or proven phenotype; experimental validation remains separate |

Inspect mass/charge balance where formulas are present, distinguish designed boundary imbalance from internal imbalance, and state unresolved annotations. Stoichiometry-only models do not establish thermodynamic feasibility. Toy-model solver regressions cannot establish accuracy of a genome-scale reconstruction.
