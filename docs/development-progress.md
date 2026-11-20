# Development progress

## Phase 4 research credibility and authorship transparency

Version 0.2.2 introduces a scientific project overview, explicit implementation
and evidence boundaries, project-level maintainer/citation credit, substantial
AI-assistance disclosure, a documented-versus-tested host matrix, contributor
expectations and a three-workflow technical guide. Human-review completion
fields remain NOT_REVIEWED. The collection remains experimental.

The same universal ZIP retains all 17 skills and the scientific toolkit, with
essential scientific/attribution guides added. Original skill instructions,
scientific implementations, test assertions and historical evaluation records
are unchanged. The local suite collected the same 221 cases: 219 passed and two
skipped. These software results do not establish biological validity or agent
effectiveness. Read [implementation status](implementation-status.md),
[scientific evidence](scientific-evidence.md) and the
[presentation audit](phase4-presentation-audit.md). Historical entries below
retain their original dates, outcomes and meaning.

## Phase 3.11 universal distribution

The current distribution is one `Bioinformatics-Agent-Skills-Complete.zip`
containing all 17 skills and the complete executable toolkit. The separate
Toolkit ZIP is superseded. Instruction-only users copy `.agents/skills/`;
scientific users install dependencies and run from the same complete extraction.
No scientific instructions, analysis methods or historical pilot judgments are
changed. See [implementation status](implementation-status.md) for verification.

## Phase 3 executable-science development

The current checkpoint implements the three existing domain recipes, a reusable
validator CLI, shared Quick/Full mode contracts, four additional scoped domain
skills and reproducible distribution, now consolidated into one universal ZIP. The complete status,
executed R evidence and unfinished Milestone 3.5 domains are recorded in
[Phase 3 status](phase3-status.md).

Begin with [START_HERE.md](../START_HERE.md) and
[SKILL_INDEX.md](../SKILL_INDEX.md). The original Phase 2 pilot and its
provisional scores retain their historical meaning.

## Phase 2 milestone 3 — Evidence integrity and skill observability

The runner now distinguishes staged availability, confirmed skill-file reads,
and unverified traces. It records each confirmed read's path, JSONL line, item
ID, output encoding and position in a multi-file command. Activation and
instruction-following require separate evidence or review.

`python scripts/run_agent_evals.py --inspect-report PATH_TO_REPORT_JSON`
replays a saved report offline, verifies artifact and source-input hashes, and
prints a new observation record. The original report stays intact. The
[pilot evidence provenance](../evals/reports/agent-benchmark-provenance.md)
maps all ten turns to the existing scores and original benchmark behavior.
It records the four confirmed reads and why the earlier detector missed them.

The extractor currently covers direct PowerShell `Get-Content` calls and
complete, matching output. Implicit loads and other read commands can be
invisible. A separate behavioral assessment is required to judge whether an
answer followed a skill. The original pilot scores remain provisional pending
independent human methodological review.

## Phase 2 milestone 2 — Controlled pilot `BLOCKED`

The native Windows isolation probe passed from a normal host process on Windows
25H2 build 26200.9974 with `codex-cli 0.169.0-alpha.11.1`. The same runner inside
the managed Codex shell received `native MXC is unavailable on this executor`.
The host surfaced two runner defects separately. Its Codex process needed
`SystemDrive`, and its sandboxed command needed `SYSTEMROOT`. The runner now
passes these values explicitly. The inner MXC policy still limits filesystem reads,
blocks writes and disables tool network access. Shell environment inheritance
remains off.

