# Instruction-skill behavioral maintainer review — November 24, 2026

Abhignan Vajjala conducted a human-directed benchmark using the local Windows
Codex runtime, with AI-assisted scripts and preliminary adjudication. This is
maintainer self-review, not independent external peer review. Phase 9 adds a
separate unblinded AI-assisted criterion review; human methodological validation
is pending. No new live agent evaluation was run for these corrections.

## Frozen evidence and integrity

Original revision: **98a9456132fb474996f4c5d566065925ed79551b**. Environment:
Windows MXC, Python 3.14.8, Codex CLI 0.168.0, ChatGPT authentication. Requested
model gpt-6.1-sol; resolved model and reasoning effort remain **UNVERIFIED**.
Original evidence locator is the supplied LOCALAPPDATA behavioral-audit-20261124-
191448-817601/evidence directory; private absolute paths and authentication data
are excluded from publication. Original inputs and execution files were read,
not modified. A preserved source ZIP and custom-manifest snapshot were available.

| Artifact | Verified SHA-256 |
|---|---|
| Source ZIP | e28db93201d36391a957085235defd13448b0225960ebe0608421d52c3b6ca3e |
| Frozen criteria | 61b5d035b6067317ba49f9b7a08f32fa1edfa39a22243d209e60d6df0eb53530 |
| Execution report | 22b3dfe28237c8bd7c0e835a257f107610d6a1939187c32cb115a7d00a2c717e |
| Original review text | ad28d3f494c000f3abdb6ccab44fb1e4fec2f494b7dbfd6ca62b06811363a49c |
| Custom scientific manifest | a4773e0fbe870e6e9a7668e1de4719f03fea1d09ab94b975f89cfa7a8b4dde8b |

The original preflight/smoke family adds 16 verified artifact hashes, including
the harmless smoke response; these are separate from scientific scoring.

All **160 turn artifacts** (40 each of prompt, response, JSONL and stderr),
original input hashes and skill snapshot hashes verified. JSONL replay with the
original skill bytes reproduces **30 reads and 19/20 target reads**. All 40
fresh turns completed, with no execution failure. Activation stays UNOBSERVABLE;
original scientific evaluation stays NOT_RUN. The supplied provenance also names
script SHA 98ff3b5f0c863ec91bcd350e655cd85602b2d35a7fa916671e3c9e94c8442f42;
that script file was not located, so its hash is **UNVERIFIED**, not reassigned to
the different, verified runner file.

Recorded aggregate usage: 1,048,692 input tokens, including 692,608 cached input
tokens; 18,542 output tokens and 266 reasoning-output tokens. These are reported
runtime counters, not independent model-configuration verification or a price.
Per-turn timings and counters remain in the sanitized review.

## Separate provisional adjudication

The supplied preliminary assessment is preserved: baseline **16 full passes /
4 incomplete**, enabled **18 / 2**, with no observed frozen-rubric critical
failure in either condition. One sample per condition/case, unblinded review,
unknown resolved configuration, a high baseline ceiling and shared-model review
prevent a claim of statistically established or causal skill effectiveness.

The original criterion-level adjudication file was not supplied; the review
text contains criteria and raw responses. Phase 9 reconstructs criterion-level
reasoning separately, explicitly labeled provisional, with exact response
excerpts/offsets, missing-criterion reasons, critical-failure observations,
original prompt/response hashes and reviewer visibility. It reproduces the supplied
aggregate counts without changing original prompts, criteria, responses or statuses.
See the [machine-readable review](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/behavioral-audit-2026-11-24.json)
and [review decisions](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reviews/behavioral-audit-2026-11-24.json).
These are judgment records, not automated scientific certification.

| Frozen case | Baseline omission | Enabled omission |
|---|---|---|
| audit-04-invalid | No explicit valid small regression control | None under frozen criteria |
| audit-05-invalid | No explicit failed-log preservation and clean output directory | None under frozen criteria |
| audit-06-valid | Missing concrete mechanistic/human evidence requirements | Same omission; no target file read observed |
| audit-08-invalid | No explicit unsupported-claim evaluation failure rule | Same omission |

For Gene X, both responses reject human causation correctly. The enabled answer
says "candidate for further investigation" but does not identify the missing
evidence. No observed read is not conclusive proof of nonactivation. The enabled
extraction answer also requires nonempty evidence strings: its demonstration has
an explicit nonreporting sentence, but that contract is inconsistent for genuine
silence. This generalization risk is recorded separately, not promoted to a new
retrospective frozen-rubric critical failure.

## Review of all ten instruction skills

