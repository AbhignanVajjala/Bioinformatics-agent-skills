"""Executable, scoped domain recipes built on the Phase 1 scientific gates."""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np

from bioskills.science import (
    ScientificValidationError,
    reconcile_omics,
    require,
    solve_model,
    toy_model,
    validate_matrix,
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
    file = output / "synthetic-model.xml"
    write_sbml_model(model, str(file))
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        model = read_sbml_model(str(file))
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
        model.medium = {"EX_a": 5}
        restricted = solve_model(model).objective_value
    with model:
        model.medium = {}
        model.reactions.BIOMASS.lower_bound = 1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
        model.reactions.BIOMASS.upper_bound = float("inf")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            unbounded = model.optimize(raise_error=False)
        require(unbounded.status == "unbounded", "fixture", "Unbounded control not demonstrated.")
        try:
            check_fba_status(model, unbounded)
        except ScientificValidationError:
            pass
        else:
            raise AssertionError("Unbounded solution was interpreted")
    restored = solve_model(model).objective_value
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
        "parsing_warnings": [str(w.message) for w in recorded],
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
        "unbounded_control": unbounded.status,
        "restored_growth": restored,
        "limitations": [
            "Arbitrary toy flux units and synthetic GPRs",
            "Steady-state predictions require biological validation",
            "SBML warnings captured via Python warnings; library logging may be separate",
        ],
    }


def cross_view_analysis(matrices, mappings, declarations, feature_map):
    """Descriptive matched-feature association after declared assay transformations.

    The finite complete-case policy rejects missing values. No imputation or
    supervised fit is performed, and no prediction performance is reported.
    """
    require(
        set(declarations) == set(matrices) and len(matrices) == 2,
        "modalities",
        "This baseline supports exactly two declared assays.",
    )
    prepared_maps = {}
    for name, mapping in mappings.items():
        require(
            "timepoint" in mapping and mapping.timepoint.notna().all(),
            "timepoint",
            "Declare timepoint for each specimen.",
        )
        require(mapping.specimen_id.is_unique, "duplicate_specimen", "Duplicate specimen.")
        prepared_maps[name] = mapping.copy()
    aligned, audit = reconcile_omics(matrices, prepared_maps)
    names = list(matrices)
    timepoints = {}
    transformed = {}
    for name in names:
        mapping = mappings[name].set_index("specimen_id")
        for specimen, time in mapping.timepoint.items():
            require(
                specimen not in timepoints or timepoints[specimen] == time,
                "timepoint_mismatch",
                "Cross-assay timepoints disagree.",
            )
            timepoints[specimen] = time
        declaration = declarations[name]
        require(
            declaration.get("namespace") and declaration.get("reference"),
            "namespace",
            "Declare feature namespace and annotation release.",
        )
        values = validate_matrix(aligned[name])
        scale = declaration.get("scale")
        if scale == "raw_counts":
            require(
                (values >= 0).all() and (values == np.floor(values)).all(),
                "count_values",
                "RNA count declaration contradicts values.",
            )
            require(
                declaration.get("modality") == "rna" and declaration.get("count_generation"),
                "count_provenance",
                "RNA count-generation provenance required.",
            )
            totals = values.sum(axis=0)
            require((totals > 0).all(), "empty_library", "Zero library.")
            transformed[name] = np.log2(1 + values / totals * 1e6)
        elif scale == "log2_intensity":
            require(
                declaration.get("modality") in {"protein", "metabolite"},
                "modality_scale",
                "Log intensity baseline requires protein or metabolite assay.",
            )
            transformed[name] = values.copy()
        else:
            raise ScientificValidationError("scale: Unsupported or ambiguous assay scale.")
        require((transformed[name].std(axis=1) > 0).all(), "constant_feature", "Constant feature.")
    require(set(feature_map) == set(names), "feature_map", "Explicit cross-view mapping required.")
    require(
        not feature_map.isna().any().any() and all(feature_map[name].is_unique for name in names),
        "feature_map",
        "One-to-one known synthetic mapping required for this baseline.",
    )
    rows = []
    for pair in feature_map.to_dict("records"):
        for name in names:
            require(pair[name] in aligned[name].index, "feature_map", "Unmapped feature.")
        left, right = (transformed[name][aligned[name].index.get_loc(pair[name])] for name in names)
        rows.append({**pair, "pearson_r": float(np.corrcoef(left, right)[0, 1])})
    return {
        "analysis_status": "EXECUTED",
        "method": "descriptive cross-view Pearson association",
        "audit": audit,
        "correlations": rows,
        "declarations": declarations,
        "missingness_policy": "Reject missing/nonfinite values before analysis",
        "transformations": {
            name: (
                "log2(CPM+1)"
                if declarations[name]["scale"] == "raw_counts"
                else "declared log2 intensity unchanged"
            )
            for name in names
        },
        "limitations": [
            "No imputation, inference, MOFA2, SNF or prediction model executed",
            "Pearson association is descriptive and depends on the supplied mapping",
            "Independent biological identity is not established by metadata",
        ],
    }
