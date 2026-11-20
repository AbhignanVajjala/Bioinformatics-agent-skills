# Implementation status

## Phase 4 research credibility and transparency — 2026-11-20

Baseline: clean synchronized local Windows main
`afd14e927e49a06df3ad7268532769c6e93002fb`. Branch:
`phase4-research-credibility`. Documentation release 0.2.2 presents scientific
scope before distribution, credits Abhignan Vajjala as initiator/maintainer,
retains contributors credit and discloses substantial AI assistance including
OpenAI Codex. It makes no sole-code-authorship or independent-review claim.

Added the host matrix, three-workflow maintainer guide, scientific-evidence
guide, development disclosure, presentation audit and source/claim records.
Human completion fields remain blank/NOT_REVIEWED. The baseline platform census
classifies 152 matched lines in 16 documents: 24 necessary technical references,
125 historical references and three unnecessary single-host framing references.
Historical evidence and technically necessary Codex examples remain intact.

The source-preservation check covers 126 baseline files: all skills, scientific
modules, recipes, examples, tests, schemas, evaluations, AGENTS.md, LICENSE,
scientific requirements and the R workflow. They are unchanged. The original
pilot score file is still tracked, with SHA-256
`fcdfd5c63f98d35a3845678d49dd1725c3f8a41866f245a756fe8702106de916`.
All 17 skills and seven validators retain their original scientific behavior.

Validation used the existing Python 3.12.10 venv, pytest 8.3.5, Ruff 0.11.13,
PyYAML 6.0.2 and jsonschema 4.23.0. Repository tests used `PYTHONUTF8=1`,
`PYTHONPATH=src`, and task-local XDG/Matplotlib cache directories.

| Check / command | Observed result |
|---|---|
| `python -m pytest -q --junitxml artifacts/phase4/pytest.xml` | 219 passed, two skipped, zero failures; 221 collected |
| Packaging/extraction/installed-CLI tests within that suite | 56 passed, one skipped; 57 cases, with actual temporary installation/first-use and schema checks |
| `ruff check .` / `ruff format --check .` | PASS; 30 Python files formatted |
| `python scripts/validate_skills.py` | 17 skills; zero structural/link errors |
| `python scripts/build_catalog.py --check` | PASS |
| `python scripts/sync_modes.py --check` | PASS |
| `python scripts/package_skills.py` / `python scripts/package_skills.py --check` | PASS; one deterministic, extractable universal ZIP |
| Official CFF 1.2.0 JSON Schema validation of parsed CITATION.cff | PASS using existing PyYAML/jsonschema; cffconvert was not installed |
| Claim-ledger JSON Schema validation | Ten scoped records PASS structural validation; automated reviewer non-independent, human approval pending |
| README order/single-download, blank human fields and source-preservation checks | PASS |

The two local skips are `test_metabolic_recipe_executes` (first native
libsbml import blocked by Windows Application Control) and
`test_symlink_resources_rejected` (account cannot create symlinks). Other
executed fixtures passed in this invocation. Fewer skips than the historical
Phase 3 run do not add tests or establish general native-runtime compatibility;
the full SBML recipe remains unexecuted locally in this run. Two warnings were
recorded: the importorskip deprecation warning and expected infeasible solver
warning. No security policies or scientific assertions were changed.

Citation validation retrieved the versioned official schema listed in
`references/phase4-documentation-sources.json`, checked it with
`jsonschema.validators.validator_for(schema).check_schema(schema)`, and
validated the PyYAML-parsed CFF. Schema SHA-256:
`0b8d22140da702d766df318dcff3a91af2f39521298dcf36d76315fd99cc169b`.
No new citation-validation dependency or external schema is vendored.

The regenerated universal ZIP contains **17 skills, 113 files, 324,602 bytes**,
SHA-256 `79bea163748f66e8aa1d710b207c7e7a423ff05fa017839549bfb1be91a7189b`.
It retains the complete scientific inventory and adds six essential citation,
compatibility, disclosure, walkthrough, evidence and integrity documents.
Development audit/history records stay outside the ZIP. One early README write
was interrupted by Windows stdin encoding; the file was restored using UTF-8
file editing, and subsequent decoding, structure and link checks passed.

Existing historical log bodies below are preserved. Hosted Python regression,
fresh Windows/Linux extracted installs and the unchanged pinned R CI remain
publication gates. No agent/model sessions or live scientific data retrieval
were launched. Independent methodological/biological review and broader host
behavioral validation remain incomplete.

