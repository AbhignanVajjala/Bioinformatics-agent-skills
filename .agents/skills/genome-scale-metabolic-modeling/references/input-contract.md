# Metabolic input contract

Require a licensed, versioned SBML/FBC model, organism/strain, compartments,
reference identifiers, objective reaction/direction, medium and flux units.
Use `model.medium` for uptake constraints and retain the original bounds.

Before reading fluxes, verify a nonempty objective, solver availability,
optimal status, finite objective and flux vector, stoichiometric residuals and
bound violations at a declared numerical tolerance (default 1e-7 in the recipe).
The original Phase 1 gate additionally requires finite input bounds.

Report unbounded and infeasible states as failures of the stated optimization.
They supply no interpretable optimal flux. The deliberately unbounded fixture
uses infinite bounds only to test rejection.