| Skill | Disposition and evidence |
|---|---|
| research-specification | Retained: donor blocking, independent units, confounding, count-aware methods and interpretation limits satisfy the frozen cases |
| research-task-decomposition | Retained: failed joins block dependents; resource limits and training-fold preprocessing preserved; independent QC need not run concurrently under an 8 GB cap |
| scientific-context-engineering | Retained: declarations separated from verification; stale outputs and missing identities remain explicit |
| scientific-debugging | Narrow clarification: exact arithmetic, explicit numerical downstream invalidation, preserved failing evidence and valid controls |
| research-reproducibility-audit | Narrow clarification: exact original-input reproduction versus changed-input execution, clean outputs, real command status and cached/fresh evidence |
| source-grounded-scientific-reasoning | Refined discovery for evidence/causal/cross-species assessment; require specific stronger-claim evidence gaps |
| verification-before-scientific-claims | Retained: prediction/association versus biological/clinical evidence and missing-artifact gates already explicit |
| scientific-prompt-engineering | Added five missingness states, empty evidence for silence and measurable unsupported-value/evidence/abstention/schema failure criteria |
| scientific-agent-orchestration | Retained: persona-only roles are not independent reviewers; critical gates cannot be overruled by majority vote |
| bioinformatics-skill-authoring | Retained: bounded experimental scope, positive/invalid fixtures, no fabricated execution or universal certification |

The shared QUICK policy remains unchanged: essential safeguards without mandatory
files or FULL-mode documentation overhead. Static structure and a passing example
cannot establish consistent future agent adherence.

## Versioned benchmark and runtime corrections

Original manifests, rubric and Phase 2 judgments remain unchanged. The new
phase9-instruction-integrity-v1 definition has **68 development triggers** across
17 skills (legitimate, out-of-scope, adversarial and invalid in-scope) plus ten
compound held-out preparations. Invalid in-scope requests should engage safeguards;
they are not out-of-scope negatives. Held-out compositions are candidate-isolated
but author-visible, not independently sealed or empirically proven difficult.

Availability, reads, trigger appropriateness, judged adherence, scientific
correctness, grounding, critical failures, response efficiency and execution
completion are separate records. Quote/offset validation checks review integrity,
not scientific truth. Blinded exports hide condition/read/usage metadata; response
content can still reveal condition. Explicit complete grading precedes unblinding.

Paired repeats use identical prompts and requested model/effort/tool configuration,
with recorded condition order and seed. Requested configuration is distinct from
unobserved resolved configuration. Live progress, bounded child termination,
partial checkpoints and strict compatible resume use fresh independent sessions;
failed turns do not auto-retry. Historical evidence is not resumed or rewritten.

Local inspection found Codex **0.171.0-alpha.13.2**, different from the benchmark.
Only version/help inspection was performed. New live execution remains NOT_RUN.
Windows keeps explicit MXC, strict configuration, read-only workspace, disabled
network and never-approve restrictions; no windows.require_mxc CLI override or
weaker fallback is introduced.

Official [permissions documentation](https://learn.chatgpt.com/docs/permissions)
and [Windows sandbox guidance](https://learn.chatgpt.com/docs/windows/windows-sandbox)
were consulted on November 24. Linux/WSL use bubblewrap/seccomp, and native Windows
supports MXC. No Linux/Codespaces environment here demonstrated equivalent isolation;
the harness therefore continues to block Linux live execution. Platform support
is not inferred from running inside a container. No sandbox/security policy was
bypassed. Further environment-specific proof is required before enabling it.

## Cross-skill computational evidence

The supplied historical workflow at the original revision had 600 genes, 48 cells,
12 donors and 50 planted upregulated genes: **11/13 checks passed**, with **two
identifier-preservation failures**. Both methods recovered all 50 planted genes;
DESeq2 selected two additional nonplanted genes, edgeR none under positive-effect
selection. Independent Fisher/BH checks agreed within the declared tolerances.
Both filtering exports corrupted all 600 leading-zero gene IDs while reporting
PASS. Original integration files/seed were not supplied; none are reconstructed.

Phase 7 already fixes the strict R reader and filtering export. Phase 9 adds a
new reproducible seed-9421 fixture of the same dimensions, not a recreation of
unavailable original inputs. It verifies exact cell/pseudobulk conservation,
all 600 filtering IDs and retained result/normalization/dispersion IDs for **both**
R methods, eligible positive-effect FDR selection, exact mapping, independent
integer-combination Fisher/manual BH references and downstream hashes.

From the full universal extraction with Python dependencies installed:

```text
python examples/pseudobulk-to-enrichment/run.py --output new-interoperability --prepare-only
```

Preparation alone leaves native DE/ORA NOT_RUN. Omit --prepare-only only in the
pinned R environment to execute both methods. Clean output directories and actual
exit status are required. This is manually constructed executable interoperability,
not autonomous agent orchestration or independent biological validation.

Actual validation counts, local solver/R limitations, failed attempts and hosted
publication results are recorded in
[implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md).
A repeated post-correction behavioral comparison requires separate maintainer
approval and independent methodological adjudication; no new large benchmark ran.
