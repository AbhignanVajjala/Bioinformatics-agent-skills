# Bulk RNA-seq executable recipes

These commands require the full repository or the executable toolkit, R 4.4.3,
Bioconductor 3.20, DESeq2 1.46.0, edgeR 4.4.2 and jsonlite. The lightweight ZIP
contains these instructions and references. Scientific scripts are external
dependencies of that download.

| Input type | Question | Method | Software | Expected result | Failure conditions |
|---|---|---|---|---|---|
| FASTQ | Obtain gene counts | Assay-aware aligner/quantifier before DE | External established workflow | Count provenance and QC | Unknown strandedness/reference |
| BAM/CRAM | Obtain gene counts | Compatible counting/import workflow | External established workflow | Gene-by-library counts | CRAM reference unavailable |
| Raw counts, independent subjects | Condition association | DESeq2 or edgeR QL, chosen before outcomes | Pinned R/Bioconductor | Effects, p-values, BH FDR and diagnostics | Scale, identity, replication or rank fails |
| Raw counts, paired donors | Within-donor association | Subject blocking | Same R environment | Paired condition coefficient | Missing pairs or pseudoreplication |
| Transcript estimated counts | Gene-level inference | Supported tximport route, external to this implementation | tximport + DE package | Gene model with valid offsets | Blind rounding or mixed annotation |
| TPM/FPKM/log values | Descriptive exploration | Scale-aware visualization | User-selected tools | Descriptive summaries | Count-model DE request |

From the full repository root, explicitly install the environment as described
in `recipes/rnaseq/environment.json`, then run:

```text
Rscript recipes/rnaseq/test.R
Rscript recipes/rnaseq/run.R deseq2 counts.tsv samples.tsv config.json new-output
Rscript recipes/rnaseq/run.R edger counts.tsv samples.tsv config.json other-output
```

The first command generates synthetic valid unpaired, paired and batch designs
and negative controls, and invokes both real model fits. It needs an empty
`artifacts/rnaseq-ci` directory. Test execution status is recorded in development
documentation. A CI definition alone does not establish a successful run.

DESeq2 uses its native Wald contrast, independent filtering and Cook outlier
handling. Its `padj` is BH adjusted and may be NA for filtered or outlier genes.
The prefilter retains genes with at least ten counts in two libraries as an
explicit demonstration policy. edgeR uses `filterByExpr`, TMM, dispersion
estimation, `glmQLFit` and `glmQLFTest`. Both export the actual retained-gene
table, normalized values, design, dispersions, diagnostic PDF and session info.
Normalized counts support diagnostics. The test is fitted to the count model.
Optional shrinkage is NOT_RUN and must not be confused with testing.

Select DESeq2 for its negative-binomial modeling workflow and edgeR QL when its
filtering and QL inference suit the design. Both need independent replication,
identifiable covariates and expert diagnostic review. Never select the package
by comparing significance. Effect direction is treatment versus reference.
