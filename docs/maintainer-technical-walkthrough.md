# Maintainer technical walkthrough

This guide supports a human maintainer's own reproduction and methodological
challenge. It does not record that Abhignan Vajjala or an independent reviewer
has completed an entire independent review. The metabolic and multi-omics rows
record scoped maintainer self-reviews supplied in Phases 5 and 6. The RNA-seq
human completion field now records the scoped Phase 7 self-review. Independent
external review remains **NOT_REVIEWED**. New automated corrections and
regression tests are distinct from supplied maintainer observations.

## Preparation and evidence discipline

Keep immutable inputs and record source version/commit, environment, exact
commands, exit statuses, parameters and input/output hashes. Install the Python
environment using [TOOLKIT_INSTALL.md](../TOOLKIT_INSTALL.md); commands below
assume that environment's Python. For R, prepare its separately pinned runtime.
Run from the complete extraction or repository root, with new output directories.

Python examples run from the universal ZIP. Commands using `tests/` need the
**full development checkout**, installed with its `dev,examples` dependencies.
The ZIP excludes development tests and evaluation reports. Repository-only test
links below point to the scientific source baseline used to prepare this guide.
Do not silently install runtimes, bypass native execution policies, or replace
unavailable methods with another statistical procedure. Record BLOCKED/NOT_RUN.

## Workflow 1: bulk RNA-seq differential expression

### Entry points and dependencies

The [R implementation](../recipes/rnaseq/run.R) performs the actual model fits.
Its [environment specification](../recipes/rnaseq/environment.json) pins R 4.4.3,
Bioconductor 3.20, DESeq2 1.46.0 and edgeR 4.4.2. The
[R test driver](../recipes/rnaseq/test.R) generates synthetic fixtures and checks
both methods. [Python gates](../src/bioskills/science.py) include `check_counts`
and `validate_counts`; the [validator API/CLI](../src/bioskills/validators.py)
adds `check_sample_ids`, `check_design_rank` and `check_replication`.
The [original example](../examples/bulk-rnaseq/run.py) executes QC/readiness,
not differential-expression modeling.

### Follow the data and model

`run.R` reads strict UTF-8 counts TSV with gene IDs in the first column, sample metadata
with `sample_id`, `subject_id`, `condition` and applicable `batch`, and a JSON
configuration declaring organism, reference, count generation, measurement type,
design and reference/treatment levels. It accepts declared raw gene counts.
FASTQ/BAM, transcript estimates, TPM/FPKM and transformed expression need other
upstream workflows; an integer-looking matrix cannot authenticate its origin.

The R gates reject empty/nonnumeric/nonfinite/negative/noninteger/oversized
counts, missing/blank/duplicate identifiers and zero library totals. Count-column
and metadata sample sets must agree. A permuted sheet is rejected by default;
`align_samples: true` explicitly permits `match`-based metadata ordering.
Original input files are not rewritten.

The Phase 7 parser validates every field count and header without implicit row
names or categorical type inference. Required configuration values are nonblank
scalar strings; duplicate JSON keys (including escaped aliases) and incorrectly
typed Boolean options reject before fitting. Numeric-looking categorical IDs
remain exact strings. Original metadata.tsv and explicit factor-code mappings
separate external identities from model-only names. A named condition term
identifies the coefficient; no positional last-column assumption is used.

Two declared conditions and independent subjects are required. The two-subject
minimum per condition supplies no power guarantee. Unpaired/batch recipes
reject repeated subjects. Paired data require exactly one specimen per subject
per condition. The supported formulas are `~ condition`, `~ donor + condition`
and `~ batch + condition`. `model.matrix` and QR rank must give full column rank
and positive residual degrees of freedom. A perfectly confounded batch/treatment
effect is not repaired by including batch in the formula.

DESeq2 keeps genes with counts at least ten in at least two samples, constructs
`DESeqDataSetFromMatrix`, runs native `DESeq`, and requests the explicit
treatment-versus-reference contrast with `results(alpha=0.05)`. Native independent
filtering and Cook's outlier behavior remain enabled; some p-values/padj can be
NA. No effect-size shrinkage is executed. Normalized diagnostics use DESeq2's
normalized counts; they are not replacement input counts for a second fit.

edgeR constructs `DGEList`, uses `filterByExpr`, TMM normalization,
`estimateDisp`, `glmQLFit(robust=FALSE)` and `glmQLFTest`. The condition term and
named coefficient identify the contrast independently of column position.
`topTags(adjust.method="BH")` exports the tested family with `sort.by="none"`.
Its `normalized.tsv` contains CPM, unlike the DESeq2 normalized-count diagnostic.
DESeq2's adjusted results also use its native BH procedure. Neither choice
supplies a study-wide multiplicity plan across additional contrasts/cell types.
Do not select a method by whichever gives smaller p-values.

