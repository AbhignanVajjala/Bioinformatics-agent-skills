"""Executable, scoped domain recipes built on the Phase 1 scientific gates."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from bioskills.omics import cross_view_analysis  # noqa: F401 - public compatibility import
from bioskills.science import (
    ScientificValidationError,
    require,
    solve_model,
    toy_model,
)


def check_fba_status(model, solution, *, tolerance=1e-7):
    """Validate an existing solution before reading its flux as a prediction."""
    from cobra.util.array import create_stoichiometric_matrix
    from cobra.util.solver import linear_reaction_coefficients

    require(np.isfinite(tolerance) and tolerance > 0, "tolerance", "Positive tolerance required.")
    require(bool(linear_reaction_coefficients(model)), "objective", "Nonzero objective required.")
    require(
        solution.status == "optimal",
        "solver_status",
        "No optimal solution for flux interpretation.",
    )
    flux = solution.fluxes.reindex([reaction.id for reaction in model.reactions]).to_numpy()
    require(np.isfinite(flux).all(), "flux", "Nonfinite or missing flux.")
    residual = create_stoichiometric_matrix(model) @ flux
    violation = max(
        max(reaction.lower_bound - value, value - reaction.upper_bound, 0)
        for reaction, value in zip(model.reactions, flux, strict=True)
    )
    max_residual = float(np.max(np.abs(residual), initial=0))
    require(max_residual <= tolerance, "mass_balance", "Stoichiometric residual exceeds tolerance.")
    require(violation <= tolerance, "bounds", "Flux violates reaction bounds.")
    require(np.isfinite(solution.objective_value), "objective", "Nonfinite objective.")
    return {
        "status": "PASS",
        "max_residual": max_residual,
        "max_bound_violation": float(violation),
        "tolerance": tolerance,
        "objective": float(solution.objective_value),
    }


def metabolic_recipe(output: Path):
    from bioskills.metabolic import metabolic_evidence

    with metabolic_evidence() as evidence:
        with evidence.at("execution"):
            report = _metabolic_recipe(output, evidence)
    report["warning_evidence"] = evidence.events
    return report


def _metabolic_recipe(output: Path, evidence):
    """SBML round trip, GPR-aware perturbations and feasibility controls on a toy."""
    import cobra
    from cobra.flux_analysis import flux_variability_analysis, pfba, single_gene_deletion
    from cobra.io import read_sbml_model, write_sbml_model

    require(not output.exists() or not any(output.iterdir()), "output", "Use an empty directory.")
    output.mkdir(parents=True, exist_ok=True)
    model = toy_model()
    model.reactions.BIOMASS.gene_reaction_rule = "synthetic_g1 or synthetic_g2"
    product = cobra.Reaction("PRODUCT")
    product.bounds = (0, 1000)
    product.add_metabolites({model.metabolites.a_c: -1})
    model.add_reactions([product])
    from bioskills.metabolic import validate_toy_structure

    structure_before = validate_toy_structure(model, product=True)
    original_bounds = {r.id: r.bounds for r in model.reactions}
    file = output / "synthetic-model.xml"
    write_sbml_model(model, str(file))
    with evidence.at("sbml-load"):
        model = read_sbml_model(str(file))
    with evidence.at("boundary-classification"):
        structure_after = validate_toy_structure(model, product=True)
    require(structure_before == structure_after, "roundtrip", "SBML structure changed.")
    require(
        model.reactions.BIOMASS.gene_reaction_rule == "synthetic_g1 or synthetic_g2",
        "roundtrip",
        "SBML GPR changed.",
    )
    model.solver = "glpk"
    baseline = solve_model(model)
    baseline_check = check_fba_status(model, baseline)
    medium = dict(model.medium)
    parsimonious = pfba(model, fraction_of_optimum=1)
    # pFBA's objective is total absolute flux. Compare original biomass flux.
    require(parsimonious.status == "optimal", "pfba", "pFBA did not optimize.")
    fva = flux_variability_analysis(model, fraction_of_optimum=0.9, processes=1)
    fva.to_csv(output / "fva.csv")
    gene_deletions = single_gene_deletion(model, processes=1)
    gene_deletions.assign(ids=gene_deletions.ids.map(lambda ids: ",".join(sorted(ids)))).to_csv(
        output / "gene-deletions.csv", index=False
    )
    with model:
        model.genes.synthetic_g1.knock_out()
        gene_one = solve_model(model).objective_value
        model.genes.synthetic_g2.knock_out()
        gene_both = solve_model(model).objective_value
    with model:
        model.reactions.BIOMASS.knock_out()
        reaction_deleted = solve_model(model).objective_value
    tradeoff = []
    for minimum_growth in (0, 5, 9):
        with model:
            model.reactions.BIOMASS.lower_bound = minimum_growth
            model.objective = "PRODUCT"
            tradeoff.append(
                {"minimum_growth": minimum_growth, "product": solve_model(model).objective_value}
            )
    with model:
        model.medium = {"EX_a": 7}
        model.reactions.BIOMASS.lower_bound = 4
        model.objective = "PRODUCT"
        uptake7_product = solve_model(model).objective_value
    with model:
        model.medium = {"EX_a": 5}
        restricted = solve_model(model).objective_value
    with model:
        model.medium = {}
        model.reactions.BIOMASS.lower_bound = 1
        with evidence.at("negative-control-infeasible"):
            infeasible = model.optimize(raise_error=False)
        try:
            check_fba_status(model, infeasible)
        except ScientificValidationError:
            pass
        else:
            raise AssertionError("Infeasible solution was interpreted")
    with model:
        # A deliberately invalid open source and uncapped drain demonstrate unbounded LP behavior.
        model.reactions.EX_a.lower_bound = -float("inf")
        model.reactions.TRANSPORT.upper_bound = float("inf")
        model.reactions.BIOMASS.upper_bound = float("inf")
        with evidence.at("negative-control-unbounded"):
            try:
                unbounded = model.optimize(raise_error=False)
            except cobra.exceptions.OptimizationError:
                # COBRApy refuses to construct a Solution for an unbounded LP.
                unbounded = model.solver
        unbounded_status = unbounded.status
        require(unbounded.status == "unbounded", "fixture", "Unbounded control not demonstrated.")
        try:
            check_fba_status(model, unbounded)
        except ScientificValidationError:
            pass
        else:
            raise AssertionError("Unbounded solution was interpreted")
    knockout_controls = []
    for label, genes, reaction in (
        ("baseline", [], None),
        ("single_g1", ["synthetic_g1"], None),
        ("single_g2", ["synthetic_g2"], None),
        ("double_gene", ["synthetic_g1", "synthetic_g2"], None),
        ("biomass_reaction", [], "BIOMASS"),
    ):
        with model:
            for gene in genes:
                model.genes.get_by_id(gene).knock_out()
            if reaction:
                model.reactions.get_by_id(reaction).knock_out()
            solution = solve_model(model)
            knockout_controls.append(
                {
                    "control": label,
                    "perturbation_type": "reaction"
                    if reaction
                    else ("gene" if genes else "baseline"),
                    "status": solution.status,
                    "predicted_biomass_flux": float(solution.fluxes.BIOMASS),
                }
            )
    import pandas as pd

    pd.DataFrame(knockout_controls).to_csv(output / "knockout-controls.csv", index=False)
    restored = solve_model(model).objective_value
    validate_toy_structure(model, product=True)
    require(
        {r.id: r.bounds for r in model.reactions} == original_bounds,
        "restoration",
        "Reaction bounds changed.",
    )
    require(
        model.medium == medium and np.isclose(restored, baseline.objective_value),
        "restoration",
        "Temporary model changes persisted.",
    )
    require(
        np.isclose(gene_one, 10) and np.isclose(gene_both, 0) and np.isclose(reaction_deleted, 0),
        "gpr",
        "OR GPR control failed.",
    )
    return {
        "status": "PASS",
        "analysis_status": "EXECUTED",
        "synthetic": True,
        "inventory": {
            "reactions": len(model.reactions),
            "metabolites": len(model.metabolites),
            "genes": len(model.genes),
            "compartments": model.compartments,
        },
        "parsing_warnings": [
            event["message"] for event in evidence.events if event["stage"] == "sbml-load"
        ],
        "structure": structure_after,
        "report_version": 2,
        "knockout_controls": knockout_controls,
        "uptake7_minimum_growth4_product": float(uptake7_product),
        "medium": medium,
        "exchange_bounds": {r.id: list(r.bounds) for r in model.exchanges},
        "fba": baseline_check,
        "pfba_total_flux_objective": parsimonious.objective_value,
        "pfba_biomass": float(parsimonious.fluxes.BIOMASS),
        "fva_fraction": 0.9,
        "single_gene_growth": gene_one,
        "double_gene_growth": gene_both,
        "reaction_deletion_growth": reaction_deleted,
        "restricted_medium_growth": restricted,
        "tradeoff": tradeoff,
        "infeasible_control": infeasible.status,
        "unbounded_control": unbounded_status,
        "restored_growth": restored,
        "limitations": [
            "Arbitrary toy flux units and synthetic GPRs",
            "Steady-state predictions require biological validation",
            "Warnings and cobra logging are scoped evidence, not a biological quality certificate",
        ],
    }
