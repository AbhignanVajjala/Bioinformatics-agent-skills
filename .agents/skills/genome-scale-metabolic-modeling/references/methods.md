# Constraint-based model notes

Authoritative documentation targets (not asserted retrieved during this skill-authoring run):

- [COBRApy documentation](https://cobrapy.readthedocs.io/en/latest/): consult version-matched model IO, media, simulation, deletion and flux-analysis sections; confirm installed solver behavior.
- [SBML specifications](https://sbml.org/documents/specifications/): check the model's declared SBML Level/Version and FBC package version before assuming objectives/bounds were imported correctly.
- [MEMOTE documentation](https://memote.readthedocs.io/): an optional broader consistency and annotation audit for curated metabolic models, not executed merely because a model passes this toy example.

Verify these source pages and relevant release details before citing them as checked. A feasible model can violate mass/energy plausibility through unbalanced internal reactions or permissive exchanges. Stoichiometric steady state does not imply thermodynamic feasibility; consider loopless/thermodynamic methods where the scientific question requires them.

A zero optimal growth value can be a feasible prediction, whereas infeasibility means no vector satisfies all constraints. Neither should be silently replaced with a positive flux. FVA bounds quantify feasible ranges under assumptions rather than confidence intervals. A biomass objective is a modeling choice and may be inappropriate for non-growing or specialized production contexts.
