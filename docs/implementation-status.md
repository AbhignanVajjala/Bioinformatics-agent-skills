# Implementation status

## Phase 2 milestone 3 — 2026-11-18

Added deterministic extraction of staged skill-file reads from saved Codex JSONL.
The offline `--inspect-report` command validates saved manifest, rubric, skill and
attempt hashes and leaves archived execution evidence and judgments unchanged.
The replay verified all ten traces and confirmed four file reads across attempts
002, 004 and 008. The
[provenance record](../evals/reports/agent-benchmark-provenance.md) links each turn
to its prompt, response, expected behavior and criterion evidence. All 59 scored
criteria and 75 verbatim excerpts were located in the ten score records and
their saved responses.

The existing `evals/reports/agent-benchmark-scores.json` is valid JSON, tracked
in Git and unchanged. The pilot remains 0 PASS, 4 FAIL and 6 BLOCKED. Activation
is unobservable in these traces, and behavioral judgments remain provisional
pending independent human methodological review. No model session was started.

`python -m pytest -q --junitxml artifacts/pilot-review/milestone3-pytest.xml`
passed **111 tests, zero failures or skips** in the Python 3.12.10 environment.
The JUnit XML SHA-256 is
`00a0479c3b4da2000554a24c1ca2bf7ef31b4fe5a22f8d66dde3b0108bb50a9e`.
Ruff lint and format checks, `python scripts/validate_skills.py` (13 skills,
zero errors), and `python scripts/build_catalog.py --check` passed. A second
offline replay produced identical output. The offline plan still enumerated
114 turns as `NOT_RUN`.

## Phase 2 pilot review — 2026-11-18

Reviewed the saved ten-turn pilot from Codex CLI `0.168.0`. All ten executions
completed. The provisional rubric review found four scientific failures and
six trigger judgments blocked by unverified activation. Both enrichment
responses omitted multiplicity control. Both survival responses omitted an
explicit estimand, censoring assumptions and diagnostics. Four skill-file accesses
across three turns were observable in the raw traces. Activation remains unverified.
Independent human methodological review is pending.
[Pilot review](../evals/reports/agent-benchmark-summary.md) and
[criterion scores](../evals/reports/agent-benchmark-scores.json).

No model sessions were started for this review. The source report, prompts,
event streams and responses were checked in place. The review files include
short excerpts, verified hashes and nonsensitive metadata.
`python -m pytest -q --junitxml artifacts/pilot-review/pytest.xml` passed 97 tests
with no failures or skips in the existing Python 3.12.10 virtual environment.
Ruff lint and format checks, `python scripts/validate_skills.py` and
`python scripts/build_catalog.py --check` passed.

## Codex CLI 0.168.0 compatibility — 2026-11-18

