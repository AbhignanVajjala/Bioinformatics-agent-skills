"""Solve a deliberately tiny synthetic constraint model with COBRApy/GLPK."""

import argparse
from pathlib import Path
import warnings
import numpy as np
from cobra.io import save_json_model
from cobra.flux_analysis import pfba, flux_variability_analysis
from bioskills.science import (
    ScientificValidationError,
    begin_run,
    finish_run,
    solve_model,
    toy_model,
    write_report,
    write_claims,
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
if args.output.exists() and any(args.output.iterdir()):
    parser.error(
        "Output directory must be empty; preserve prior run artifacts and choose a new path."
    )
args.output.mkdir(parents=True, exist_ok=True)
run = begin_run()
model = toy_model()
save_json_model(model, str(args.output / "model.json"))
solution = solve_model(model)
assert np.isclose(solution.objective_value, 10)
parsimonious = pfba(model)
assert parsimonious.status == "optimal" and np.isclose(parsimonious.fluxes.BIOMASS, 10)
fva = flux_variability_analysis(model, fraction_of_optimum=1, processes=1)
assert np.allclose(fva.loc["BIOMASS"], [10, 10])
fva.to_csv(args.output / "fva.csv")
solution.fluxes.to_csv(args.output / "fba.csv")
parsimonious.fluxes.to_csv(args.output / "pfba.csv")
with model:
    model.reactions.EX_a.lower_bound = -5
    sensitivity = solve_model(model)
    assert np.isclose(sensitivity.objective_value, 5)
with model:
    model.reactions.EX_a.lower_bound = 0
    model.reactions.BIOMASS.lower_bound = 1
    save_json_model(model, str(args.output / "infeasible-model.json"))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            solve_model(model)
    except ScientificValidationError as exc:
        negative = str(exc)
    else:
        raise AssertionError("Infeasible model accepted")
report = {
    "status": "PASS",
    "solver": "GLPK",
    "fba_objective": float(solution.objective_value),
    "biomass_at_uptake_5": float(sensitivity.objective_value),
    "negative_control": {"status": "PASS", "detected": negative},
    "limitations": [
        "Synthetic one-substrate model; not genome-scale or organism-specific",
        "Arbitrary toy flux units, no calibrated biomass or maintenance",
        "No measured phenotype, GPR, enzyme capacity or thermodynamic validation",
        "pFBA minimizes total absolute flux; its objective is not the biomass objective",
    ],
}
write_report(args.output, run, report)
write_claims(
    args.output / "claims.json",
    [
        {
            "claim": "Toy biomass flux optimum equals allowed substrate uptake",
            "claim_type": "predicted",
            "status": "PASS",
            "source_or_artifact": "fba.csv",
            "analysis_run_id": run["run_id"],
            "verification_method": "COBRApy/GLPK optimization, steady-state residual, sensitivity and infeasibility checks",
            "limitations": report["limitations"],
            "reviewer": "automated",
        }
    ],
)
finish_run(
    run,
    args.output,
    [args.output / "model.json", Path(__file__)],
    {"uptake_bound": 10, "objective": "BIOMASS", "solver": "glpk", "fva_fraction_of_optimum": 1},
)
print(
    f"PASS: FBA objective={solution.objective_value}; pFBA/FVA, sensitivity and infeasibility checked. Artifacts: {args.output}"
)