Post-filter library totals now gate normalization explicitly. Requested and actual
DESeq2 dispersion fitting are recorded, including native local fallback. Size
factors or TMM/effective libraries, method-specific limitations, warning/message
events and ignored covariates accompany staged success/failure statuses. An
unpaired fit does not adjust a supplied batch; known confounding is disclosed.
An unsupported ratio normalization stops without substituting another method.
Independent filtering and Cook-related missing values remain native.
The [dated RNA-seq review](maintainer-reviews/2026-11-24-bulk-rnaseq-review.md)
preserves supplied historical numbers separately from new regression results.

### Reproduce and inspect

First install jsonlite 1.8.9 and BiocManager 1.30.25 as described in the
[toolkit guide](../TOOLKIT_INSTALL.md), then use the pinned installation recipe.
Use a fresh working copy without a previous `artifacts/rnaseq-ci` tree:

```text
Rscript recipes/rnaseq/install.R
Rscript recipes/rnaseq/test.R
Rscript recipes/rnaseq/test-validation.R
```

The test driver creates six real fits: both methods in unpaired, paired and
batch designs. To inspect one explicit rerun with a new output path:

```text
Rscript recipes/rnaseq/run.R deseq2 artifacts/rnaseq-ci/deseq2-unpaired/counts.tsv artifacts/rnaseq-ci/deseq2-unpaired/samples.tsv artifacts/rnaseq-ci/deseq2-unpaired/config.json artifacts/walkthrough-deseq2
```

Successful output contains `results.tsv`, `normalized.tsv`, `dispersion.tsv`,
`dispersion.pdf`, `filtering.tsv`, `design.tsv`, `analysis-status.json` and
`sessionInfo.txt`. Inspect comparison direction, formula, rank, residual DF,
retained genes, adjustment, versions and input MD5s in the status. The test driver
also emits `artifacts/rnaseq-ci/test-summary.json`. Record the source revision
separately; the R status is not the Python `analysis_run.json` contract.

### Negative controls and reviewer questions

The R driver expects nonzero exit plus `status: FAIL` and
`analysis_status: NOT_RUN` for permuted metadata, TPM declaration, duplicate IDs,
confounded design, subject pseudoreplication and missing count provenance, for
each method. These twelve expected rejections are successful tests of a failure
gate, not successful scientific analyses.

In the full checkout, inspect the
[Python API/CLI fixtures](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/afd14e927e49a06df3ad7268532769c6e93002fb/tests/test_validators.py)
and [count/design controls](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/afd14e927e49a06df3ad7268532769c6e93002fb/tests/test_science.py):

```text
python -m pytest -q tests/test_validators.py tests/test_science.py
```

A reviewer should ask: Which samples are independent biological units? Is the
requested contrast estimable? Who verified count generation and annotation?
Which genes and contrasts form the error-control family? How were NA results,
outliers, filtering and uncertainty handled? Are repeated measures more complex
than this paired recipe allows?

Defensible limit: the seeded synthetic effect tests software behavior. It is
not a biological discovery, a power study, an external-cohort replication or a
clinical result. Unmeasured confounding and model adequacy still need review.

## Workflow 2: constraint-based metabolic modeling

See the [dated maintainer investigation](maintainer-reviews/2026-11-24-metabolic-model-review.md). The corrected base has two metabolites and three reactions; the domain adds PRODUCT for four reactions. Named e/c compartments distinguish EX_a from intracellular demands. pFBA total flux is 30 (including transport), with biomass ten; FVA90 ranges are EX_a [-10,-9], TRANSPORT [9,10], BIOMASS [9,10], PRODUCT [0,1]. Uptake seven/growth four gives product three. Scoped warning evidence and knockout-controls.csv supplement numerical checks. validate_toy_structure is fixture-specific, not a general biological-model validator.


### Entry points and procedure

[Domain implementation](../src/bioskills/domain_workflows.py): `metabolic_recipe`
and `check_fba_status`. [Shared gates](../src/bioskills/science.py): `toy_model`
and `solve_model`. [Example entry point](../examples/domain-recipes/run.py):
`metabolic`. Dependencies are COBRApy 0.29.1, GLPK/swiglpk, libsbml, NumPy and
pandas. External scientific libraries are installed, not vendored in the ZIP.

The recipe builds an explicitly synthetic model, adds a product reaction and
an OR gene rule for biomass, writes SBML/FBC and reads it back. It records
reaction/metabolite/gene/compartment inventory, objective context, exchanges,
`model.medium` and Python parsing warnings. The report now captures scoped COBRApy logging and Python warnings with stage/expected-control labels; parsing_warnings remains a loading-only compatibility field.