Removed the requirements-only `windows.require_mxc` CLI override. The runner
selects MXC explicitly, keeps strict config for `exec`, and blocks execution
when the read-only isolation probe fails. Codex documents that explicit MXC
selection fails if MXC is unavailable or disallowed.
[Windows sandbox configuration](https://learn.chatgpt.com/docs/windows/windows-sandbox).

`python -m pytest -q --junitxml artifacts/codex-0168-compat/pytest.xml` passed
**97 tests, zero failures or skips** with Python 3.12.10. Ruff lint and format
checks, `python scripts/validate_skills.py` (13 skills, zero errors) and
`python scripts/build_catalog.py --check` passed. The regression checks the
0.168.0 argument contract offline and verifies that a rejected MXC probe blocks
execution even if it prints the success marker. The installed CLI was
`0.169.0-alpha.11.1`. Its no-model command
`python scripts/run_agent_evals.py --probe --output-dir artifacts/codex-0168-compat/probe`
returned `ISOLATION_OK` (report SHA-256
`19cdc08aa718eea3a4afb32b24a0ad3d8cb92cbaff9b042a9c753f5b1f5e2d3e`).
The 0.168.0 executable and model inference were untested in this checkpoint.

## Phase 2 milestone 2 — 2026-11-18

**BLOCKED at ChatGPT sign-in.** The native Windows MXC isolation check passed
from a host process, and no model turn or scientific pilot was executed. This
checkpoint starts from `fb438986bb9076a70aaa94e1f3369760462953dd`. Runbook and
pilot review criteria are in [development progress](development-progress.md).

Diagnostics used Windows 25H2 build 26200.9974, PowerShell 7.6.9, Python 3.14.8,
and `codex-cli 0.169.0-alpha.11.1` from the installed Windows app. Commands below
are from the checkout with the corresponding existing virtual environment active.
Evidence directories are under the ignored `artifacts/phase2-milestone2/`.

| Command and context | Result and evidence directory |
|---|---|
| `python scripts/run_agent_evals.py --probe --output-dir artifacts/phase2-milestone2/managed` in the managed Codex shell | Exit 1. `native MXC is unavailable on this executor`. Report under `managed/agent-eval-d0a4eb4a6f1c435c8d47594abd3aa75a/`. |
| Same probe from a host process with `--output-dir artifacts/phase2-milestone2/host` | Exit 1. `MXC requires nonempty Unicode host SystemDrive`. Report under `host/agent-eval-32ecdfe119814fe2898b3946baa6f501/`. |
| Host probe with `SystemDrive` restored and `--output-dir artifacts/phase2-milestone2/host-systemdrive` | Exit 1. MXC's explicit command environment lacked `SYSTEMROOT`. Report under `host-systemdrive/agent-eval-9ad5f15bb8344e84bc0aa91887bdd8a0/`. |
| Host probe with both corrections and `--output-dir artifacts/phase2-milestone2/host-final` | Exit 0, `ISOLATION_OK`. Read inside succeeded. Sibling read and in-workspace write were denied. Report under `host-final/agent-eval-55a01739982b4c6586b412cc2f1a0803/`. |
| `python scripts/run_agent_evals.py --execute --smoke --model gpt-6-sol --codex-home $authCheck --output-dir artifacts/phase2-milestone2/smoke` from a host process with a freshly created dedicated auth home | Exit 1. Isolation exited 0 and login status exited 1 with `chatgpt_authenticated: false`. Smoke `BLOCKED`, adjudication `NOT_RUN`. Report under `smoke/agent-eval-94e7f1b372a3487aaa8d12332ed0e442/`. |

The messages identify a limitation of the managed executor and two separate
runner environment omissions on the host. The user config declares Windows
`elevated` mode. The probes selected MXC per invocation and left that config
intact. The corrected test still uses
`windows.require_mxc=true`, the confined read-only profile, disabled tool
networking, and `shell_environment_policy.inherit="none"`. The successful probe
tested filesystem boundaries. It did not run a model or verify network behavior
end to end. No login credentials were read into evaluation artifacts.

`wsl.exe --list --verbose` returned `Wsl/E_ACCESSDENIED` from the managed shell
and listed Ubuntu as WSL version 2 when run on the host. The host inventory found
`/usr/bin/bwrap`, Python 3.14.4, and a `codex` path in the Windows app's mounted
resources. The runner requires Windows MXC for live execution, and no Linux
Codex sandbox test was run.

| Offline validation command | Observed result |
|---|---|
| `python -m pytest -q --junitxml artifacts/phase2-milestone2/pytest-final.xml` | **95 passed, 0 failed, 0 skipped**, Python 3.12.10 with the Milestone 1 dependency environment and local caches |
| `ruff check .` and `ruff format --check .` | Both exit 0, 14 Python files formatted |
| `python scripts/validate_skills.py` and `python scripts/build_catalog.py --check` | Both exit 0, 13 skills and 0 structural or link errors |
| `python scripts/run_evals.py --output artifacts/phase2-milestone2/deterministic.json` | Exit 0, seven tool scenarios `PASS`, five agent scenarios `NOT_RUN` |
| `python scripts/run_agent_evals.py --output-dir artifacts/phase2-milestone2/plans` | Exit 0, all 114 benchmark turns `NOT_RUN` |
| `python scripts/run_agent_evals.py --pilot --output-dir artifacts/phase2-milestone2/pilot-plan` | Exit 0, five scenarios and ten planned turns, all `NOT_RUN` |

Evidence SHA-256 values are below. Live responses, skill access, token usage and
behavioral evaluation have no evidence because inference did not start.

| Artifact | SHA-256 |
|---|---|
| Corrected host probe report | `f98a832259ec53762104a63d3ace025b9c5caaa9c987ba8da2f651d754ac2a51` |
| Blocked smoke report | `c8d2990d059437f9344db2e86506a6537fa0775075fdff7f7dee5fa814195f6d` |
| Offline pilot plan report | `d77f3ab621748dc62a6233ae6341ace5f2945665f497094f09adcb9305e9c7a8` |
| Final pytest XML | `a1c90c322471902ddbb2a7275fb788785fff0224d42775bfa564b66512f15e0f` |

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