At Phase 4 source `1b5c7d2`, [hosted Python/distribution validation](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44726146764)
passed 217 tests with four Windows-only skips and zero failures. Both fresh
Windows/Linux extraction jobs passed isolated dependency/package installation,
module-origin and pip checks, all seven command help interfaces, first-use,
cross-view, metadata dry-run, schema validation and both metabolic examples.
Extracted R execution remained NOT_RUN in these Python jobs and is checked by
the separate pinned R workflow. Their reported ZIP hash matches the value above.
The README labels the original publication inventory as historical; its source
file and all historical records are preserved.

## Phase 3.11 universal distribution — 2026-11-19

Started from clean synchronized local Windows main `1a05135` on branch
`phase3-universal-distribution`. Version 0.2.1 consolidates the entire previous
104-file toolkit inventory into `Bioinformatics-Agent-Skills-Complete.zip`,
with the shared mode policy, scientific source record and explicit Python package
initializer added. The 17 skills and their instructions, scientific method
implementations, R recipes, evaluation criteria and historical verdicts are unchanged.

The universal archive has **107 files, 285,194 bytes**, SHA-256
`27220befd97d20d3d15f0c7d25ece424a722dd355d199dca2c8cf1dfc217a423`.
It passed exact source/extracted inventory and normal installation/first-use
checks before removal of the redundant Toolkit ZIP. The single checksum is
tracked in SHA256SUMS. Packaging and CI reject extra root ZIPs, unsafe portable
paths, symlinks, unreviewed file types and recognized credential patterns.
Text newlines are normalized while binary resources retain exact bytes.
Credential pattern checks are bounded safeguards, not a universal secret detector.

Validation used Python 3.12.10, pytest 8.3.5, Ruff 0.11.13 and setuptools 80.9.0
in the existing virtual environment. Set `PYTHONUTF8=1`, `PYTHONPATH=src`, and
task-local `XDG_CACHE_HOME`/`MPLCONFIGDIR` before the repository checks.

| Command | Observed result |
|---|---|
| `python -m pytest -q tests/test_package_skills.py --junitxml artifacts/phase3-universal/packaging.xml` | 56 passed, 1 skipped, zero failures |
| `python -m pytest -q --junitxml artifacts/phase3-universal/pytest.xml` | 207 passed, 14 skipped, zero failures; 221 collected |
| `ruff check .` / `ruff format --check .` | PASS; 30 Python files formatted |
| `python scripts/validate_skills.py` | 17 skills, zero structural/link errors |
| `python scripts/build_catalog.py --check` | PASS |
| `python scripts/sync_modes.py --check` | PASS |
| `python scripts/package_skills.py` / `python scripts/package_skills.py --check` | PASS; deterministic archive and single checksum |

Thirteen local scientific skips retain the existing Windows Application Control
block on libsbml. The symlink rejection fixture is skipped because this account
cannot create symlinks; the implementation still rejects them. The new offline
extraction test installs the packaged source normally into a temporary venv and
reuses third-party dependency files only, without loading the development venv's
editable-install hooks. Isolated `-I` subprocesses verify that every toolkit module
loads from the installed package, discover all seven CLI commands, execute the
first-use, bulk-readiness, multi-omics and metadata dry-run examples, check hashes
and schemas, and reject a TPM scientific-invalid fixture with exit 2.

An initial offline test setup failed because a fresh venv does not inherit a
parent venv's build dependencies. Explicit offline third-party dependency reuse
corrected that setup; final tests pass. Hosted CI additionally gates publication
on fresh dependency installation from the extracted ZIP in clean Windows/Linux
venvs, Linux scientific regression checks and the unchanged pinned R job.
No model sessions or live public data requests were launched. Prior scientific
limitations and independent human review requirements remain in force.

The additional local standalone run created a fresh venv with no shared site
packages, installed `requirements-toolkit.txt` and the extracted package, then
ran `python -m pip check`, isolated CLI/module-origin checks, first-use,
cross-view, metadata dry-run and schema checks. All eight checks passed.
Metabolic execution remained BLOCKED at the native COBRApy import; R execution
from the extraction was NOT_RUN. The record is
`artifacts/standalone-Windows.json`; logs are in
`artifacts/phase3-universal/standalone-local.log`, both excluded from Git.