`solve_model` requires a nonzero objective and finite ordered bounds and checks
actual optimal status. `check_fba_status` additionally requires finite fluxes
and objective, maximum absolute `S @ v` residual and bound violation within
the fixed default tolerance `1e-7`. Invalid status blocks interpretation.
FBA maximizes biomass under the declared medium. pFBA preserves the original
optimum while minimizing absolute flux; its reported total-flux objective is
not biomass growth. The recipe exports the original biomass flux separately.
FVA uses `fraction_of_optimum=0.9`, not a statement that all returned fluxes
are simultaneously achievable or measured.

Gene deletion applies the GPR: deleting one member of `g1 OR g2` leaves the
reaction enabled by the other gene; deleting both blocks biomass. Reaction deletion directly blocks biomass
and is a different intervention. The fixture checks growth 10, 0 and 0 for the
single-gene, double-gene and reaction deletions respectively, in arbitrary toy
units. It evaluates product maxima 10, 5 and 1 at biomass minima 0, 5 and 9.
Medium uptake restricted to five yields growth five.

All perturbations use `with model:` and the final medium and optimum are checked
against baseline. An empty medium with forced positive growth is infeasible.
A deliberately open source, uncapped transport and uncapped biomass drain are unbounded; COBRApy may raise an
optimization exception, so the actual solver status is retained and interpretation
rejected. An exception or solver label must not become a fabricated flux result.

### Reproduce, evidence and negative controls

```text
python examples/domain-recipes/run.py metabolic --output artifacts/walkthrough-metabolic
```

Inspect `synthetic-model.xml`, `fva.csv`, `gene-deletions.csv`, `results.json`
and `analysis_run.json`. The latter records actual commands, versions and hashes;
results record the medium, numerical checks, distinct pFBA objective, trade-offs,
infeasible/unbounded controls and restoration. The
[original example](../examples/metabolic-modeling/run.py) is retained separately.

Full-checkout tests include infeasible/unbounded handling, restoration and a
deliberately altered flux that must fail the bounds/mass-balance gate:

```text
python -m pytest -q tests/test_domain_recipes.py -k "metabolic or flux_bounds"
```

[Exact test implementation](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/afd14e927e49a06df3ad7268532769c6e93002fb/tests/test_domain_recipes.py).
If a native dependency is blocked, record BLOCKED; do not bypass policy or count
a skipped test as an executed optimization.

A reviewer should ask: Why this objective and medium? What are the units and
exchange signs? Is the organism model curated and balanced? Why FVA at 90%?
Does the GPR capture real isoenzymes? Are product comparisons made at the same
growth requirement? Were temporary changes restored?

Defensible limit: this is a steady-state, constraint-based prediction in a tiny
synthetic model. It measures neither cellular flux nor regulation. Increasing
a reaction bound does not establish gene overexpression, and optimization does
not prove engineering benefit, mechanism or therapeutic efficacy.

## Workflow 3: matched multi-omics cross-view analysis

### Entry points, identity and computation

[Domain entry point](../src/bioskills/domain_workflows.py): `cross_view_analysis`,
implemented in [omics](../src/bioskills/omics.py).
[Shared implementation](../src/bioskills/science.py): `reconcile_omics` and
`validate_matrix`. [Synthetic driver](../examples/domain-recipes/run.py):
`multiomics_example`. This baseline uses NumPy/pandas and exactly two assays.
It does not fit an integration latent-variable model or supervised predictor.

Each feature-by-assay-sample matrix must have unique IDs and finite values.
Its mapping index must exactly match its column IDs in order; row-order matching
without checking IDs is invalid. A permuted sheet is rejected rather than
silently joined. Mappings declare specimen, subject, timepoint and partition.
Shared specimen IDs must identify consistent subjects and timepoints, and each
assay must map specimens uniquely. Reconciliation uses explicit specimen IDs,
reports unmatched/excluded samples and retains the matched intersection.
Labels remain declarations, not independent authentication of biological identity.

Subject-level split labels must be train/test/validation and consistent across
all appearances and assays. A declared subject in both train and test fails.
This check cannot discover unrecorded aliases or establish that future
preprocessing avoided leakage. This workflow fits no supervised model; if one
is added, grouped splitting must precede learned preprocessing and selection.

Declared raw RNA counts must be nonnegative integers with count-generation
provenance and positive library totals; the baseline uses log2(CPM+1).
Declared protein/metabolite log2 intensities are left unchanged. Feature
namespaces and annotation releases must be declared. Missing/nonfinite values
are rejected, not universally zero-imputed. Constant mapped features are rejected;
constant unmapped features are reported without blocking other valid pairs.
A supplied one-to-one feature map identifies pairs; no automatic biological
mapping is inferred. Shared `stable_pearson` computes a descriptive Pearson correlation
across matched samples for each mapped pair. There are no inferential p-values,
prediction scores or claims of causal regulation.

