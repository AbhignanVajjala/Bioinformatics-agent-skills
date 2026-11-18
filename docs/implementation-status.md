# Implementation status

## Phase 2 milestone 1 — 2026-11-18

The local Windows branch `phase2-agent-evaluations` starts from `7ba97ae`.
The new [agent evaluation runner](../scripts/run_agent_evals.py) plans the 52 trigger
and five scientific agent scenarios in baseline and skill-enabled configurations.
It has an explicit live Codex CLI mode with preflight isolation, fresh sessions
and structured execution evidence. The runner leaves behavioral adjudication
`NOT_RUN` until review. See [development progress](development-progress.md) for
operation, evidence semantics, and remaining work.

Validation used Windows build 26200 and PowerShell 7.6.9. The installed Python
3.14.8 was used for the dependency-light harness check. For the full suite, a
portable Python 3.12.10 and an isolated virtual environment were placed in
`artifacts/phase2-validation/`. The runtime came from the official Python NuGet
package (archive SHA-256
`0eb85c2dfccccf1b17352de4c397f69194035b7d37149eacc16f1147d93de3b8`).
The project used the versions in `requirements-tested.txt` plus Windows
`colorama==0.4.6`. During Phase 1 checks, `PYTHONUTF8=1` handled the checkout's UTF-8
materials, `PYTHONPATH` pointed to `src`, and `XDG_CACHE_HOME` and `MPLCONFIGDIR`
used ignored artifact paths. Commands below use the corresponding virtual
environment's interpreter.

| Command | Observed result |
|---|---|
| `python -m pytest -q tests/test_agent_evals.py --junitxml artifacts/phase2-validation/harness-py314.xml` | **22 passed, 0 failed, 0 skipped** with Python 3.14.8 |
| `python -m pytest -q --junitxml artifacts/phase2-validation/pytest-final.xml` | **94 passed, 0 failed, 0 skipped** with Python 3.12.10, including all 72 Phase 1 tests |
| `python -m pip check` | Exit 0, no broken requirements |
| `ruff check .` and `ruff format --check .` | Exit 0 for both; 14 Python files formatted |
| `python scripts/validate_skills.py` | Exit 0, 13 skills, 0 structural or link errors |
| `python scripts/build_catalog.py --check` | Exit 0 |
| `python examples/bulk-rnaseq/run.py --output artifacts/phase2-validation/bulk-rnaseq` | Exit 0, readiness/QC PASS, DE NOT_RUN |
| `python examples/multiomics/run.py --output artifacts/phase2-validation/multiomics` | Exit 0, specimen reconciliation and descriptive concordance PASS |
| `python examples/metabolic-modeling/run.py --output artifacts/phase2-validation/metabolic-modeling` | Exit 0, FBA objective 10.0, pFBA/FVA, sensitivity and infeasibility checked |
| `python scripts/run_evals.py --output artifacts/phase2-validation/deterministic.json` | Exit 0, **7 tool scenarios PASS** across 11 pytest cases and **5 agent scenarios NOT_RUN** |
| `python scripts/run_agent_evals.py --output-dir artifacts/phase2-validation/plans` | Exit 0, **114 planned turns NOT_RUN** |
| `python scripts/run_agent_evals.py --probe --output-dir artifacts/phase2-validation/preflight` | Exit 1, local CLI `0.169.0-alpha.11.1` found, native MXC unavailable on this executor |

The initial Python 3.14.8 harness run had 13 passes and six failures. Windows
platform reporting unexpectedly invoked a shell, and the test temp directory
inside the checkout violated the intended isolation checks. The runner now
gets the Windows version without a subprocess, and validation uses the native
temporary directory for pytest fixtures. The final runs above have no test failures.

Local evidence under `artifacts/phase2-validation/` includes example artifacts,
`pytest-final.xml` with SHA-256
`91c2dc5ca182c97fecee80174f2d25bf8d60fcce7f15296697dfc38ddc7941b4`,
and `deterministic.json` with SHA-256
`cb455861bc2cba1ce78ebac0a7261cdeb012c8ad71739c5bf1c9d1c694101272`.
The final plan is `plans/agent-eval-0cd6d51fadb249bd8a2a5019010db572/report.json`
with SHA-256 `34f3aa47c02059d41545446201ca29cbbaf7a5f73753a0d1bfee60f4933ff7fd`.
The CLI preflight logs are under
`preflight/agent-eval-4e6d9076b1494141b37c85f9568291d1/`. That early preflight
used the same MXC configuration as the final runner. Its `isolation.stderr`
SHA-256 is `e01fec220084dcad78090dbc2c818a5c9f4f565e65b8cc26c65f479ffe497ccb`.
Live response collection, skill discovery, activation and performance remain
`NOT_RUN`. The local sandbox probe failed before any login check or inference.

