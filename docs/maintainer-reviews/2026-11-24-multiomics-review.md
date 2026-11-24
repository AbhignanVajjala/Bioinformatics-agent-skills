# Multi-omics maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Review type: **human-directed maintainer self-review
with ChatGPT-assisted adversarial diagnostic scripts**. This is the second scoped
investigation in the maintainer's audit of 17 skills. It is neither independent
external peer review nor unaided human implementation. Other skills are not
certified by this record. Independent methodological review remains incomplete.

## Supplied maintainer observations (historical)

Source investigated: `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2.
Environment: GitHub Codespaces/Linux, Python 3.12.3, NumPy 2.2.6, pandas 2.2.3,
SciPy 1.15.3. The original Codespaces artifacts are unavailable in this local
checkout. No original file hashes, exact timestamps, signatures or artifact paths
beyond those supplied are asserted. The following are observations supplied by
the maintainer, not terminal observations personally made by Codex.

Both commands completed successfully:

```text
python examples/multiomics/run.py --output artifacts/my-manual-multiomics-review
python examples/domain-recipes/run.py multiomics --output artifacts/my-manual-crossview-review
```

| Pair | Original readiness Pearson r | Expanded cross-view Pearson r |
|---|---:|---:|
| gene_0/protein_0; gene0/protein0 | 0.9848268993122902 | -0.18037311612127607 |
| gene_1/protein_1; gene1/protein1 | 0.981022122879502 | 0.3734261770509437 |
| gene_2/protein_2; gene2/protein2 | 0.9813029694967363 | 0.41865422771703026 |
| gene_3/protein_3; gene3/protein3 | 0.9797640724175947 | -0.6020016995027743 |

Readiness QA: input integrity PASS, computation PASS, statistical methodology
WARN, biological interpretation NOT_RUN, provenance PASS. Readiness matches
seven specimens after its deliberate protein-only replacement; expanded matches
all eight. Expanded RNA uses log2(CPM+1), protein declared log2 intensity unchanged.
These are synthetic descriptive calculations, not biological findings.

| ID | Actual adversarial change | Supplied observed outcome | Source-inspected root cause and correction |
|---|---|---|---|
| MO-01 | Empty map with expected columns | `ACCEPTED: EXECUTED`, `Correlations: 0` | Vacuous checks; now require nonempty map and at least one completed pair |
| MO-02 | All timepoints whitespace | Accepted; original correlations | Null-only check; require nonblank categories or finite numeric values |
| MO-03 | RNA count_generation whitespace | Accepted; original correlations | Truthiness; require nonblank string |
| MO-04 | Remove protein specimen_id | `REJECTED: AttributeError`, `'DataFrame' object has no attribute 'specimen_id'` | Access before validation; validate all required columns first |
| MO-05 | RNA namespace whitespace | Accepted; original correlations | Truthiness; require nonblank string for both assays |
| MO-06 | RNA reference whitespace | Accepted; original correlations | Truthiness; require nonblank string for both assays |
| MO-07 | Duplicate protein subject_id column | `ACCEPTED: EXECUTED`; four original correlations | No column uniqueness gate; reject duplicates including contradictory values |
| MO-08 | protein0 = alternating ±1e308, eight values | Overflow/invalid warnings, accepted; pair reported 0.0 | Unscaled std/corrcoef; exact power-of-two scaling and controlled arithmetic |

Actual supplied warning evidence for MO-08:

```text
RuntimeWarning: overflow encountered in multiply
RuntimeWarning: invalid value encountered in divide
ACCEPTED: EXECUTED
```

All final values were finite, so a final-only finiteness check did not identify
the unreliable computation. The maintainer had not independently established
the correct modified-pair value; the mathematical reference below is new work.

MO-09 limitation: a constant mapped protein was correctly rejected. A separate
constant `unused_protein`, absent from the map, also rejected the whole analysis.
The new path tests variability only for mapped pairs while preserving whole-matrix
integrity and the entire RNA normalization universe.

Three methodological considerations, not all mathematical defects:

1. Eight specimens assigned to one subject/all train produced unchanged values.
   Within-subject description is allowed; independence/generalization is not.
2. All specimens assigned test produced unchanged values. No prediction model
   was fit; all partitions now have explicit descriptive semantics and counts.
3. Removing gene3 and its pair changed denominators and retained-pair results:

| Pair | Original | Reduced count matrix |
|---|---:|---:|
| gene0/protein0 | -0.18037311612127607 | -0.3421912257504099 |
| gene1/protein1 | 0.3734261770509437 | 0.10396169207738355 |
| gene2/protein2 | 0.41865422771703026 | 0.3046667638816443 |

This is expected CPM denominator sensitivity, not itself a numerical defect.
The new contract requires a declared complete intended matrix and scope; exact
sample-wise sums and source are reported. Changing only the map cannot change
normalization. External denominators and preselected subsets remain unsupported.
Metadata cannot establish that a declared universe is biologically appropriate.

Maintainer-observed correct safeguards: valid four-pair baseline; identical
results after correctly reordering matrix and corresponding metadata; controlled
rejection of conflicting subjects, cross-partition subjects, conflicting
timepoints, negative/fractional counts, zero libraries, missing expression,
duplicate pairs and constant mapped proteins. These observations are preserved.

## New implementation and mathematical checks

Phase 6 starts from merged Phase 5 `d8119c5167b98e92a6929596dc294b2acc49e893`.
The public `domain_workflows.cross_view_analysis` entry point is preserved through
an import of `omics.cross_view_analysis`. Shared matrix/reconciliation gates also
serve readiness, count/design validators and pseudobulk dependencies; regression
checks cover those callers. Seven public validator interfaces remain unchanged.
No metabolic implementation, historical benchmark verdict or prompt is revised.

Both multi-omics examples now use `stable_pearson`: exact power-of-two scaling,
shifted compensated mean, centered rescaling, unit norms and compensated dot sum.
Mapped constants and maximum centered scaled variation <=64 binary64 epsilon
are rejected. This conservative threshold avoids cancellation-sensitive inputs;
it is not a universal error bound or biological threshold. Returned r must be
finite and within [-1,1], allowing clipping only within 16 epsilon roundoff.
Scoped RuntimeWarnings/overflow/underflow/invalid/division errors stop computation
with stage/category/message evidence attached to ScientificValidationError.
Global NumPy error state and warning filters are restored, including on failure.
Empty maps and undefined pairs never return partial EXECUTED success.

The independent computational reference uses Python Decimal at 100 digits,
exact conversion of binary64 observations, safe scaling, centered covariance
and decimal square roots. It shares no production Pearson routine. On the
expanded gene0/alternating-±1e308 fixture, reference r is approximately
**0.1125037320033151**, rather than zero; production gives
**0.11250373200331505** in the local run. This is an independent algorithmic check,
not independent human methodological review. The production test requires
agreement within 2e-15 absolute for these fixtures after exact scaling; known
positive, negative and orthogonal examples independently fix +1, -1 and 0.
Very small nonzero values are supported when scaling remains representable;
dynamic ranges causing arithmetic underflow are rejected. Counts/totals over
2^53-1 are outside the exact-integer binary64 normalization scope and rejected
before summation in floating point. Integer sums use Python integers.

Additional source-inspected gaps closed with new tests: the shared count gate
also used unchecked floating sums, and complex-valued matrices could lose their
imaginary component during a float cast. Shared exact totals and explicit
real-valued input validation now reject these cases. These are newly identified
code findings, not extra historical maintainer observations.

Numerical design references: [NumPy scoped errstate](https://numpy.org/doc/2.2/reference/generated/numpy.errstate.html)
and [SciPy 1.15.3 Pearson warnings](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.pearsonr.html).
These inform the audit; this baseline computes descriptive r only, not SciPy
inferential p-values. CPM remains susceptible to composition and supplied-universe
choices; no advanced normalization or MOFA2/SNF method has been introduced.

## New Codex-executed validation and remaining review

Local Windows validation uses Python 3.12.10 in the existing virtual environment,
NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3, pytest 8.3.5 and Ruff 0.11.13.
Both original and expanded example commands executed in new Phase 6 output
directories, preserving original evidence. Their analysis_run.json records actual
input/output hashes and versions. New targeted regressions and full validation
results are recorded in [implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md).
Hosted CI retains machine-readable JUnit, example/provenance output, deterministic
evaluation and separate Windows/Linux installation evidence. Development-only
tests/evaluation reports are intentionally outside the universal ZIP.

New tests cover malformed/duplicate columns, blank declarations, key/type errors,
empty/unknown/ambiguous maps, numerical extremes, state restoration, repeated
subjects, test-only partitions, denominator invariance, immutability and preserved
identity/leakage gates. These additional adversarial tests are new automated
checks, not retrospectively claimed maintainer terminal observations.

Independent external methodological review, real-data validation, biological
identity authentication, power/generalization assessment and clinical validation
remain incomplete. Multiple specimens are not independent subjects. Correlation
establishes neither causality nor predictive performance. No additional model
sessions or agent-effectiveness benchmark was run for this correction.
