# Architecture

The library has three independent surfaces: canonical agent instructions in `.agents/skills`, ordinary Python scientific checks and demonstrations, and versioned research artifacts. There is no agent server, required model provider or remote execution service.

Skills define triggers, essential inputs, decisions and evidence gates. Supporting material loads on demand. A skill remains a single source of truth; catalogs summarize it rather than maintaining copies. Personas assign review responsibilities, while workflows order those responsibilities and pass concrete artifacts. Neither file type creates a process or grants permissions.

The Python layer makes scoped assertions about inputs and synthetic analyses.
NumPy/pandas support count/design and identity gates, SciPy performs Fisher/BH
ORA, and COBRApy/GLPK performs constraint-based optimization. Separate pinned
R/Bioconductor scripts execute DESeq2 and edgeR; the original Python RNA-seq
example remains readiness-only. MOFA2/SNF and a supervised integration model are
not implemented by the cross-view baseline. PyYAML parses metadata, jsonschema
checks artifact structure and pytest verifies declared fixtures. Tool versions
and actual runtime evidence must be captured per run.

Eight JSON Schema Draft 2020-12 contracts under `schemas/` cover research
specifications, datasets, runs, validation, claims, methods, handoffs and
validator reports. Templates are unexecuted examples, not evidence. Optional
source fields avoid fabricated accessions for synthetic data. Schema validation
does not authenticate files or establish legal access or scientific validity.

A failed gate stops dependent stages. Independent stages can continue. Recovery produces a new run and a recorded change rather than silently replacing inputs or results. Only a fully evidenced claim may reach a report, and expert review requirements survive successful software tests.

The collection contains seven domain skills and ten foundation/maintainer
instruction workflows. The universal ZIP curates scientific source, recipes,
schemas, templates and essential user documentation. Development tests, raw
evaluation traces and historical audit records remain outside the ZIP.
The evaluation harness is a separate surface and does not run automatically
when a skill is installed. No model provider is required for direct Python/R use.

See [scientific evidence](scientific-evidence.md),
[development transparency](development-and-ai-assistance.md),
[host compatibility](agent-host-compatibility.md) and the
[technical walkthrough](maintainer-technical-walkthrough.md). The implementation
status records actual execution; the roadmap records deferred work. All skills
remain experimental, with independent human review incomplete.
