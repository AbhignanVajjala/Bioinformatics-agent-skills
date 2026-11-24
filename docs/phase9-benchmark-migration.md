# Phase 9 benchmark migration and operation

This protocol supplements historical evidence without changing old prompts,
labels, rubrics or scores. All new live evaluations are NOT_RUN and require
separate maintainer approval. Use Python 3.11+ in a virtual environment. The
runner uses the standard library; scientific examples need toolkit dependencies.

## Versions and dimensions

Legacy triggers.json (52 cases), scientific.json (five agent cases), Phase 3
manifests and scientific-review.md remain unchanged. Default planning still
yields 114 paired turns. Some old negative labels mix out-of-scope requests with
invalid in-scope requests; do not retrospectively regrade them using new labels.

evals/benchmarks/phase9-v1.json has 68 development cases: legitimate, out-of-scope,
adversarial and invalid-in-scope requests for every skill. Invalid in-scope
requests should engage safeguards. Ten compound held-out preparations have
distinct source groups. They are candidate-isolated but author-visible, not
independently sealed or empirically proven harder. Do not tune on their future
outputs; independent curators should supply a separately sealed replication set.

| Dimension | Evidence and limit |
|---|---|
| Availability | Repository skills staged or unavailable; does not describe every host system instruction |
| Observable reads | Command output verified against exact staged skill bytes; absence is not proven nonactivation |
| Trigger appropriateness | Reviewer judgment of task relevance/disposition, separate from access |
| Instruction adherence | Provisional workflow judgment; cannot prove that loading caused behavior |
| Scientific correctness | Criterion decisions with quoted evidence and limitations |
| Grounding | Actual excerpts/locators or explicit whole-response absence review |
| Critical failures | Required separate adjudications; critical failure overrides positive scores |
| Efficiency | Words, characters, elapsed time and available token/cache counts; no automatic scientific score or price |
| Execution | COMPLETED, INCOMPLETE, FAILED, BLOCKED or NOT_RUN; never scientific success alone |

Requested and resolved model/effort are separate. Identical requested settings,
tools and prompts do not establish identical backend behavior. Unobserved resolved
configuration stays unverified. A seed controls order, not model sampling.

## Offline planning

From the repository root using the chosen virtual environment:

```powershell
python scripts/run_agent_evals.py --benchmark evals/benchmarks/phase9-v1.json --trials 3 --seed 17 --output-dir "$env:LOCALAPPDATA/BioinformaticsAgentSkills/phase9-plans"
python scripts/run_agent_evals.py --benchmark evals/benchmarks/phase9-v1.json --split heldout --trials 3 --seed 17 --output-dir "$env:LOCALAPPDATA/BioinformaticsAgentSkills/phase9-plans"
```

These plan 408 development and 60 held-out turns, all NOT_RUN, without invoking
Codex. --case selects bounded cases; --all explicitly selects a split. Prefer
outputs outside OneDrive. Repeats retain identical paired prompt hashes and
record trial/order/seed. Alternating order counterbalances even repeat counts.

After separate approval, live operation requires --execute, explicit selection,
--model, --reasoning-effort, --timeout and a dedicated --codex-home. First validate
one approved harmless turn. Stop on isolation/initialization failure; do not
repeatedly invoke nested sessions or use unrestricted execution as a workaround.
No live turn was run for Phase 9 implementation.

## Progress and interruption

Execution emits JSON progress to stderr at turn boundaries and every ten seconds,
configurable with --progress-interval. It shows completed/remaining, failed and
incomplete turns, current case/condition/trial and elapsed time. Keep progress
away from blinded reviewers. The final report location remains on stdout.

Ctrl+C or timeout requests termination of the owned CLI process with bounded
terminate/kill waits. The current turn is INCOMPLETE and partial streams remain;
later turns remain unrun. Power loss can leave RUNNING in the last checkpoint.
Automatic resume rejects that uncheckpointed state: preserve it, establish that
the old runtime stopped, and start a new experiment rather than risk duplicate work.
Offline tests exercise this behavior; new live-runtime cancellation is NOT_TESTED.
Already consumed requests cannot be promised cost-free or reversible.

For an interrupted compatible live report, retain its exact source, skills,
runtime and dedicated authentication home, then explicitly resume:

