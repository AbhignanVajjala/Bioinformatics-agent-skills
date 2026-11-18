# Phase 2 pilot evidence provenance

**Provisional automated review. Independent human methodological review is pending.**
This record adds evidence locators to the [original scores](agent-benchmark-scores.json)
and [pilot review](agent-benchmark-summary.md). The recorded benchmark verdicts
remain 0 PASS, 4 FAIL and 6 BLOCKED.

The source run is `agent-eval-7e2fa2331d71450a8dd5020640971e6d`. Its saved
`report.json` has SHA-256
`07af7e9c06cb30a9dcae81e6fcbdccd7f7858d6edfc5da900fae4bd60f2eca32`.
The original reviews were committed in `385522247b45e00c478ef35fa71c6676943dcdc7`.

## Locating each judgment

For each row below, find the scored turn at the zero-based JSON pointer shown.
Its `artifact_sha256` values identify `prompt.txt`, `response.txt` and
`events.jsonl` under the recorded attempt directory in the saved run. The
turn's `dimensions/<dimension>/criteria/<index>` entries give each criterion,
verdict, reason and verbatim response excerpts. The `activation` entry records
the distinct trigger criterion when applicable. The `benchmark_reason`
explains the overall provisional verdict. The expected-behavior source is the
case's `expected_behavior`, `failure_behavior` and applicable
`expected_activation` in the [trigger manifest](../cases/triggers.json) or
[scientific manifest](../cases/scientific.json), interpreted under the
[scientific review rubric](../rubrics/scientific-review.md). The explicit
invocation case uses the existing [pilot criteria](../../docs/development-progress.md#pilot-review)
and the positive trigger prompt prefixed with `$research-specification`.

| Attempt | Score pointer | Original expectation | Provision and access to target skill |
|---|---|---|---|
| 001 | `/turns/0` | Explicit `research-specification` request with paired estimand and design gates | Baseline. Target unavailable in staged library. |
| 002 | `/turns/1` | Same explicit request | Target staged. Read observed. |
| 003 | `/turns/2` | `research-specification-positive-1`. Automatic selection of `research-specification` and application of its gates | Baseline. Target unavailable in staged library. |
| 004 | `/turns/3` | Same automatic-selection expectation | Target staged. Read observed, plus a second skill read. |
| 005 | `/turns/4` | `scientific-prompt-engineering-negative-2`. Handle the FASTQ rename without applying `scientific-prompt-engineering` | Baseline. Target unavailable in staged library. |
| 006 | `/turns/5` | Same negative-control expectation | Target staged. No read observed. |
| 007 | `/turns/6` | `enrichment-background`. Eligible universe, audited organism-specific mapping and multiplicity control | No target skill specified. Baseline had no staged library. |
| 008 | `/turns/7` | Same enrichment safeguards | No target skill specified. One file read observed. |
| 009 | `/turns/8` | `survival-censoring`. Preserve censoring, specify estimand and assumptions, propose suitable methods and diagnostics | No target skill specified. Baseline had no staged library. |
| 010 | `/turns/9` | Same survival safeguards | No target skill specified. Library staged. No read observed. |

## Exact file-read evidence

| Attempt | JSONL line, item and read order | Staged file | Match to benchmark target |
|---|---|---|---|
| 002 | 5, `item_1`, 1 | `.agents/skills/research-specification/SKILL.md` | Matches explicit target |
| 004 | 5, `item_1`, 1 | `.agents/skills/research-specification/SKILL.md` | Matches automatic-selection target |
| 004 | 5, `item_1`, 2 | `.agents/skills/bulk-rnaseq-differential-expression/SKILL.md` | Additional read, different from target |
| 008 | 5, `item_1`, 1 | `.agents/skills/verification-before-scientific-claims/SKILL.md` | Scientific case has no target skill |

These completed command events each exited zero. They name the staged files,
and the **full** recorded output matches the corresponding source bytes rendered
as Windows-1252, including the ordered pair of files in attempt 004. The previous
detector searched for an absolute path and an exact UTF-8 match to one file.
The pilot commands used relative paths, the combined read returned two bodies,
and PowerShell rendered non-ASCII characters differently. The JSONL command
events record file access. They do not expose semantic skill activation or
instruction-following. [Codex non-interactive event documentation](https://learn.chatgpt.com/docs/non-interactive-mode).

## Offline replay and interpretation

From the checkout on Windows, use the existing Python virtual environment:

```powershell
$report = Join-Path $env:LOCALAPPDATA 'BioinformaticsAgentSkills/milestone2/agent-eval-7e2fa2331d71450a8dd5020640971e6d/report.json'
python scripts/run_agent_evals.py --inspect-report $report
```

Replay reads the saved files, verifies the prompt, response and JSONL hashes
recorded for each attempt, and checks the current manifests, rubric and skill
bytes against the saved input hashes. It also checks the final response and
thread ID of completed turns against the stream. Output goes to stdout.
The recorded source hash above identifies the original report when comparing
independently obtained copies.

- `UNAVAILABLE` means the canonical file was absent from the staged library.
  Availability describes staging, with no assertion about bundled or administrator skills.
- `AVAILABLE_NO_OBSERVED_READ` means the staged file had no confirmed read in
  the supported event shapes. Unsupported or partial command evidence may appear
  under `ambiguous_item_ids`.
- `SKILL_FILE_READ_OBSERVED` means a successful literal PowerShell
  `Get-Content` event names the file and matches the full rendered output.
- `AVAILABLE_TRACE_UNVERIFIED` means the file was staged and the trace could
  not verify a complete turn. Reads from malformed traces are discarded.
- `instruction_following_status: NOT_ASSESSED` means the extractor has made no
  behavioral judgment. Assess actual adherence from the response and applicable
  criterion in the original scores. Missing telemetry leaves activation
  `UNOBSERVABLE`.

The replay supports literal, unredirected PowerShell reads of staged paths and
UTF-8 or Windows-1252 rendering. It may miss reads through other tools, aliases,
dynamic commands, truncated output, or implicit skill-loading mechanisms.
The pilot contains one turn per mode per case. Access observations leave the
original scientific verdicts and the limits on paired comparisons unchanged.