Require nonempty feature maps, unique mapping columns and all required fields
before access. Whitespace-only declarations and mixed-type identifiers fail
controlled validation. Legitimate synchronized assay/metadata reordering is valid.
Declare `count_universe: complete_supplied_matrix` and nonblank normalization_scope;
all supplied RNA rows contribute before pair selection. Report exact denominators
and their source; external denominators/preselected universes are unsupported.
Counts and totals over 2^53-1 fail the supported exact-integer numerical scope.
Power-of-two scaling and compensated sums prevent the observed extreme-intensity
overflow. Mapped constants, unreliable near-constants and arithmetic warnings
reject the entire computation; no undefined pair is replaced with zero.
Reports distinguish matched specimens/subjects, repeats, timepoints and partition
counts. All matched partitions contribute; no predictive evaluation is performed.
See the [dated investigation](maintainer-reviews/2026-11-24-multiomics-review.md)
for historical values, defects, reference calculations and review limitations.

### Reproduce, evidence and negative controls

```text
python examples/domain-recipes/run.py multiomics --output artifacts/walkthrough-cross-view
```

The driver generates seeded synthetic RNA counts and protein intensities, writes
and reloads `rna-matrix.csv`, `protein-matrix.csv` and their mapping CSVs, then
exports `results.json` and `analysis_run.json`. Inspect the matched/exclusion
audit, declared scales and namespaces, transformation labels, correlations,
input/output hashes and versions. The driver exercises four mapped feature pairs;
this is not a fitted MOFA2 or SNF analysis.

In the full checkout:

```text
python -m pytest -q tests/test_domain_recipes.py -k cross_view
```

The [scientific fixtures](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/afd14e927e49a06df3ad7268532769c6e93002fb/tests/test_domain_recipes.py)
include a positive calculation and deliberate failures for permutation, duplicate
specimens, subject leakage, TPM scale, timepoint mismatch, missing namespace,
missing values and ambiguous feature mapping. A missing-assay exclusion audit
is separate from a malformed/missing-value gate.

A reviewer should ask: Who verified specimen identity? What happens to unmatched
samples? Why are the declared scales appropriate? What is the missingness
mechanism? Does the one-to-one feature map make biological sense? Can a shared
subject enter different partitions? What justifies the interpretation of a
correlation?

Defensible limit: this is descriptive matched-feature association. Correlation
does not establish causality, pathway activation or biomarker validity. MOFA2,
SNF, supervised multiblock fitting and general missing-data integration are not
implemented/executed by this baseline.

## Human reproduction and methodological-review checklist

Complete a row only after an actual human performs and records the work. Software
test success is not a human signature. Preserve separate review records when
multiple people or environments are involved.

| Workflow | Review status | Actual execution date | Human reviewer | Environment and source revision | Findings and artifact hashes | Unresolved issues |
|---|---|---|---|---|---|---|
| RNA-seq | MAINTAINER_SELF_REVIEW_REPORTED; not independent | 2026-11-24 | Abhignan Vajjala | Codespaces Python 3.12.3/R 4.4.3/Bioc 3.20; DESeq2 1.46.0/edgeR 4.4.2; 98a9456 | Supplied baseline/adversarial observations; original hashes unavailable locally; see dated review | External review, real-data calibration and biological validation incomplete |
| Metabolic modeling | MAINTAINER_SELF_REVIEW_REPORTED; not independent | 2026-11-24 | Abhignan Vajjala | Codespaces Linux/Python 3.12.3; 98a9456, package 0.2.2 | Original artifacts preserved in Codespaces; hashes unavailable locally; see dated review | External review and biological validation incomplete |
| Multi-omics | MAINTAINER_SELF_REVIEW_REPORTED; not independent | 2026-11-24 | Abhignan Vajjala | Codespaces Linux/Python 3.12.3, NumPy 2.2.6/pandas 2.2.3/SciPy 1.15.3; 98a9456, package 0.2.2 | Supplied baseline/adversarial observations; original artifact hashes unavailable locally; see dated review | External review, real-data and biological validation incomplete |

- [ ] Reproduced commands and inspected actual artifacts, warnings and failures.
- [ ] Challenged biological units, identity, contrasts, confounding and leakage.
- [ ] Reviewed normalization, multiplicity, model assumptions and numerical tolerances.
- [ ] Independently assessed interpretation and the boundary of each supported claim.
- [ ] Recorded qualifications relevant to the review, scope and actual independence.
- [ ] Recorded discrepancies and unresolved issues; no automatic promotion to validated.

Independent human methodological review and independent biological validation remain
incomplete. See [scientific evidence](scientific-evidence.md) and
[development transparency](development-and-ai-assistance.md).
