"""Fixture-specific structure gates and scoped metabolic warning evidence."""

from contextlib import contextmanager
import logging
import warnings

import numpy as np

from bioskills.science import require


class MetabolicEvidence(logging.Handler):
    """Capture cobra logging and Python warnings without changing logger policy."""

    def __init__(self):
        super().__init__(logging.WARNING)
        self.stage = "execution"
        self.events = []

    def emit(self, record):
        self.events.append(
            {
                "channel": "logging",
                "stage": self.stage,
                "expected_negative_control": self.stage.startswith("negative-control"),
                "category": record.name,
                "message": record.getMessage(),
            }
        )

    @contextmanager
    def at(self, stage):
        previous = self.stage
        self.stage = stage
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    yield
                finally:
                    self.events.extend(
                        {
                            "channel": "python_warning",
                            "stage": stage,
                            "expected_negative_control": stage.startswith("negative-control"),
                            "category": item.category.__name__,
                            "message": str(item.message),
                        }
                        for item in caught
                    )
        finally:
            self.stage = previous


@contextmanager
def metabolic_evidence():
    logger = logging.getLogger("cobra")
    recorder = MetabolicEvidence()
    logger.addHandler(recorder)
    try:
        yield recorder
    finally:
        logger.removeHandler(recorder)
        recorder.close()


def validate_toy_structure(model, *, product=False):
    """Validate this synthetic fixture only, never an arbitrary organism model."""
    from cobra.medium.boundary_types import find_external_compartment
    from cobra.util.array import create_stoichiometric_matrix
    from cobra.util.solver import linear_reaction_coefficients

    expected = {"EX_a": {"a_e": -1}, "TRANSPORT": {"a_e": -1, "a_c": 1}, "BIOMASS": {"a_c": -1}}
    if product:
        expected["PRODUCT"] = {"a_c": -1}
    require(
        model.compartments == {"e": "extracellular", "c": "cytoplasm"},
        "toy_structure",
        "Synthetic fixture requires named e/c compartments.",
    )
    require(
        {m.id: m.compartment for m in model.metabolites} == {"a_e": "e", "a_c": "c"},
        "toy_structure",
        "Synthetic metabolite compartments differ.",
    )
    require(find_external_compartment(model) == "e", "toy_structure", "Wrong external compartment.")
    require(
        {r.id for r in model.exchanges} == {"EX_a"},
        "toy_structure",
        "Wrong exchange classification.",
    )
    demands = {"BIOMASS", "PRODUCT"} if product else {"BIOMASS"}
    require(
        {r.id for r in model.demands} == demands, "toy_structure", "Wrong demand classification."
    )
    require(
        {r.id: {m.id: v for m, v in r.metabolites.items()} for r in model.reactions} == expected,
        "toy_structure",
        "Synthetic stoichiometry differs.",
    )
    matrix = create_stoichiometric_matrix(model)
    wanted = np.array(
        [[expected[r.id].get(m.id, 0) for r in model.reactions] for m in model.metabolites]
    )
    require(np.array_equal(matrix, wanted), "toy_structure", "Stoichiometric matrix differs.")
    require(set(model.medium) == {"EX_a"}, "toy_structure", "Unexpected medium exchange.")
    require(
        all(r.bounds == ((-10, 0) if r.id == "EX_a" else (0, 1000)) for r in model.reactions),
        "toy_structure",
        "Baseline fixture bounds differ.",
    )
    require(
        {r.id: v for r, v in linear_reaction_coefficients(model).items()} == {"BIOMASS": 1}
        and model.objective.direction == "max",
        "toy_structure",
        "Baseline objective differs.",
    )
    return {
        "status": "PASS",
        "scope": "synthetic_fixture_only",
        "external_compartment": "e",
        "exchanges": ["EX_a"],
        "demands": sorted(demands),
        "stoichiometric_matrix": matrix.tolist(),
        "metabolite_order": [m.id for m in model.metabolites],
        "reaction_order": [r.id for r in model.reactions],
        "biological_plausibility": "NOT_ASSESSED",
        "independent_biological_validation": "NOT_RUN",
    }
