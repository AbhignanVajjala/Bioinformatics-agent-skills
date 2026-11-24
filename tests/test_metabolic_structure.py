"""Synthetic structure, serialization and solver evidence; not biological validation."""

import json
import logging
import warnings

import numpy as np
import pandas as pd
import pytest

cobra = pytest.importorskip("cobra", exc_type=ImportError)
from cobra.flux_analysis import pfba, flux_variability_analysis  # noqa: E402
from cobra.io import read_sbml_model, write_sbml_model  # noqa: E402
from bioskills.science import toy_model, solve_model, ScientificValidationError  # noqa: E402
from bioskills.domain_workflows import metabolic_recipe, check_fba_status  # noqa: E402
from bioskills.metabolic import validate_toy_structure, metabolic_evidence  # noqa: E402


@pytest.fixture
def model():
    m = toy_model()
    r = cobra.Reaction("PRODUCT")
    r.bounds = (0, 1000)
    r.add_metabolites({m.metabolites.a_c: -1})
    m.add_reactions([r])
    m.reactions.BIOMASS.gene_reaction_rule = "synthetic_g1 or synthetic_g2"
    return m


def snapshot(m):
    return (
        dict(m.compartments),
        {
            r.id: (
                r.bounds,
                {v.id: c for v, c in r.metabolites.items()},
                r.gene_reaction_rule,
                r.objective_coefficient,
            )
            for r in m.reactions
        },
        m.objective.direction,
        dict(m.medium),
    )


def test_structure_roundtrip_and_warning_absence(model, tmp_path):
    with metabolic_evidence() as evidence, evidence.at("roundtrip"):
        assert validate_toy_structure(model, product=True)["external_compartment"] == "e"
        path = tmp_path / "model.xml"
        write_sbml_model(model, str(path))
        restored = read_sbml_model(str(path))
        assert snapshot(model) == snapshot(restored)
        assert validate_toy_structure(restored, product=True)["demands"] == ["BIOMASS", "PRODUCT"]
    assert not any("identify an external compartment" in e["message"] for e in evidence.events)


def test_old_defect_and_logging_capture(model):
    from cobra.medium.boundary_types import find_external_compartment

    old = cobra.Model("original_defect")
    old.add_reactions([cobra.Reaction("EX_a"), cobra.Reaction("BIOMASS")])
    a = cobra.Metabolite("a_c", compartment="c")
    for r in old.reactions:
        r.add_metabolites({a: -1})
    with metabolic_evidence() as evidence, evidence.at("boundary-classification"):
        assert find_external_compartment(old) == "c"
        assert {r.id for r in old.exchanges} == {"EX_a", "BIOMASS"}
        with pytest.raises(ScientificValidationError, match="toy_structure"):
            validate_toy_structure(old)
    assert any(
        e["channel"] == "logging" and "external compartment" in e["message"]
        for e in evidence.events
    )


def test_capture_stages_and_cleanup():
    logger = logging.getLogger("cobra")
    before = (list(logger.handlers), logger.level, logger.propagate, logger.disabled)
    with pytest.raises(RuntimeError), metabolic_evidence() as evidence:
        with evidence.at("negative-control-test"):
            warnings.warn("expected negative", UserWarning)
            logger.warning("library evidence")
        raise RuntimeError("fixture")
    assert (list(logger.handlers), logger.level, logger.propagate, logger.disabled) == before
    assert {e["channel"] for e in evidence.events} == {"logging", "python_warning"}
    assert all(
        e["expected_negative_control"] and e["stage"] == "negative-control-test"
        for e in evidence.events
    )


@pytest.mark.parametrize("uptake,growth,expected", [(10, 0, 10), (10, 5, 5), (10, 9, 1), (7, 4, 3)])
def test_tradeoff_and_two_mass_balances(model, uptake, growth, expected):
    original = snapshot(model)
    with model:
        model.medium = {"EX_a": uptake}
        model.reactions.BIOMASS.lower_bound = growth
        model.objective = "PRODUCT"
        solution = solve_model(model)
        assert solution.objective_value == pytest.approx(expected)
        v = solution.fluxes
        assert -v.EX_a - v.TRANSPORT == pytest.approx(0, abs=1e-7)
        assert v.TRANSPORT - v.BIOMASS - v.PRODUCT == pytest.approx(0, abs=1e-7)
        assert v.BIOMASS + v.PRODUCT == pytest.approx(-v.EX_a)
    assert snapshot(model) == original


