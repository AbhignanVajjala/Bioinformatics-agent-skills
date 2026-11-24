# Maintainer Reproduction and Structural Review of the Synthetic Metabolic Model

- Reviewer: Abhignan Vajjala
- Date: November 24, 2026
- Type: human-directed maintainer self-review with ChatGPT-assisted diagnosis and experimental scripts
- Original source: `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2
- Environment reported by maintainer: GitHub Codespaces Linux, Python 3.12.3,
  COBRApy 0.29.1, NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3,
  python-libsbml 5.21.2, swiglpk 5.0.13, GLPK.

## Evidence provenance

The observations below were supplied by the maintainer in the Phase 5 request.
The original Codespaces artifacts, environment inventory and source ID were
preserved there, but are not available in this local checkout. No original
artifact hashes, timestamps or private paths are reconstructed here. This is
not external independent peer review or unaided human implementation. The
permanent correction and new automated tests are AI-assisted implementation.
New execution results belong in the current implementation status, separately.

## Original reproduction and investigation

The maintainer executed:

```text
python examples/domain-recipes/run.py metabolic --output artifacts/my-manual-metabolic-review
```

Despite a PASS message, the terminal repeated five warnings beginning
"Could not identify an external compartment by name" and warning that selecting
the compartment with most boundary reactions could be nonsense. The maintainer
questioned those warnings and inspected the exported SBML rather than treating
PASS as a model-quality certificate.

Reported diagnosis: compartments `{'c': ''}`, detected external compartment `c`,
exchanges `EX_a`, `BIOMASS`, `PRODUCT`, no demands, medium `{'EX_a': 10.0}`.
The source used a single intracellular substrate for exchange and drains.
COBRApy therefore treated the cytoplasm as external. Numeric optimization of
that simplified network remained consistent, but its structure/classification
was misleading. `parsing_warnings: []` described only captured Python warnings;
the visible compartment messages came through library logging.

## Corrected architecture and analytical checks

The shared base fixture now has `a_e` in named extracellular `e` and `a_c` in
named cytoplasm `c`. `EX_a` consumes `a_e`, bounds (-10, 0); `TRANSPORT` converts
`a_e` to `a_c`, bounds (0, 1000); `BIOMASS` drains `a_c`, bounds (0, 1000), and
is the maximized objective. The domain recipe adds the PRODUCT drain and
`synthetic_g1 or synthetic_g2` biomass GPR. These are synthetic pseudo-reactions,
not a curated organism model or biochemical biomass equation.

Balances are `-v_EX_a - v_TRANSPORT = 0` and
`v_TRANSPORT - v_BIOMASS - v_PRODUCT = 0`; hence biomass plus product equals
substrate uptake. At uptake seven with minimum growth four, product is at most
three. This algebra is a documented analytical check, not a new human experiment.

| Quantity | Original / diagnostic observation | Maintainer-observed corrected result |
|---|---|---|
| Compartments | Only c, unnamed | e extracellular; c cytoplasm |
| Boundary classification | All three drains counted as exchanges | Exchange EX_a; demands BIOMASS and PRODUCT |
| Domain inventory | Three reactions, one metabolite | Four reactions, two metabolites |
| Maximum biomass | 10 | 10 |
| pFBA total absolute flux | 20 | 30, including transport flux 10 |
| pFBA biomass | 10 | 10 |
| FVA at 90% | Historical outputs preserved, not rewritten | EX_a [-10,-9], TRANSPORT [9,10], BIOMASS [9,10], PRODUCT [0,1] |
| Uptake seven, growth minimum four | New corrected-model experiment | Maximum product 3 |
| Restored growth | Original numeric baseline 10 | 10 |

The reported corrected FBA vector was EX_a=-10, TRANSPORT=10, BIOMASS=10,
PRODUCT=0, with optimal status. No original compartment-identification warning
was observed in the maintainer's corrected experiments.

## SBML, knockouts and solver observations

The maintainer reported an SBML round-trip retaining external compartment e,
exchange EX_a, both intracellular demands and growth ten. Reported OR-GPR
results: single-gene knockout ten, double-gene knockout zero, biomass reaction
knockout zero; final restored growth ten. Zero-growth optimal states are not
infeasible states. Infeasible and unbounded controls returned those actual solver
statuses. The infeasible control's UserWarning is expected and differs from the
structural compartment warning.

The unbounded control must open EX_a uptake, TRANSPORT capacity and BIOMASS
capacity. Opening only exchange and biomass leaves transport capped. Normal
execution still requires finite bounds; infinite bounds exist only in the
deliberately invalid control. COBRApy exceptions retain actual solver status.

## Permanent correction and new automated evidence

Fixture-specific checks now assert compartments, classification, stoichiometry,
bounds, objective and medium. They are not imposed on arbitrary real models.
Scoped logging/Python warning evidence labels execution stages and expected
negative controls; handlers and warning state are restored. No global logging
configuration or blanket warning suppression is used.

`gene-deletions.csv` retains its single-gene interface. A supplementary
`knockout-controls.csv` records baseline, both single genes, double gene and
reaction knockout, perturbation type, actual status and predicted biomass.
The new AND-GPR regression is automated requested work, not claimed to be one
of the maintainer's manual experiments. Numeric/structural/biological validity
remain distinct. New regression tests also assert both compartment balances,
SBML preservation, trade-offs, pFBA/FVA, failures and restoration.

## Limits and unresolved review

This is scoped maintainer reproduction and structural self-review with AI
assistance. It does not complete external methodological review, independent
biological validation, real-organism calibration or clinical validation.
Original Codespaces artifacts must be supplied separately for independent hash
verification. RNA-seq and multi-omics checklist states remain NOT_REVIEWED.
Historical Phase 1–4 evidence and agent verdicts remain unchanged. No improved
AI-agent effectiveness is inferred from this correction.
