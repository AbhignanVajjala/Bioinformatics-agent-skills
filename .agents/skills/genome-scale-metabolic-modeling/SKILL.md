---
name: genome-scale-metabolic-modeling
description: "Inspect and analyze constraint-based metabolic models with SBML/FBC, COBRApy, FBA, pFBA and FVA under explicit objectives and media; use for model-based steady-state predictions, not measured flux claims or proven therapeutic interventions."
metadata:
  maturity: experimental
---

# Genome-scale metabolic modeling

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Required inputs and preflight
Require model file/version/license and organism/strain, compartments and identifiers, objective and direction, medium/exchange definitions, flux units, solver availability and the biological question. Preserve the original model and record every constraint change. SBML/FBC describes constraint information; syntactically readable SBML does not prove biochemical validity. Large FVA/knockout screens need bounded parallelism and runtime estimates; start with a tiny solver smoke test.

## Method selection
FBA optimizes a specified objective subject to steady-state stoichiometry and bounds; it does not estimate measured intracellular flux. pFBA chooses a minimum-total-flux solution subject to an objective requirement and is one modeling assumption, not proof of enzyme economy. FVA gives per-reaction attainable ranges at a documented objective fraction; extrema across reactions are generally not jointly attainable. Use isotope-constrained flux analysis or experimental measurements for different questions. Do not infer overexpression simply by increasing a flux upper bound.

## Procedure
1. Load with a supported COBRApy SBML reader and record parsing warnings and package/solver versions. Inspect metabolite compartments, reaction IDs, stoichiometry, objective coefficients and GPR rules. Check atom/charge balance where chemical formulae are available, documenting biomass, exchange and pseudo-reaction exceptions.
2. Separate exchange, transport, demand and sink reactions. Inspect boundary orientation rather than assuming every negative flux is uptake. Record media concentrations separately from flux bounds; converting concentrations to uptake rates needs additional kinetic/experimental assumptions.
3. Check finite ordered bounds, intended reversibility and nonempty valid objective. Inspect unexplained sources/sinks, unconstrained nutrients and energy-generating cycles. Verify organism/strain context and reference biomass composition where biologically material.
4. Establish baseline feasibility. Inspect solver status before any objective or flux access; infeasible/unbounded/error outcomes have no valid optimized flux to report. Check stoichiometric residuals and bound violations against documented numerical tolerances, not literal floating-point zero.
5. Run FBA under the recorded medium and objective. For pFBA record the objective fraction and understand that its optimization objective may represent total absolute flux, not the original biomass value. Report the original objective separately.
6. Run FVA on selected reactions with the objective fraction, solver tolerance and loop-handling assumptions recorded. Distinguish alternate optima from numerical uncertainty. Investigate unbounded ranges and internal cycles before biological interpretation.
7. Perturb media and bounds with explicit rationale, using model context managers or copied models to restore the baseline. For gene deletion, evaluate GPR Boolean logic; reaction knockout is not interchangeable with gene knockout. Report synthetic lethality/model predictions as hypotheses.
8. Compare objectives, growth/product trade-offs and sensitivity across justified constraints. A product-maximizing result without a growth requirement may be biologically misleading. Record feasibility and objective for every scenario rather than only favorable outcomes.

## Executable model demonstration
From the repository root with COBRApy and its solver installed:

```bash
python examples/metabolic-modeling/run.py --output artifacts/metabolic-modeling
```

This is a synthetic toy network, not a curated genome-scale organism model. Its expected behavior and deliberately infeasible variant test numerical/gating behavior; they do not validate real metabolism.

## Validation, stops and outputs
Stop on missing objective, inconsistent bounds, infeasible/unbounded solver status or unresolved model/medium identity. Do not fix infeasibility by silently opening exchanges or deleting maintenance requirements. Output model/hash, constraint table, solver status, objective, fluxes/ranges, residual checks, sensitivity results and a prediction claim ledger. Keep units explicit; arbitrary toy units must not become mmol/gDW/h by assertion.

## Examples, evaluation and definition of done
Positive: compare biomass-constrained product capacity across documented carbon uptake bounds and propose experimental follow-up. Negative: announce an experimentally increased yield from FBA alone or read fluxes from an infeasible solution. Test infeasible constraints, absent objective and invalid bounds. Done means valid solver evidence, physical/constraint checks and sensitivity support every reported prediction, with experimental validation clearly separate.

Read [method notes](references/methods.md) for source targets and scope.
For the optional full-repository SBML/GPR recipe, read
[recipes](references/recipes.md), the [input contract](references/input-contract.md)
and [troubleshooting](references/troubleshooting.md).