The host smoke command passed isolation and stopped at the ChatGPT login check.
The fresh evaluation home had no verified login. This run has no model output,
activation signal, token usage or pilot adjudication. See
[implementation status](implementation-status.md#phase-2-milestone-2--2026-11-18)
for the individual probe outcomes and evidence.

### Continue from normal local PowerShell

Open PowerShell from Windows and run these commands in the same terminal. The
dedicated home is on the local profile, away from the checkout and evaluation
reports. The login command opens the ChatGPT sign-in flow in the browser.
[Codex CLI authentication](https://learn.chatgpt.com/docs/auth?surface=cli).

```powershell
Set-Location -LiteralPath 'C:\Users\kukka\OneDrive\Documents\GitHub\Bioinformatics-agent-skills'
$python = (Resolve-Path -LiteralPath '.venv/Scripts/python.exe').Path
$cli = (Get-Command codex.exe -CommandType Application -ErrorAction Stop).Source
$authHome = Join-Path $env:LOCALAPPDATA 'BioinformaticsAgentSkills\codex-auth'
$evidence = Join-Path $env:LOCALAPPDATA 'BioinformaticsAgentSkills\milestone2'

& $python scripts/run_agent_evals.py --probe --codex $cli --output-dir $evidence
if ($LASTEXITCODE -ne 0) { throw 'MXC isolation probe failed. See the reported directory.' }

New-Item -ItemType Directory -Path $authHome -Force | Out-Null
$previousCodexHome = [Environment]::GetEnvironmentVariable('CODEX_HOME', 'Process')
try {
    $env:CODEX_HOME = $authHome
    & $cli login -c 'forced_login_method="chatgpt"'
    if ($LASTEXITCODE -ne 0) { throw 'ChatGPT sign-in failed.' }
} finally {
    [Environment]::SetEnvironmentVariable('CODEX_HOME', $previousCodexHome, 'Process')
}
```

Enter a model ID available to your ChatGPT account. The next block runs one
baseline turn and checks its exact response before starting the five-case pilot.
The same model and tool settings are used for both modes in every pair.

```powershell
$model = Read-Host 'Codex model ID'
$smoke = & $python scripts/run_agent_evals.py --execute --smoke --codex $cli `
    --model $model --codex-home $authHome --output-dir $evidence
$smokeExit = $LASTEXITCODE
$smoke
if ($smokeExit -ne 0) { throw 'Smoke run stopped. See the reported directory.' }
$smokeReport = Get-Content -Raw -LiteralPath $smoke[0] | ConvertFrom-Json
$smokeDir = Join-Path (Split-Path -Parent $smoke[0]) $smokeReport.results[0].artifact_dir
$answer = Get-Content -Raw -LiteralPath (Join-Path $smokeDir 'response.txt')
if ($smokeReport.results[0].status -ne 'COMPLETED' -or $answer.Trim() -cne 'READY') {
    throw 'Smoke evidence did not match the expected READY response.'
}

& $python scripts/run_agent_evals.py --execute --pilot --codex $cli `
    --model $model --codex-home $authHome --output-dir $evidence
```

### Pilot review

`--pilot` selects five scenarios for ten total turns. It also works without
`--execute` to produce an offline plan. The default 114-turn plan stays intact.

| Scenario | What to check in the evidence |
|---|---|
| Explicit `$research-specification` invocation | Inspect available runtime evidence for how the requested skill was handled. The response should specify the estimand, donor pairing and design gates. |
| Automatic research-specification selection | Use the same paired RNA-seq task without the skill name. Review skill evidence and the adequacy of the response separately. |
| Negative control for scientific-prompt-engineering | A FASTQ rename request should be handled as file housekeeping and preserve file contents. Review any evidence of unnecessary prompt-engineering skill use. |
| Enrichment background | Check that eligible tested genes define the universe, assignments account for species and ambiguous identifiers, and the response addresses multiplicity. |
| Survival censoring | Check that censoring is retained and the response proposes a suitable estimand and censoring-aware analysis. |

Record the reviewer, quoted response evidence, evaluation status and unresolved
uncertainty separately from execution status. The explicit request is a user
prompt condition. A request mention or observed skill-file read alone leaves
activation or scientific adequacy unresolved. Preserve raw JSONL, final messages
and reported token usage under the evidence directory.
[Skill discovery and explicit invocation](https://learn.chatgpt.com/docs/build-skills),
[scientific evaluation rubric](../evals/rubrics/scientific-review.md).

### WSL2 route

Ubuntu WSL2 is installed. The host inventory found Python 3.14.4 and
`/usr/bin/bwrap`. The `codex` on its PATH resolved to the Windows app's mounted
resources directory. Linux CLI identity and sandbox behavior were unverified.
OpenAI supports native Linux Codex in WSL2 with bubblewrap. A Linux adaptation
of this harness needs its own isolation probe before it can run the pilot.
The current harness preflight requires native Windows MXC. Legacy Windows
`elevated` mode requires separate provisioning and was outside this milestone.
[WSL2 setup](https://learn.chatgpt.com/docs/windows/wsl),
[native Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox?translationFallback=pt-BR).

## Phase 2 milestone 1 — Local agent evaluation

Baseline `7ba97ae` on the local Windows feature branch `phase2-agent-evaluations`.
The milestone adds [the agent runner](../scripts/run_agent_evals.py) and
[offline tests](../tests/test_agent_evals.py). The existing deterministic runner,
manifests, rubric and 13 canonical skills continue to supply the evaluation inputs.

## Run the harness

From the repository root with a Python 3.11+ virtual environment active in PowerShell:

```powershell
python scripts/run_agent_evals.py
python scripts/run_agent_evals.py --case scientific-prompt-engineering-positive-1
python scripts/run_agent_evals.py --probe
```

Planning is offline and covers 52 trigger and five scientific agent scenarios in
both modes, for 114 planned turns. Each report has a unique directory under
`[System.IO.Path]::GetTempPath()` in `bioskills-evals` by default. Use
`--output-dir artifacts/agent-evals` to retain reports across managed shell sessions.

Live execution requires an explicit selection (`--case`, `--smoke`, or `--all`),
an explicit `--model`, and a dedicated `--codex-home` with a ChatGPT login. Use
a separate shell for signing in to that home and restore the normal environment
before running the harness. The adapter invokes the installed CLI locally, and
ChatGPT supplies model inference. `--execute --smoke` selects one synthetic
baseline turn by default. Running a selected benchmark case uses both modes unless
`--mode baseline` or `--mode skills` is given.

The runner uses `codex exec --json --ephemeral` with a new process, temporary
working directory and user profile per turn. Both modes receive the same prompt
bytes over stdin. The skills mode stages the 13 canonical skills and their three
method references under `.agents/skills`. The baseline workspace starts empty.
The case ID, target skill label, expected behavior, manifest and rubric stay
with the runner. The runtime's bundled or administrator-provided instructions
may still influence both modes. Live skill discovery remains unverified.
[Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

The Windows probe checks that a native MXC command can read inside its workspace,
cannot read a sibling canary, and cannot write into the workspace. The profile
also disables shell networking and approval requests. The CLI runs with an
environment allowlist, user config and rules ignored, and hooks, plug-ins, apps,
memories and web search disabled. API-key variables are excluded. Authentication
is checked separately and its raw output stays out of evidence. Preflight failure
blocks the batch. A failed or timed-out turn stops the batch without retry.
[Codex permission profiles](https://learn.chatgpt.com/docs/permissions),
[Windows MXC sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).

## Read the evidence

`report.json` records the CLI version and preflight when probed, requested model,
input and skill SHA-256 hashes, and per-turn timestamps, exit status and thread ID
where available. Each attempted turn also stores the exact prompt, JSONL stream,
stderr and final response with hashes. The CLI stream used here does not identify
the resolved model version. The
[skill evidence contract](../evals/reports/agent-benchmark-provenance.md#offline-replay-and-interpretation)
describes which observed reads the current runner can verify.

`COMPLETED` requires exit zero, a fresh thread, exactly one completed turn,
and a nonempty final response consistent with the event stream. `FAILED` means
an attempted turn did not meet that contract. `BLOCKED` means a prerequisite or
earlier failure prevented execution, and `NOT_RUN` is the offline plan status.
Benchmark adjudication is `NOT_RUN` separately even for a completed turn. Reviewers
use the [existing rubric](../evals/rubrics/scientific-review.md) outside the candidate
session. No automated grading or improvement claim is produced by the harness.

## Validation and remaining work

The local CLI version probe succeeded with `0.169.0-alpha.11.1`. The filesystem
probe exited 1 with `failed to prepare MXC sandbox: native MXC is unavailable on
this executor`. This was a local sandbox command. No model turn, login attempt
or benchmark adjudication took place. See the [implementation status](implementation-status.md)
for commands and offline validation evidence.

Milestone 2 records the follow-up host probe and the controlled pilot plan above.
