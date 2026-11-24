---
name: bulk-rnaseq-differential-expression
description: "Guide and audit gene-level bulk RNA-seq differential expression with validated counts, sample identities and biological replication; use for count-based comparisons, not per-cell tests, TPM/FPKM as counts, microarrays or clinical conclusions."
metadata:
  maturity: experimental
---

# Bulk RNA-seq differential expression

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Required inputs and preflight
Require organism/taxonomy, tissue/material, count-generation method, gene/reference annotation version, gene-by-sample matrix, sample-to-subject metadata, biological conditions, covariates/batches, independent replicate structure and intended contrast. Preserve raw inputs and pseudonymize identifiers before logs. Check local storage and R/Bioconductor availability before promising DE; the bundled Python demonstration performs readiness/QC, not DESeq2.

## Method selection
In QUICK and FULL, validate required scalar declarations and optional parameter
types, reject duplicate configuration keys/metadata columns, and preserve all
categorical identifiers exactly. Numeric-looking IDs are text, not quantities.
Reject Boolean counts and malformed table widths before fitting. Generic count
integrity and readiness for R's per-count integer limit are different scopes.

- FASTQ needs an upstream alignment/quantification workflow with library strandedness, QC and a compatible reference. BAM/CRAM alone is not a gene count matrix; CRAM also needs its reference.
- Raw nonnegative integer gene counts with known provenance support DESeq2 or edgeR; limma-voom models the mean–variance relationship of log-counts with appropriate precision weights. Select and justify one established workflow rather than testing all for the smallest p-values.
- Transcript estimated counts require a supported import/aggregation route such as tximport with matching transcript-to-gene annotation; do not blindly round or treat length-corrected values as raw counts.
- TPM, FPKM, VST/rlog/log expression and microarrays are different input classes. Do not convert them to raw counts by rounding or use count-model assumptions without a justified reconstruction. Single-cell data require donor-aware analysis and separate QC.

## Procedure
1. Verify unique gene/sample identifiers, dimensions, finite nonnegative count values and library totals. Integer appearance alone does not establish raw-count provenance. Reject missing/duplicated samples; require exact correspondence and explicitly reorder by verified ID only after reporting mismatch. Never align by row position.
2. Count independent biological units per condition. Technical replicates cannot supply population-level replication. Retain donor pairing/repeated measures in the design; explain why too few independent units limits inference instead of treating genes as replicates.
3. Write the design formula and contrast before fitting. Check design rank, condition-by-batch cross-tabulation, residual degrees of freedom and meaningful covariate support. Perfect condition/batch confounding blocks separate treatment estimation; batch correction cannot create missing information.
4. Define low-expression filtering independently of treatment outcomes and preserve the tested-gene universe. Inspect library composition and choose method-supported normalization (e.g. size factors or TMM); examine whether global shifts undermine assumptions. Do not feed normalized values back as raw counts.
5. Fit with the chosen versioned Bioconductor workflow. Record reference group, coefficient/contrast, offsets and exclusions. Extract effect sizes, uncertainty where supported, raw p-values and adjusted p-values; report the FDR procedure and testing family. Label shrinkage method and distinguish shrunken effect estimates from test statistics.
6. Review sample-distance/PCA plots using suitable transformed data, dispersion/mean–variance diagnostics, outlier handling and model fit. A PCA separation is descriptive and does not establish a treatment effect. Diagnose anomalous samples without automatically deleting them.
7. For enrichment, map identifiers with version/ambiguity accounting. ORA uses eligible tested genes with compatible annotations as background, not every genome gene. Ranked enrichment needs a justified full ranking and versioned gene sets. Correct multiple pathway tests and avoid interpreting enrichment as pathway activation or mechanism by itself.
8. Save a methods report, result table, QC figures, design/contrast, exclusions, hashes, software versions and claim ledger. Review exploratory vs confirmatory status and biological context before reporting.

## Executable readiness demonstration
From the repository root after installing example dependencies:

```bash
python examples/bulk-rnaseq/run.py --output artifacts/bulk-rnaseq
```

Inspect the generated report and numerical outputs. This command is a synthetic QC/design demonstration, not full differential-expression analysis. Full R analysis is NOT_RUN unless separately executed with its own evidence.

## Validation, stops and outputs
Record post-filter library totals, requested and actual dispersion fitting,
normalization factors, native warnings/messages, tested/adjusted families and
legitimate missing p-values. Automatic DESeq2 parametric-to-local fallback is
native behavior to report, not a reason to suppress diagnostics. Undefined ratio
size factors or post-filter zero libraries stop this recipe without silently
substituting normalization. Disclose ignored covariates and known confounding;
an unadjusted condition association is not a treatment-specific causal effect.

Block count-based inference for unsuitable input scale, unresolved sample mismatch, rank deficiency, absent independent replication or unknown essential provenance. Output `count-qc`, a sample/design audit, method-selection decision, executed-run evidence and claim limitations. A finished DE analysis additionally needs actual model diagnostics and effect/FDR tables; a readiness PASS alone cannot satisfy it.

## Examples, evaluation and definition of done
Positive: six independently sampled bulk libraries, three per condition, balanced batches and verified gene counts; audit design then run a justified count model. Negative: TPM labeled “counts,” a permuted sample sheet, or all treated samples in one sequencing batch. The negative cases must fail readiness before fitting. Done means gates were executed, the contrast is estimable, output provenance is available and claim strength matches the executed scope.

Read [method notes](references/methods.md) for authoritative source targets and qualifications.
For optional full-repository R execution, read [recipes](references/recipes.md),
the [input contract](references/input-contract.md) and
[troubleshooting](references/troubleshooting.md). Consult the development status
for actual pinned DESeq2 and edgeR execution evidence.
