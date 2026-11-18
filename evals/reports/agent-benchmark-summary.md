# Phase 2 controlled pilot review

**Provisional automated assessment. Independent human methodological review is pending.**

| Outcome | Count |
|---|---:|
| Execution completed | 10 |
| Provisional benchmark PASS | 0 |
| Provisional benchmark FAIL | 4 |
| Provisional benchmark BLOCKED | 6 |
| Activation unverified | 10 |

The two enrichment responses fail the multiplicity requirement. The two survival
responses fail the estimand, censoring assumption and diagnostics requirements.
All six trigger judgments are blocked because invocation or non-invocation
could not be verified. Scientific content and workflow are scored separately
for those turns.

## Evidence and scoring

This review covers the saved run `agent-eval-7e2fa2331d71450a8dd5020640971e6d`
from November 18, 2026. The run recorded Codex CLI `0.168.0`, provider ChatGPT,
and requested model `gpt-6.1-sol`. The resolved backend model version is unknown.
The review checked the recorded artifact hashes, distinct thread IDs, one completed
turn per thread, zero exit statuses, final response agreement with the JSONL,
and token usage agreement with the completion events. The version, isolation
and login preflight steps recorded exit zero.

The five pairs used byte-identical prompts within each pair and the same
recorded CLI settings after normalizing per-attempt paths. All prompts matched
the original manifests or the existing explicit pilot prompt derived from the
positive trigger. The input, rubric, runner and staged skill hashes matched
the checkout. The [machine-readable score report](agent-benchmark-scores.json)
records the input and artifact hashes, per-turn token counts, and the exact
excerpts and reasons for each criterion. Raw transcripts and local runtime
details remain in the original evidence directory.

Benchmark outcomes follow the [scientific review rubric](../rubrics/scientific-review.md),
the [trigger manifest](../cases/triggers.json), the
[scientific manifest](../cases/scientific.json), and the existing
[pilot criteria](../../docs/development-progress.md#pilot-review).
The paired RNA-seq review also uses the
[research specification skill](../../.agents/skills/research-specification/SKILL.md)
for the automatic-selection case's scientific gates and handoff expectations.
The workflow dimension also records gaps that do not independently determine
the benchmark verdict. There is no composite score.

| Attempt and scenario | Mode | Scientific correctness | Method completeness | Critical errors¹ | Unsupported conclusions¹ | Workflow quality | Benchmark |
|---|---|---|---|---|---|---|---|
| 001 · Explicit research specification | Baseline | PASS | PASS | PASS | PASS | PASS | BLOCKED |
| 002 · Explicit research specification | Skills | PASS | PASS | PASS | PASS | PASS | BLOCKED |
| 003 · Automatic research specification | Baseline | PASS | FAIL | PASS | PASS | FAIL | BLOCKED |
| 004 · Automatic research specification | Skills | PASS | PASS | PASS | PASS | FAIL | BLOCKED |
| 005 · FASTQ negative control | Baseline | PASS | PASS | PASS | PASS | PASS | BLOCKED |
| 006 · FASTQ negative control | Skills | PASS | PASS | PASS | PASS | PASS | BLOCKED |
| 007 · Enrichment background | Baseline | PASS | FAIL | PASS | PASS | PASS | FAIL |
| 008 · Enrichment background | Skills | PASS | FAIL | PASS | PASS | PASS | FAIL |
| 009 · Survival censoring | Baseline | PASS | FAIL | PASS | PASS | FAIL | FAIL |
| 010 · Survival censoring | Skills | PASS | FAIL | PASS | PASS | PASS | FAIL |

¹ PASS indicates that the review found no critical error or unsupported
conclusion in the observed response. The omissions below are substantive
rubric failures. The responses did not report invalid fits or biological claims
from those incomplete methods.

## Paired comparisons

**Explicit research specification, attempts 001–002.** Both defined a paired
gene-level contrast and set identity, replication, confounding, QC and FDR gates.
Baseline described the contrast as “conditional on donor” and said the
requested skill “was not found in the available skills or accessible workspace.”
Skills described a “Within-subject treatment-associated expression difference”
and drafted a research specification, analysis plan and acceptance checks in
the response. The files were proposed in text. Checks and fitting were marked
`NOT_RUN`.

**Automatic research specification, attempts 003–004.** Both used pair
blocking, checked design rank, and prespecified FDR. Baseline called the target
a “population-average within-pair treatment effect” and later clarified that
“The treatment coefficient is a common effect conditional on pair.” It omitted
an explicit raw-count or supported-import gate and prospective precision
planning. Skills required “raw gene counts with known provenance, or a supported
transcript-to-gene import,” added residual degrees of freedom, and called for
effect and dispersion assumptions to assess pair count adequacy. Both supplied
usable plans in prose and omitted the canonical three-part handoff and reviewer
identity.

**FASTQ negative control, attempts 005–006.** Both treated the request as file
housekeeping, respected read-only access and made no change. Baseline
provided a `Rename-Item -LiteralPath` example and preserved the compressed
extension. Skills asked for “the file’s path and desired new name.” The control
checks non-invocation of the prompt-engineering skill. The absence of a reported
read cannot establish that criterion.

**Enrichment background, attempts 007–008.** Both rejected the selected
list as the universe and flagged many-to-many symbol mapping without species or
annotation provenance. Baseline said “resolve ambiguous mappings consistently”
but omitted a record of mapping decisions. Skills said “document ambiguity
resolution and deduplication” and conditioned the eligible universe on annotation
coverage. Both stopped short of a pathway result. Neither specified how to
control multiplicity across tested pathways or terms, an explicit manifest
requirement. The eligible-universe check is consistent with the
[Gene Ontology enrichment guidance](https://geneontology.org/docs/go-enrichment-analysis/).

**Survival censoring, attempts 009–010.** Both correctly identified events at
3 and 8 and censoring at 6 and 10, rejected ordinary regression that ignores
event labels, and proposed Kaplan–Meier. Baseline's “survival probabilities of
0.75 after time 3 and 0.375 after time 8” and median of 8 agree with the toy
product-limit calculation. Skills stated the event coding assumption and
explained that “With only four observations and no predictors, regression is
not warranted.” Neither defined the event, time origin and target survival
quantity as an estimand, stated independent or non-informative censoring, or
named checks for censoring patterns, risk-set support or uncertainty. Event
coding alone does not address the censoring assumption.
[Kaplan and Meier, 1958](https://doi.org/10.1080/01621459.1958.10501452).

## Skill access and limitations

The runner reported `UNOBSERVABLE` and an empty tracked-read list for every
turn. The raw JSONL contains successful PowerShell reads of staged relative
paths, with matching document headings in the output:

| Attempt | Trace item | Files read |
|---|---|---|
| 002 | `item_1` | Research specification |
| 004 | `item_1` | Research specification and bulk RNA-seq differential expression |
| 008 | `item_1` | Verification before scientific claims |

The runner's detector expects an absolute path and a matching single-file
body. These raw trace observations establish file access. All activation
judgments remain unverified. No benchmark fixture or runner behavior was changed
for the review.

Each case has one response per mode, with baseline first in every pair.
The observed differences describe those responses. They cannot establish
causality, activation, or general skill effectiveness.
