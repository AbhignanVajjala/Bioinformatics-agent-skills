# Bulk RNA-seq maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Human-directed maintainer self-review with
ChatGPT-assisted adversarial testing, not independent external peer review or
unaided human implementation. This is a scoped investigation of bulk RNA-seq;
independent methodological and biological review remain incomplete.

## Supplied historical observations

Original source: `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2.
Codespaces environment: Python 3.12.3, R 4.4.3, Bioconductor 3.20, DESeq2 1.46.0,
edgeR 4.4.2, jsonlite 1.8.9, BiocManager 1.30.25. Original automated R tests:
18/18 passed. First adversarial batch: 22 passed, 18 failed expected behavior.
Second batch: 26 passed, 14 failed expected behavior, eight assessment-only cases.
The **32 failed checks are repeated manifestations across methods, not 32 distinct
defects**. The original directories were artifacts/my-manual-rnaseq-review,
artifacts/rnaseq-ci, artifacts/my-rnaseq-adversarial-JzEKGo and
artifacts/my-rnaseq-final-audit-AkPawk. Original Codespaces files are unavailable
here; no original hashes, timestamps or personal terminal observations are invented.

Both methods accepted whitespace-only organism/reference/count-generation,
null reference/count-generation, multiple-organism arrays, conflicting duplicate
JSON keys and string-valued align_samples. Numeric inference changed gene IDs
0001/0002/0003 into 1/2/3, rejected otherwise valid zero-prefixed samples,
collapsed conditions "01"/"1" and donors "0001"/"1". Both accepted an unlabelled
extra leading field in count/metadata TSVs through implicit row-name inference.

Python readiness observations: duplicate/contradictory subject_id columns raised
AttributeError; Boolean counts, mixed integer 1/string "1" identifiers and counts
beyond the supported R integer range were accepted. Finite 1e308 counts caused a
library-sum overflow warning yet returned PASS. Phase 6 subsequently closed the
shared overflow/mixed-matrix-label gaps; Phase 7 retains those corrections.

All three DESeq2 designs reported automatic parametric-to-local dispersion trend
substitution. This was legitimate native behavior, not failed fitting. The edgeR
report incorrectly carried a DESeq2-specific independent-filter/Cook limitation.
All-zero and low-count controls correctly retained 599 and 550 genes, with matching
filter/result identifiers and finite normalized values. DESeq2 rejected every-gene-
has-a-zero data because ratio size factors were undefined; edgeR analyzed it.
Both rejected post-filter zero-depth libraries; edgeR's "missing value where
TRUE/FALSE needed" reason was uninformative. Unpaired fits accepted an ignored,
perfectly confounded batch: valid unadjusted computation, not separable treatment
causality. These distinctions are preserved.

Original unpaired synthetic fixture: 600 genes, 12 samples, 50 planted fourfold
changes. Supplied results, preserved as history:

| Metric | DESeq2 | edgeR |
|---|---:|---:|
| True positives / false negatives | 50 / 0 | 50 / 0 |
| False positives / true negatives | 7 / 543 | 2 / 548 |
| Realized false discovery proportion | 0.12280701754385964 | 0.038461538461538464 |
| Median planted-gene log2FC | 1.88284382887523 | 1.8959364566524899 |

Cross-method effect Pearson r: 0.9999925099937185. All six unpaired, paired and
batch fits recovered 50 planted genes and passed BH comparisons without missing
adjusted values. DESeq2 false positives were 7,7,6; edgeR 2,2,2. DESeq2 Wald
statistic/p-value comparison passed. Both methods passed reversed contrasts in
all designs. Explicit sample realignment left unpaired results unchanged.
These observations are synthetic checks, not general calibration or biological
validation. One realized FDP above 5% does not establish incorrect FDR control.

## Source-inspected corrections and current contracts

Phase 7 starts from merged Phase 6 `19ae86864c6e331554f7ff66b9c17ea4b14610a7`.
Scientific methods, original 18-test assertions, Phase 5 metabolic gates, Phase 6
numerical checks and historical benchmark judgments are retained.

Configuration is one flat JSON object with seven required nonblank scalar strings,
enumerated measurement/design and optional Boolean align_samples. Grammar is
validated, then lexical object keys (including escaped aliases and nested keys)
are checked before object parsing. Unknown fields and unsupported structures
fail with a structured status before fitting. No provenance is inferred.

Strict UTF-8 TSV parsing checks every row's width, unique nonblank headers and
nonempty records without row-name or categorical type inference. Fields are exact
text, including leading zeros, long numbers, punctuation and literal "NA" IDs.
Only count fields undergo numeric conversion, with finite nonnegative integral
values <=2147483647. Totals must be positive/finite and <=2^53-1. The supported
format is plain tab-delimited records, without CSV quoting/multiline semantics;
NULs and malformed encodings/line endings reject. Inputs remain immutable.

Model-only factor codes avoid native name-sanitization collisions. Original
metadata is exported unchanged apart from explicitly authorized row alignment;
factor-code mappings and original contrast strings are recorded. This coding is
explicit and does not merge or rewrite original identities. Design exports have
an explicit sample_id column. Gene IDs persist across results, normalization,
filtering and dispersion outputs; sample IDs persist in normalized headers.
Condition coefficients are identified by the named formula term, never assumed
to occupy the last column. Reversed contrasts remain separately tested.

Post-filter library totals are checked before normalization. DESeq2 keeps ratio
size factors and native parametric fitting with automatic local fallback; no
alternative normalization is silently substituted. Requested/actual dispersion,
size factors, TMM factors/effective libraries, package messages and warnings are
recorded. Native diagnostics remain visible on stderr. Method-specific limitations
distinguish DESeq2 from edgeR. Ignored covariates and declared batch confounding
are disclosed without calling an unadjusted association a causal estimate.

Generic Python counts retain the Phase 6 <=2^53-1 scope; only bulk R readiness
imposes the per-cell R integer limit. Boolean counts and ambiguous mixed-type
identifiers reject. Duplicate metadata columns fail ScientificValidationError
before field access. Homogeneous numeric labels remain allowed in generic Python
APIs; file-based categorical identities are exact strings, and mixed numeric/text
labels fail before serialization can collapse them.

Successful export means EXECUTED and model_fit_status COMPLETE. Preflight/filter
rejections mean NOT_RUN/FAIL. A fitting or later failure means FAILED/FAIL, with
model status, stage, reason, diagnostics and any emitted artifacts. No partial
artifacts imply successful execution. Legitimate missing p/padj values remain NA;
BH is checked over the native adjustment family, with missingness counts and
DESeq2 filter metadata. Readiness PASS never implies a fitted model or biology.

Primary references: [R table import semantics](https://stat.ethz.ch/R-manual/R-patched/library/utils/html/read.table.html),
[DESeq2 documentation](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html),
[edgeR guide](https://bioconductor.org/packages/release/bioc/vignettes/edgeR/inst/doc/edgeRUsersGuide.pdf).
Installed pinned APIs, diagnostics and actual hosted tests govern this recipe;
current release documentation alone is not execution evidence for older versions.

## New execution evidence and limitations

An additional source-inspection finding concerns numeric text: a sub-ulp fraction
such as 1.00000000000000001, or 1e-9999, could round to an integer/zero during
floating conversion. Exact Decimal checks in Python and lexical decimal/exponent
integrality checks in R now reject these before a successful count gate. Valid
integral notation such as 1.0, 1e3 and 10e-1 remains supported. This is a new
inspection/regression finding, not an extra historical maintainer observation.

New Python and R regression drivers are separate from maintainer observations.
The original R driver remains 18 checks; the new driver records its actual count,
criterion-level reasons, new synthetic observations, source hashes and session
information in artifacts/rnaseq-phase7/test-summary.json. Tests cover configuration
types/duplicates, TSV structure, identity round trips, integer limits, BH/NA
semantics, Wald p-values, all three reversed contrasts, alignment, filtering,
normalization failure, covariate reporting and real native fit-failure statuses.

Local Python uses the existing 3.12.10 virtual environment, NumPy 2.2.6, pandas
2.2.3, pytest 8.3.5 and Ruff 0.11.13. Rscript is not installed on the local PATH;
native R validation is NOT_RUN locally and must pass in pinned hosted CI before
merge. See [implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md)
and the eventual PR for genuine counts, failures, warnings and evidence links.
No original Codespaces artifact is reconstructed and relabelled as historical.

Independent external methodological review, real-data/power assessment, genuine
assay/subject authentication, causal identification and biological/clinical
validation remain incomplete. No new agent sessions or effectiveness benchmark
are part of this correction.
