# Phase 2 milestone 1 — Local agent evaluation

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
the resolved model version. A successful shell event that names a staged
`SKILL.md` and returns its full contents is recorded as an observed read. There
is no activation verdict for implicit, partial or unobserved reads.

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

On a host that passes the isolation probe, the remaining tasks are to collect a
single live smoke response, verify the discovery and activation evidence available
from that CLI version, then run selected pairs and eventually the full benchmark
with human adjudication. No further Phase 2 milestone was started.