## Phase 1 record — 2026-11-17

**Experimental prototype with executed synthetic scientific checks.** Original implementation
is present in the existing checkout. At the first milestone no commit, push, package publication or deployment
was performed. HEAD was then unborn; milestone provenance recorded `git_revision: null`
and source hashes. The initial-publication preparation below supersedes that Git state.

## Specification and reference inspection

The complete master prompt was read and adopted for implementation. Reattached inputs
were verified identical by SHA256: specification
`3d353a670309703446a29d571e947b6b157f90ea9d071184e497b765198fb8bd`, archive
`bdb141719e8f00d8eecb97d130e274027d2379b8cc925fe7cfb08c48d66d0a65`.
The archive was inspected read-only. No redistribution license was found and no archive
skill bodies, scripts, templates or assets were copied. See [reference analysis](reference-analysis.md).
The project MIT license covers original content and synthetic fixtures only.

The current Agent Skills specification was read from its official GitHub source.
Requested documentation hosts and the Codex documentation target returned HTTP 403.
Official Codex repository docs link to that blocked target. Format compatibility was
checked locally; live Codex discovery is NOT_TESTED. External scientific source URLs
are supplied with access qualifications; retrieval outcomes are in
[reference checks](../references/source-checks.json). Unretrieved pages are not verified citations.

## Implemented inventory

| Capability | Implemented / executed scope |
|---|---|
| Foundation skills (10) | scientific-prompt-engineering; scientific-context-engineering; research-specification; research-task-decomposition; source-grounded-scientific-reasoning; scientific-agent-orchestration; scientific-debugging; verification-before-scientific-claims; research-reproducibility-audit; bioinformatics-skill-authoring |
| Domain skills (3) | bulk-rnaseq-differential-expression; multiomics-integration; genome-scale-metabolic-modeling, each with method references and limitations |
| Personas (4) | Biostatistician, Computational Biologist, Biological Data Curator, Reproducibility Auditor; operational instructions, not automatic agents |
| Workflows (3) | hypothesis-to-analysis, multi-omics, metabolic-modeling; entry/exit gates, ownership, recovery and handoffs |
| Artifact contracts (7) | research_spec, dataset_manifest, analysis_run, validation_report, scientific_claim_ledger, methods_report, handoff; JSON Schemas and templates |
| Code | Scientific input/design/identity/leakage/optimization gates; provenance and claim helpers; structural validator; generated catalog; evaluation runner |
| Maintenance | README, installation, authoring worksheet, scientific integrity, license/citation/contribution/security/conduct, issue/PR templates, lint/test/example CI definition |

All 13 skills are **experimental**. Structural validity and content review are implemented;
model-driven skill effectiveness is not established. [Catalog](catalog.md) links every skill;
[repository tree](repository-tree.md) inventories source files.

## Execution evidence

Tested Linux x86_64, Python 3.12.14, local venv. Direct dependency pins are in pyproject.toml;
[requirements-tested.txt](../requirements-tested.txt) records installed transitive versions.
Installation `python -m pip install -e '.[dev,examples]'` succeeded, including COBRApy 0.29.1
and GLPK via swiglpk 5.0.13. No GPU, private data or external AI API used.

Current publication rerun command records, timestamps, stdout, stderr and exit statuses
(the table below records the earlier milestone; rerun evidence supersedes timings):
[verification.json](../evals/reports/publication/verification.json).

| Actual command (venv active, repository root) | Observed result |
|---|---|
| `python -m pip check` | PASS: no broken requirements |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS: 12 Python files formatted |
| `python scripts/validate_skills.py` | PASS: 13 skills, 0 structural/local-link errors |
| `python scripts/build_catalog.py --check` | PASS: generated catalog current |
| `pytest -q --junitxml=evals/reports/pytest.xml` | **72 passed, 0 failed, 0 skipped**, 11.11 s |
| `python examples/bulk-rnaseq/run.py --output artifacts/final/bulk-rnaseq` | PASS, exit 0; six independent samples, design rank 3, count/library QC and PNG; misalignment negative detected; DE NOT_RUN |
| `python examples/multiomics/run.py --output artifacts/final/multiomics` | PASS, exit 0; seven matched specimens, exclusions recorded, four synthetic mapped-feature correlations >0.8; mismatch negative detected; integration model NOT_RUN |
| `python examples/metabolic-modeling/run.py --output artifacts/final/metabolic-modeling` | PASS, exit 0; FBA optimum 10, restricted uptake optimum 5, pFBA/FVA, infeasible negative detected |
| `python scripts/run_evals.py --output evals/reports/latest.json` | **7 tool scenarios PASS, 5 agent scenarios NOT_RUN**; 11 real pytest regression nodes executed across the 7 scenarios; exit 0 |

