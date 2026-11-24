# Public bioinformatics data retrieval troubleshooting

Check the actual parser or dependency error, input scale, identifier relationships,
reference version and independent units. Preserve failed evidence. Resolve known
input errors in a new run. Label descriptive or exploratory computations explicitly.

NCBI E-utilities documentation encountered a browser verification page on 2026-11-19. Ensembl lookup documentation returned 403. These earlier releases retain historical NOT_RUN status. Three live provider requests were observed on 2026-11-24 at source 98a9456132fb474996f4c5d566065925ed79551b; Phase 8 adds separately recorded scoped live checks. Transport success alone is insufficient.

Implemented scope and executed test status are recorded in the repository's
Phase 3 development documentation. Successful tests do not establish clinical
validity or general agent behavior.

## Phase 8 failure interpretation

Inspect transport_status separately from validation_status. Do not convert PARTIAL_UNVERIFIED or no-record responses into verified study provenance. Verify summary UIDs and database-specific accession relationships, including SRA XML fragments.