def test_pfba_fva_and_restricted_uptake(model):
    assert solve_model(model).objective_value == pytest.approx(10)
    solution = pfba(model)
    assert solution.objective_value == pytest.approx(30)
    assert solution.fluxes.BIOMASS == pytest.approx(10)
    assert solution.fluxes.abs().sum() == pytest.approx(30)
    fva = flux_variability_analysis(model, fraction_of_optimum=0.9, processes=1)
    for r, values in {
        "EX_a": [-10, -9],
        "TRANSPORT": [9, 10],
        "BIOMASS": [9, 10],
        "PRODUCT": [0, 1],
    }.items():
        assert fva.loc[r].to_numpy() == pytest.approx(values)
    with model:
        model.medium = {"EX_a": 5}
        assert solve_model(model).objective_value == pytest.approx(5)
    assert solve_model(model).objective_value == pytest.approx(10)


@pytest.mark.parametrize("rule", ["synthetic_g1 or synthetic_g2", "synthetic_g1 and synthetic_g2"])
def test_gpr_and_knockout_restoration(model, rule):
    model.reactions.BIOMASS.gene_reaction_rule = rule
    original = snapshot(model)
    for gene in model.genes:
        with model:
            gene.knock_out()
            solution = solve_model(model)
            assert solution.status == "optimal"
            assert solution.fluxes.BIOMASS == pytest.approx(0 if " and " in rule else 10)
    with model:
        for gene in model.genes:
            gene.knock_out()
        assert solve_model(model).objective_value == pytest.approx(0)
    with model:
        model.reactions.BIOMASS.knock_out()
        assert solve_model(model).objective_value == pytest.approx(0)
    assert snapshot(model) == original


@pytest.mark.parametrize(
    "failure", ["infeasible", "unbounded", "residual", "bounds", "finite_bounds"]
)
def test_solution_and_finite_bounds_fail_closed(model, failure):
    if failure in {"residual", "bounds"}:
        solution = solve_model(model)
        if failure == "residual":
            solution.fluxes.TRANSPORT = 9
        else:
            solution.fluxes[:] = [
                -11 if r == "EX_a" else (0 if r == "PRODUCT" else 11) for r in solution.fluxes.index
            ]
        with pytest.raises(ScientificValidationError):
            check_fba_status(model, solution)
    elif failure == "infeasible":
        model.medium = {}
        model.reactions.BIOMASS.lower_bound = 1
        with pytest.raises(ScientificValidationError):
            solve_model(model)
    else:
        model.reactions.EX_a.lower_bound = -float("inf")
        if failure == "finite_bounds":
            with pytest.raises(ScientificValidationError, match="reaction_bounds"):
                solve_model(model)
        else:
            model.reactions.TRANSPORT.upper_bound = float("inf")
            model.reactions.BIOMASS.upper_bound = float("inf")
            try:
                solution = model.optimize(raise_error=False)
            except cobra.exceptions.OptimizationError:
                solution = model.solver
            assert solution.status == "unbounded"
            with pytest.raises(ScientificValidationError, match="solver_status"):
                check_fba_status(model, solution)


def test_report_artifact_consistency(tmp_path):
    report = metabolic_recipe(tmp_path)
    assert report["pfba_total_flux_objective"] == pytest.approx(30)
    assert report["uptake7_minimum_growth4_product"] == pytest.approx(3)
    table = pd.read_csv(tmp_path / "knockout-controls.csv")
    assert json.loads(table.to_json(orient="records")) == report["knockout_controls"]
    assert table.status.tolist() == ["optimal"] * 5
    assert table.predicted_biomass_flux.tolist() == pytest.approx([10, 10, 10, 0, 0])
    assert len(pd.read_csv(tmp_path / "gene-deletions.csv")) == 2
    assert report["inventory"]["reactions"] == 4 and report["inventory"]["metabolites"] == 2
    assert any(
        e["expected_negative_control"] and "infeasible" in e["message"]
        for e in report["warning_evidence"]
    )
    assert not any(
        "identify an external compartment" in e["message"] for e in report["warning_evidence"]
    )
    assert np.isclose(report["fba"]["max_residual"], 0)