```powershell
python scripts/run_agent_evals.py --resume "C:/path/to/interrupted/report.json" --execute --codex-home "C:/path/to/dedicated-codex-home"
```

Resume adopts the frozen selection/model/effort/trials/timeout and checks source,
skills, prompts, runtime executable and existing artifact hashes before another
turn. Incompatible overrides reject without replacing the report. Completed turns
stay; old partial attempts retain distinct IDs and the pre-resume report is saved
with its checksum. Attempt summaries include historical incomplete attempts;
resource accounting marks missing counters as unknown rather than zero. New attempts use fresh workspace,
home and thread IDs. This is batch continuation, never Codex session resume.
Legacy schema-1 evidence cannot resume. FAILED turns do not auto-retry: diagnose
and start a new experiment. Source/runtime changes also require a new experiment.

## Blinded adjudication

Only completed turns with matching prompt/artifact/JSONL evidence can export.
Use the exact skill/benchmark snapshot, new output paths and a private allocation
file outside the reviewer directory:

```powershell
python scripts/grade_agent_evals.py blind --report "C:/path/report.json" --benchmark evals/benchmarks/phase9-v1.json --reviewer-dir "C:/path/reviewer" --private-map "C:/private/allocation.json"
python scripts/grade_agent_evals.py grade --packet "C:/path/reviewer/responses.json" --judgments "C:/path/reviewer/judgments.json" --output "C:/path/frozen-grades.json"
python scripts/grade_agent_evals.py unblind --grades "C:/path/frozen-grades.json" --private-map "C:/private/allocation.json" --output "C:/path/paired-review.json"
```

Packets contain opaque IDs, prompts, unchanged responses and criteria, without
condition/read/usage/runtime metadata. Content can still reveal skill use; this
is metadata blinding, not guaranteed blinding or cryptographic sealing. Keep
allocation private until scientific grading is complete. Record reviewer
visibility, independence, qualifications, actual date and disagreements.

judgments.json supplies each blind_id, reviewer, overall reason, criteria and
critical_failures. Each criterion needs id/status/reason/evidence. PASS/FAIL
require exact response character offsets and quotation. MISSING requires a reason
and review_scope=entire_response, without inventing an absence quotation.
UNRESOLVED stays BLOCKED. Every critical rule needs NOT_OBSERVED, OBSERVED or
UNRESOLVED and a reason; observed failures require quotations. The tool validates
records, not scientific truth. An example evidence entry is
{"start":0,"end":6,"quote":"Source"} only if the response really starts Source.

Complete grading precedes unblinding; packet hashes prevent allocation mixing.
Reports remain provisional pending independent human review. Failed/incomplete
executions remain separate from graded completed answers. Do not add overlapping
test counts or infer effectiveness from one sample, pooled scores or file reads.

## Runtime platform boundary

Windows retains explicit MXC, strict configuration, read-only workspace, disabled
network, never-approve and the existing isolation probe. No ordinary
windows.require_mxc override or weaker fallback is introduced. Local CLI
0.171.0-alpha.13.2 version/help was inspected; its live compatibility is not
inferred from the original successful 0.168.0 benchmark.

Official [permissions](https://learn.chatgpt.com/docs/permissions) and
[Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox) guidance
was consulted November 24, 2026. Linux/WSL use bubblewrap/seccomp. Equivalent
Linux/Codespaces isolation has not been demonstrated here, so live Linux remains
BLOCKED. A container alone does not prove equivalence.

Before enabling Linux, test inside reads; denied outside/home/rubric/auth/socket
reads; denied writes and loopback/external network; absent parent guidance; fresh
sessions; and fail-closed initialization under the actual supported CLI. Do not
change security policies or weaken isolation to make those checks pass.

## Proposed post-correction evaluation

After maintainer approval, validate one harmless turn, then a proposed four-case,
three-repeat paired pilot (24 turns, with an explicit timeout/resource ceiling)
covering evidence gaps, extraction silence/conflict, checked arithmetic and changed-
input reproduction. Predeclare repeats, model/effort, resource ceiling, stopping
rules, rubric and blinded independent adjudication. Only after measurement
validation should prepared held-out or 68-case development comparisons execute.
Keep their results separate, disclose exposure/backend uncertainty/incomplete turns,
and retain critical failures. Independently sealed harder cases and qualified
human review remain required for stronger effectiveness claims.