At source `a868e3b`, [Linux validation and standalone execution](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44558732180)
passed 217 tests with four Windows-only skips. The fresh Linux extraction also
executed both original and domain metabolic recipes successfully.
The [unchanged pinned R job](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44558732357)
passed all 18 checks (six model fits, twelve invalid-input rejections).
The first hosted Windows standalone installation succeeded but its origin
assertion compared a resolved long path with an unresolved `RUNNER~1` short
path. Both expected and actual paths are now resolved; this preserves the
installed-origin requirement. The packaging suite was rerun: 56 passed, one
symlink-creation skip, zero failures. A native Windows short/long-path check
also passed. Final-head CI must pass before merging
[PR 3](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/pull/3).

## Phase 3 domain execution checkpoint — 2026-11-19

Development proceeds on `phase3-executable-science` from synchronized main
`7aa0c1a`. See [Phase 3 capability and execution status](phase3-status.md).
The initial checkpoint adds pinned R/Bioconductor recipes, richer synthetic
SBML/GPR controls and an executed cross-view baseline. R execution and Linux
metabolic execution initially awaited CI. R execution has since passed eighteen
checks, with the verified status/result hashes in
[R execution provenance](../references/phase3-r-execution.json). The latest local
suite has 173 passed, 13 skipped and zero failures. The skips are blocked
COBRA imports. Both extracted archives and the toolkit first-use recipe passed.
Linux CI passed 182 tests with four Windows-only skips and ran the metabolic
recipes and all seven validator fixture groups. Milestone 3.5 remains explicitly
unfinished. The repository now ships 17 experimental skills, with all historical
Phase 2 judgments preserved.
See the Phase 3 status for final Linux execution and publication evidence.
Historical Phase 2 evidence is preserved.

## Complete skills ZIP package — 2026-11-19

Built `Bioinformatics-Agent-Skills-Complete.zip` on clean local `main` after
fast-forwarding it to `origin/main` at
`5f5df871eb390c96b5f0bdcb41daeff3f4fc1e23`. The archive contains 13 canonical
`SKILL.md` files, the RNA-seq, multi-omics and metabolic-modeling
`references/methods.md` files, `INSTALL.md`, and the MIT `LICENSE`.
Its 18 files total **63,534 archive bytes**. SHA-256 is
`434329c62a46f7b94aeb4e496cc8a898f114a71eeb3cb42184f03624f53a93eb`.
The scientific instruction sources, benchmark scores and evaluation evidence
have no changes.

`python scripts/package_skills.py` discovers and validates the skill folders,
packages their Markdown reference files, normalizes text newlines, and fixes ZIP
ordering, timestamps and file modes. ZIP stored entries avoid compression-library
differences. Unsupported files under a skill fail the build for review. The build
checks bundled Markdown references, validates exact member contents and metadata,
and extracts into a temporary directory to check all files and skill metadata.
`python scripts/package_skills.py --check` detects stale archive bytes without
rewriting the ZIP. GitHub Actions runs this check and verifies Git tracks the
root archive. README provides its direct GitHub download link, and
[INSTALL.md](../INSTALL.md) explains host-dependent installation and invocation.

Validation used the existing Python 3.12.10 virtual environment and Ruff
0.11.13 on Windows, with UTF-8 mode, `PYTHONPATH=src`, and repository-local
cache paths. The relevant commands and results follow.

| Command | Observed result |
|---|---|
| `python -m pytest -q tests/test_package_skills.py --junitxml artifacts/skills-package/packaging.xml` | 21 passed |
| `python -m pytest -q --junitxml artifacts/skills-package/pytest.xml` | **124 passed, 8 skipped, 0 failures**, 132 collected |
| `ruff check .` and `ruff format --check .` | Both exit 0; 16 Python files formatted |
| `python scripts/validate_skills.py` | 13 skills, 0 structural or link errors |
| `python scripts/build_catalog.py --check` | Exit 0 |
| `python scripts/package_skills.py --check` | Exit 0; exact archive and extracted inventory verified |

The eight skipped existing tests require COBRApy, whose `libsbml` DLL import was
blocked by Windows Application Control. Those scientific checks remain unverified
in this run. The packaging tests all executed. The full-suite JUnit XML SHA-256 is
`2949b843d648f838d4710bdd789b6489f3c1dcd90fe207636710ea09d018501c`.
The local commit requires a later push to make the README's GitHub download
available. No push or GitHub Release was performed for this task.

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
