# Executed by the pinned Bioconductor CI job. All inputs below are synthetic.
dir.create("artifacts/rnaseq-ci", recursive = TRUE, showWarnings = FALSE)
base <- "artifacts/rnaseq-ci"
set.seed(731)
n <- 12L
counts <- matrix(rnbinom(600L * n, mu = 150, size = 12), nrow = 600)
counts[1:50, 7:12] <- counts[1:50, 7:12] * 4L
tab <- data.frame(gene_id = paste0("synthetic_gene_", seq_len(nrow(counts))), counts)
names(tab)[-1] <- paste0("sample_", seq_len(n))
md <- data.frame(sample_id = names(tab)[-1], subject_id = paste0("donor_", seq_len(n)),
    condition = rep(c("control", "treated"), each = 6), batch = rep(c("a", "b"), 6))
cfg <- list(organism = "synthetic", reference = "synthetic-v1", count_generation = "rnbinom seed731",
    measurement_type = "raw_counts", design = "unpaired", reference_level = "control", treatment_level = "treated")
run <- function(method, label, m = md, x = tab, config = cfg, expected = 0L) {
    folder <- file.path(base, paste(method, label, sep = "-"))
    dir.create(folder)
    write.table(x, file.path(folder, "counts.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(m, file.path(folder, "samples.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    jsonlite::write_json(config, file.path(folder, "config.json"), auto_unbox = TRUE)
    code <- system2(file.path(R.home("bin"), "Rscript"), c("recipes/rnaseq/run.R", method,
        file.path(folder, "counts.tsv"), file.path(folder, "samples.tsv"), file.path(folder, "config.json"),
        file.path(folder, "output")), stdout = file.path(folder, "stdout.log"), stderr = file.path(folder, "stderr.log"))
    stopifnot(code == expected)
    status <- jsonlite::fromJSON(file.path(folder, "output/analysis-status.json"))
    if (expected == 0L) {
        stopifnot(status$analysis_status == "EXECUTED", status$retained_genes > 100, status$residual_df > 0)
        result <- read.delim(file.path(folder, "output/results.tsv"))
        p <- if (method == "deseq2") result$pvalue else result$PValue
        adj <- if (method == "deseq2") result$padj else result$FDR
        effect <- if (method == "deseq2") result$log2FoldChange else result$logFC
        stopifnot(any(is.finite(p)), all(adj[!is.na(adj)] >= 0), all(adj[!is.na(adj)] <= 1))
        stopifnot(median(effect[1:50]) > 1, file.info(file.path(folder, "output/dispersion.pdf"))$size > 0)
    } else stopifnot(status$analysis_status == "NOT_RUN", status$status == "FAIL")
}
for (method in c("deseq2", "edger")) {
    run(method, "unpaired")
    paired <- md
    paired$subject_id <- rep(paste0("donor_", 1:6), 2)
    config <- cfg
    config$design <- "paired"
    run(method, "paired", paired, config = config)
    config$design <- "batch"
    run(method, "batch", config = config)
    run(method, "permuted", md[12:1, ], expected = 1L)
    bad <- cfg
    bad$measurement_type <- "TPM"
    run(method, "tpm", config = bad, expected = 1L)
    dup <- md
    dup$sample_id[2] <- dup$sample_id[1]
    run(method, "duplicate", dup, expected = 1L)
    confounded <- md
    confounded$batch <- confounded$condition
    run(method, "confounded", confounded, config = config, expected = 1L)
    unreplicated <- md
    unreplicated$subject_id <- unreplicated$condition
    run(method, "pseudoreplication", unreplicated, expected = 1L)
    bad <- cfg
    bad$count_generation <- NULL
    run(method, "missing-provenance", config = bad, expected = 1L)
}
jsonlite::write_json(list(tests = 18L, passed = 18L, failed = 0L, synthetic = TRUE),
    file.path(base, "test-summary.json"), auto_unbox = TRUE)
