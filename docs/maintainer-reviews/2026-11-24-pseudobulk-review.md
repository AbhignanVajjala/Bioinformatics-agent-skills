# Single-cell pseudobulk maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Human-directed maintainer self-review with
ChatGPT-assisted scripts in Codespaces, not independent external peer review.
Independent methodological and biological validation remain incomplete.

## Supplied historical evidence

Source `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2, November 24,
2026. Environment: Python 3.12.3, NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3.
Original directories: `artifacts/my-combined-domain-audit-qAgil0` and
`artifacts/my-final-domain-audit-9j6Ml3`. Original files are unavailable here;
no original hashes or execution records are reconstructed. The supplied first
batch was 51 checks (26 PASS/16 INVESTIGATE/9 ASSESS); the second was 49
(18/19/12). Combined **100: 44 PASS/35 INVESTIGATE/21 ASSESS** across four
skills, not per-skill totals, accuracy rates or distinct defect counts.
Assessment-only cases also exposed confirmed numerical defects.

The original 20-gene/16-cell control produced exact 20-by-4 sums. Four cells
with g0=2^62 should sum to **18446744073709551616**, but pandas returned **0**
without warning and still reported READY_FOR_DESIGN_REVIEW. This is observed
integer wraparound. The separate **2^53+1** integer fixture aggregated exactly;
it was not an observed failure. Float conversion before integer checking remains
an integrity risk and is excluded from exact-source validation.

Duplicate subject_id columns raised AttributeError; Boolean counts, paired="false"
and mixed specimen integer 1/string "1" were accepted. Perfect batch-condition
confounding was called ready, and unpaired structural absence was reported as
four missing donor-condition combinations. These are scientific input/reporting
defects, not evidence that pseudobulk statistics were executed.

Correct preserved behavior: conflicting specimen identities/timepoints,
misalignment, blank populations and negative counts reject; reordered input
preserves sums; complete paired observations pass, incomplete pairing/insufficient
donors/absent populations block inference; two populations yield 20-by-8 exact
counts; inputs remain immutable.

## Correction and regression evidence

[Checked aggregation](../../src/bioskills/aggregation.py) uses exact source
integers and Python sums before int64 conversion; validates source and aggregate
libraries, gene aggregates and exact conservation; exposes decimal-string totals.
Unsupported aggregates fail before export. Generic int64 limits and downstream
R int32/count and 2^53-1/library limits are separate gates.

| Criterion | New evidence / acceptance condition |
|---|---|
| Overflow | Four 2^62 cells reject with aggregate_range; no wrapped matrix |
| Exact integers | 2^53+1 remains exact; fractional/nonfinite/Boolean/unsafe floats reject |
| Metadata | Duplicate fields, serialization collisions and non-Boolean paired reject |
| Design | Batch confounding, donor deficiency and incomplete pairs have per-population reasons |
| Identity/conservation | Reordering and two-population sums exact; inputs immutable |
| Integration | Exported exact counts/IDs pass bulk input and format gates; native R import runs separately |

Automated cases are in tests/test_pseudobulk_integrity.py and
tests/test_domain_integration.py; commands and actual counts are in
[implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md). Aggregation EXECUTED is
separate from design readiness; differential state remains **NOT_RUN**. Upstream
QC, power, true donor identity and real-data calibration remain unverified.

Primary method reference: [muscat vignette](https://bioconductor.org/packages/release/bioc/vignettes/muscat/inst/doc/analysis.html)
(previously consulted); no execution of muscat is claimed.
