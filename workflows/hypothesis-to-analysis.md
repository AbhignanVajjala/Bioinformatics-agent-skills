# Hypothesis to reproducible analysis

Entry: a research question, available-data inventory and permission boundaries. Use the [execution contract](README.md); ownership below names responsibilities, not spawned processes.

| Stage / owner | Required inputs and tools | Output and validation gate | Recovery and next condition |
|---|---|---|---|
| Specify / biostatistician | Question, study type, unit, target population; design review | Research specification: estimand, controls, covariates, exclusions, planned contrasts and limits | Resolve ambiguity; no inferential method choice until unit and estimand are known |
| Discover / curator | Specification, source catalog and access terms; authoritative source lookup when permitted | Candidate manifest with accession/version/license and fitness assessment | Inaccessible or unsuitable sources remain BLOCKED; use authorized synthetic demonstration only if labeled |
| Validate / curator | Frozen files, mapping, assay and reference; parsers/checksums | Manifest, exclusion ledger, exact alignment and provenance | Resolve duplicates/version conflicts; progress only with auditable identities |
| Plan / biostatistician | Validated design and modality; rank/replication/leakage checks | Analysis plan, multiple-testing policy, diagnostic and sensitivity criteria | Non-identifiable contrasts stop; revise question or obtain data |
| Prepare / analyst | Plan, versioned environment and resource estimate; package setup | Recorded versions and successful relevant smoke test | Diagnose dependency/tool failure; mark unavailable methods NOT_RUN |
| Execute and QC / computational biologist | Accepted inputs/plan; domain skill and established tools | Actual analysis_run, figures, diagnostics, check statuses | Failed or scientifically unsuitable outputs block interpretation; preserve failed run and repair root cause |
| Interpret / computational biologist | Outputs, diagnostics and verified contextual sources | Claim ledger separating measured, associated and predicted results | Narrow claims when assumptions fail; unexpected findings prompt investigation |
| Audit / auditor | All artifacts and commands; fresh rerun/hash/schema checks | Validation report, methods report and handoff | Missing evidence blocks completion; reports list unresolved work explicitly |

A synthetic readiness example may complete a readiness question while differential expression remains NOT_RUN. Completion requires artifacts supporting the specified question; it never establishes general biological or clinical validity. High-stakes interpretations require human expert review.
