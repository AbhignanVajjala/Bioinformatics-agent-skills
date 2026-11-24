# Scientific evidence and its limits

The [Phase 7 RNA-seq review](maintainer-reviews/2026-11-24-bulk-rnaseq-review.md)
records Abhignan Vajjala's human-directed, AI-assisted maintainer investigation
separately from new software checks. The 32 failed adversarial checks reflect
shared defects across two methods, not 32 independent defects. Strict config/TSV
contracts, exact identities, normalization/fitting diagnostics and scoped Python
readiness now address those findings. Original synthetic effect/FDP observations
remain historical; a realized FDP above 5% is not proof of broken FDR control.
Independent external methodological review remains incomplete. No agent benchmark
or claim of improved instruction-following accompanies these utility corrections.

All 17 skills remain EXPERIMENTAL. The collection contains seven domain skills
and ten foundation/maintainer instruction workflows. No independent biological
validation, clinical validation or external peer review is established here.

**Successful automated testing demonstrates the behavior of the tested
implementation under the evaluated conditions. It does not independently
establish biological validity, clinical applicability or improved AI-agent
scientific reasoning.**

## Implemented functionality

The [Python package](../src/bioskills/validators.py) provides seven scientific
validator APIs and a CLI. [Domain workflows](../src/bioskills/domain_workflows.py)
implement a synthetic COBRApy recipe and a descriptive two-assay cross-view
baseline. [Expanded utilities](../src/bioskills/expanded.py) implement pseudobulk
aggregation, Fisher/BH ORA and scoped format inspection; the
[metadata client](../src/bioskills/retrieval.py) supports dry-run and bounded
public metadata requests. [R recipes](../recipes/rnaseq/run.R) fit established
DESeq2 and edgeR models under a pinned environment.

Implementation existence is established by these source files and their input
contracts. It does not establish that a computation was run on a particular
dataset. Templates describe contracts and are not execution evidence.

## Executed software validation

These are preserved **pre-Phase-4 execution records**, not new scientific results:

| Evidence | Observed result | Auditable record |
|---|---|---|
| Structural/fixture tests and scientific Python checks | Linux: 217 passed, four Windows-only skips; zero failures at `aeb13bd` | [CI run](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44559842977), [validator tests](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/aeb13bdb1cd0992bdac4700da19147229e02e914/tests/test_validators.py), [domain tests](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/aeb13bdb1cd0992bdac4700da19147229e02e914/tests/test_domain_recipes.py) |
| Local Windows regression | 207 passed, 14 skipped, zero failures; 13 libsbml-policy skips and one symlink-creation skip | [Phase 3.11 implementation record](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/afd14e927e49a06df3ad7268532769c6e93002fb/docs/implementation-status.md) |
| Extracted distribution | Fresh Windows/Linux installs, all seven command help interfaces, first-use, cross-view and metabolic examples passed in hosted CI | [Standalone jobs](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44559842977); agent-host discovery was not tested |
| R/Bioconductor recipes | 18 checks passed: six real synthetic model fits plus twelve deliberate input/design rejections | [R CI](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/actions/runs/44559842600), [test recipe](../recipes/rnaseq/test.R), [earlier hashed result evidence](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/references/phase3-r-execution.json) |

The pinned R environment is R 4.4.3, Bioconductor 3.20, DESeq2 1.46.0 and edgeR
4.4.2. Transitive packages are inventoried in `sessionInfo.txt`, not fully
content-locked. CI artifacts/logs identify the source and execution conditions;
artifact hosting retention can limit later retrieval. Retain checksums and
locally obtained evidence when reproducing a study.

New documentation/package checks belong in the current
[implementation record](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md).
They do not replace or reinterpret the historical results above.

## Scientific methodological validity

Count-scale declarations, exact IDs, biological-unit declarations, rank/residual
degrees of freedom, explicit contrasts, selected/tested universes, BH policies,
subject partitions and solver feasibility are checked within scoped workflows.
[Scientific integrity](scientific-integrity.md) and the
[technical walkthrough](maintainer-technical-walkthrough.md) explain the assumptions.

These checks cannot establish truthful provenance or biological identity,
adequate power, absence of unmeasured confounding, correct missingness assumptions,
all forms of leakage, a biologically adequate metabolic model, or a study-wide
multiplicity plan. A minimum replicate gate is not a universal adequacy rule.
Descriptive association is not causality; optimized flux is not a measurement.