[JUnit](../evals/reports/publication/pytest.xml) records the 72 tests. These include invalid metadata,
schema fields/statuses/timestamps, count alignment/type/replication/confounding, numeric
categorical batch regression, specimen identity/leakage, solver objective/infeasibility,
evaluation-report integrity and subprocess execution of all three examples. Integration
tests validate all nine run/validation/claim artifacts, their hashes, cross-artifact run
IDs and nonempty-output preservation. Five QA domains remain explicit: biological
interpretation/expert validation is NOT_RUN even when input and computation checks pass.

[Evaluation report](../evals/reports/publication/latest.json) links actual per-case logs/XML.
The 52 trigger cases (two positive/two negative per skill) are supplied and structurally
checked, but **all 52 agent-trigger executions are NOT_RUN**. Do not add these prompts
to the count of passed tests. Five agent-only scientific cases cover citation/injection,
enrichment background, cure overclaims, censoring and unauthorized upload; their expected
behaviors are specified but no model outputs or performance scores were fabricated.

## Investigation and corrections during implementation

- Initial scientific run: 15 passed, 4 failed because COBRApy tried the read-only home cache.
  Supported `XDG_CACHE_HOME` and `MPLCONFIGDIR` overrides fixed this; final checks use
  repository-local `.cache`. Installation/CI document the requirement.
- Numeric batch labels could be treated as continuous. Explicit categorical coding and
  additional regression cases now detect confounded multi-batch designs.
- Review found output overwrite/stale-PASS risk. Examples now reject nonempty output
  directories before writing; subprocess tests confirm earlier files remain byte-identical.
- Intermediate suite: 54 passed, 1 failed because JSON Schema date-time checking needed
  its optional dependency. Added pinned `rfc3339-validator`; invalid timestamps now fail.
- Formatting initially found six files requiring changes. Formatted and reran checks.
- Separate agent implementation/review tasks helped isolate issues; some tasks encountered
  an execution quota interruption after writing files. Root inspected the resulting files,
  completed integration and executed the full suite. This is software review within the
  same assistant workflow, **not independent human scientific peer review**.

## Limitations and unfinished tasks

NOT_RUN: R/Bioconductor DE, a learned MOFA/SNF integrator, external validation,
real genome-scale SBML/FBC biological benchmarking, live agent-trigger evaluation,
hosted GitHub CI, Windows/macOS, fresh cloud-task restoration and independent expert review.
Codex documentation retrieval is BLOCKED by current outbound access; live discovery is
NOT_TESTED. These do not prevent the tested local Python demonstrations.

Synthetic examples prove narrow computations and guards, not truthful source metadata,
adequate statistical power, clinical safety, therapeutic efficacy, causal mechanisms,
real organism predictions or general agent reliability. Partial/missing modalities,
paired/longitudinal designs, many-to-many feature mapping and complex covariates need
broader implementations; current code rejects some unsupported cases conservatively.
No enrichment or survival analysis software is implemented. Agent-only fixtures cannot
stand in for those future scientific validators.

Post-publication priorities are live Codex discovery and real agent-behavior evaluation
of existing skills before adding skills. Subsequent work covers Bioconductor DE,
established integration/curated metabolic models and independent human review.
P1 broader foundation skills/personas/review/debugging/manuscript workflows and P2 domain
expansion remain [planned with acceptance criteria](roadmap.md); no placeholder skills
are shipped for them.

## Initial-publication preparation

Requested scope: audit, fresh validation and a local implementation commit; pushing
requires explicit user approval. Origin fetch and push URLs both resolve to
`https://github.com/AbhignanVajjala/Bioinformatics-agent-skills.git` without embedded
credentials. Read-only remote inspection found an existing main seed commit
`a8bcd7a837b562a87917c46ca7008183afcce17b` containing only the project title in README.md.
The local implementation is based on this commit, preserving its history and title.
A future push must be a normal fast-forward after rechecking remote main; never force-push.

The publication audit and fresh execution results are recorded in
[publication audit](publication-audit.md). Only the reviewed publication evidence snapshot
is included; older runs, analysis outputs, virtual environments and caches stay local.
README claims remain scoped to executed synthetic checks; all skills are experimental.
No new skills were added during preparation.
