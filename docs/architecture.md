# Architecture

The library has three independent surfaces: canonical agent instructions in `.agents/skills`, ordinary Python scientific checks and demonstrations, and versioned research artifacts. There is no agent server, required model provider or remote execution service.

Skills define triggers, essential inputs, decisions and evidence gates. Supporting material loads on demand. A skill remains a single source of truth; catalogs summarize it rather than maintaining copies. Personas assign review responsibilities, while workflows order those responsibilities and pass concrete artifacts. Neither file type creates a process or grants permissions.

The Python layer makes narrow, inspectable assertions about inputs and tiny analyses. Established packages perform numerical work; the repository does not replace DESeq2, MOFA or a metabolic solver. Scientific example dependencies are optional to keep structural/schema checks offline and lightweight after installation. PyYAML parses metadata, jsonschema checks artifact structure, pytest tests behavior; numerical libraries and COBRApy support the examples. Tool versions and full runtime evidence must be captured per run.

Seven independent JSON Schema Draft 2020-12 contracts under `schemas/` cover research specifications, datasets, runs, validation, claims, methods and handoffs. Templates contain explicit unexecuted examples, not evidence. Required fields are conservative; optional source accessions and download dates avoid forcing fabricated identifiers onto synthetic data. Schema validation does not replace semantic checks: hash/file agreement, timestamp ordering, legal access and scientific validity require additional review.

A failed gate stops dependent stages. Independent stages can continue. Recovery produces a new run and a recorded change rather than silently replacing inputs or results. Only a fully evidenced claim may reach a report, and expert review requirements survive successful software tests.

The first vertical slice covers bulk RNA-seq readiness, paired multi-omics readiness/exploration and small constraint-based metabolic predictions. See `implementation-status.md` for executed capability inventory and `roadmap.md` for deferred capabilities. All skills start experimental; structural validation alone cannot promote maturity.
