# Pathway enrichment and gene identifier mapping troubleshooting

Check the actual parser or dependency error, input scale, identifier relationships,
reference version and independent units. Preserve failed evidence. Resolve known
input errors in a new run. Label descriptive or exploratory computations explicitly.

SciPy 1.15.3 Fisher exact and false_discovery_control API pages were retrieved on 2026-11-19. The implementation includes a known-result Fisher/BH synthetic regression. Ranked enrichment is NOT_RUN.

Implemented scope and executed test status are recorded in the repository's
Phase 3 development documentation. Successful tests do not establish clinical
validity or general agent behavior.

## Phase 8 failure interpretation

Malformed declarations/IDs reject before mapping. Inspect family_audit and excluded_pathways; BH uses eligible_family, retaining eligible zero-overlap pathways. No eligible sets is NOT_RUN, not successful ORA.