Independent human methodological review is **NOT_REVIEWED**. Biological and
clinical validation are **NOT_ESTABLISHED**. The walkthrough's human checklist
now records a scoped maintainer self-review; no independent external review or signature is recorded. Computational role passes are not
independent peer review.

## AI agent effectiveness

The original Phase 2 pilot executed ten Codex CLI turns across five paired
baseline/skill-enabled cases, one sample per condition per case. Its automated
review remains provisional: **0 PASS, 4 FAIL, 6 BLOCKED**. The
[original scores](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/agent-benchmark-scores.json),
[review](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/agent-benchmark-summary.md)
and [provenance](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/agent-benchmark-provenance.md)
retain the prompts, criterion judgments and evidence locators.

All executions completed, but execution success is separate from scientific
success. Four skill-file reads across three turns establish access only.
UNOBSERVABLE activation remains unverified. The enrichment responses omitted
required multiplicity control; survival responses omitted required estimand,
censoring assumptions and diagnostics. Historical verdicts were not revised.

Phase 3's 16 trigger and ten adversarial scientific fixtures remain NOT_RUN.
The complete agent benchmark has not run, and improved agent effectiveness has
not been demonstrated. A fixed protocol, adequate repeated comparisons, observable
activation where possible and independent methodological assessment are needed
before making stronger claims. No new agent sessions were run for Phase 4.

## Phase 5 maintainer self-review and structural correction

[Abhignan Vajjala's dated reproduction](maintainer-reviews/2026-11-24-metabolic-model-review.md) records human-directed, AI-assisted investigation of the single-compartment defect. The original artifacts are in Codespaces and are unavailable here; manual results are supplied observations, not reconstructed original evidence. The permanent fixture uses extracellular uptake, transport and cytoplasmic drains. New automated assertions cover structure, pFBA30, FVA90, knockouts, warning capture and solver rejection. This scoped self-review does not complete independent methodological or biological review. Original Phase 1–4 outputs and agent judgments remain historical and unchanged.

## Phase 6 multi-omics maintainer investigation

[Abhignan Vajjala's second scoped investigation](maintainer-reviews/2026-11-24-multiomics-review.md)
records human-directed, ChatGPT-assisted Codespaces observations at 0.2.2 separately
from source inspection, new automated regressions and a Decimal mathematical
reference. It identifies eight validation/numerical defects, the constant-unmapped
feature limitation and three methodological considerations. New code requires
meaningful metadata and nonempty maps, uses shared stable correlation, records
normalization denominators and reports subjects/repeats/partitions honestly.
The ±1e308 example now agrees with the independently calculated reference rather
than returning an unreliable zero. No advanced integration, inferential/predictive
validation, independent external review or improved agent effectiveness is claimed.
Original benchmark prompts and judgments remain unchanged.

## Phase 8 consolidated domain investigation

Four human-directed maintainer self-reviews with AI-assisted scripts cover
[pseudobulk](maintainer-reviews/2026-11-24-pseudobulk-review.md),
[ORA](maintainer-reviews/2026-11-24-enrichment-review.md),
[formats](maintainer-reviews/2026-11-24-file-formats-review.md) and
[public metadata](maintainer-reviews/2026-11-24-public-metadata-review.md).
Supplied Codespaces observations at 98a9456 comprise 100 checks (44 PASS,
35 INVESTIGATE, 21 ASSESS), not distinct defect counts or accuracy rates.
Original files/hashes are unavailable; none are fabricated. Assessment cases
also expose confirmed arithmetic defects. Exact combinatorial ORA references
are separate from biological evidence.

Three historical live requests were observed on November 24, 2026 at that
source revision; earlier release NOT_RUN records remain unchanged. The new
corrected client separately completed scoped live GEO/SRA/Ensembl checks, with
bounded raw response hashes recorded in its review. HTTP success, identity
relationships and computational correctness remain distinct claims. New
offline regressions and native R cross-skill lineage checks are reported in
implementation status. No new model sessions or effectiveness benchmark ran.
Independent methodological review, real-data calibration, differential-state
modeling, full format conformance and biological validation remain incomplete.
