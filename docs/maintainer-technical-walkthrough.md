# Maintainer technical walkthrough

This guide supports a human maintainer's own reproduction and methodological
challenge. It does not record that Abhignan Vajjala or an independent reviewer
has completed that work. All human completion fields below are **NOT_REVIEWED**.
The scientific implementations and their assertions are unchanged by this guide.

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

`run.R` reads counts TSV with gene IDs in the first column, sample metadata
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
`estimateDisp`, `glmQLFit(robust=FALSE)` and `glmQLFTest`. The last design column
is the treatment coefficient for these constrained two-condition formulas.
`topTags(adjust.method="BH")` exports the tested family with `sort.by="none"`.
Its `normalized.tsv` contains CPM, unlike the DESeq2 normalized-count diagnostic.
DESeq2's adjusted results also use its native BH procedure. Neither choice
supplies a study-wide multiplicity plan across additional contrasts/cell types.
Do not select a method by whichever gives smaller p-values.

### Reproduce and inspect

First install jsonlite 1.8.9 and BiocManager 1.30.25 as described in the
[toolkit guide](../TOOLKIT_INSTALL.md), then use the pinned installation recipe.
Use a fresh working copy without a previous `artifacts/rnaseq-ci` tree:

```text
Rscript recipes/rnaseq/install.R
Rscript recipes/rnaseq/test.R
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

### Entry points and procedure

[Domain implementation](../src/bioskills/domain_workflows.py): `metabolic_recipe`
and `check_fba_status`. [Shared gates](../src/bioskills/science.py): `toy_model`
and `solve_model`. [Example entry point](../examples/domain-recipes/run.py):
`metabolic`. Dependencies are COBRApy 0.29.1, GLPK/swiglpk, libsbml, NumPy and
pandas. External scientific libraries are installed, not vendored in the ZIP.

The recipe builds an explicitly synthetic model, adds a product reaction and
an OR gene rule for biomass, writes SBML/FBC and reads it back. It records
reaction/metabolite/gene/compartment inventory, objective context, exchanges,
`model.medium` and Python parsing warnings. Library logging can contain warnings
not captured by Python's warnings mechanism.

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
A deliberately open source/uncapped drain is unbounded; COBRApy may raise an
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

[Domain implementation](../src/bioskills/domain_workflows.py): `cross_view_analysis`.
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
are rejected, not universally zero-imputed. Constant features are rejected.
A supplied one-to-one feature map identifies pairs; no automatic biological
mapping is inferred. `np.corrcoef` computes a descriptive Pearson correlation
across matched samples for each mapped pair. There are no inferential p-values,
prediction scores or claims of causal regulation.

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
| RNA-seq | NOT_REVIEWED | | | | | |
| Metabolic modeling | NOT_REVIEWED | | | | | |
| Multi-omics | NOT_REVIEWED | | | | | |

- [ ] Reproduced commands and inspected actual artifacts, warnings and failures.
- [ ] Challenged biological units, identity, contrasts, confounding and leakage.
- [ ] Reviewed normalization, multiplicity, model assumptions and numerical tolerances.
- [ ] Independently assessed interpretation and the boundary of each supported claim.
- [ ] Recorded qualifications relevant to the review, scope and actual independence.
- [ ] Recorded discrepancies and unresolved issues; no automatic promotion to validated.

Human methodological review and independent biological validation remain
incomplete. See [scientific evidence](scientific-evidence.md) and
[development transparency](development-and-ai-assistance.md).
