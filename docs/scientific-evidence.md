# Scientific evidence and its limits

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
contains no completed reviews or signatures. Computational role passes are not
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
