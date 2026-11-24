# New Phase 7 checks; the original 18-case test.R remains separately executed.
source("recipes/rnaseq/validation.R")
base <- "artifacts/rnaseq-phase7"
if (dir.exists(base) && length(list.files(base, all.files = TRUE, no.. = TRUE))) stop("Choose an empty Phase 7 evidence directory")
dir.create(base, recursive = TRUE, showWarnings = FALSE)
checks <- list()
check <- function(name, expr) {
    error <- tryCatch({ force(expr); NULL }, error = function(e) conditionMessage(e))
    checks[[length(checks) + 1L]] <<- list(name = name, status = if (is.null(error)) "PASS" else "FAIL", reason = error)
}
reject <- function(expr, pattern = ".") {
    error <- tryCatch({ force(expr); NULL }, error = function(e) conditionMessage(e))
    stopifnot(!is.null(error), grepl(pattern, error))
}
cfg <- jsonlite::fromJSON("artifacts/rnaseq-ci/deseq2-unpaired/config.json", simplifyVector = FALSE)
config_path <- file.path(base, "configuration.json")
required <- names(cfg)
for (field in required) for (kind in c("missing", "null", "blank", "empty", "number", "boolean", "array", "object")) {
    check(paste("configuration", field, kind), {
        bad <- cfg
        value <- switch(kind, null = NULL, blank = " \t", empty = "", number = 1,
            boolean = TRUE, array = c("a", "b"), object = list(value = "x"), missing = NULL)
        if (kind == "missing") bad[[field]] <- NULL else bad[field] <- list(value)
        jsonlite::write_json(bad, config_path, auto_unbox = TRUE, null = "null")
        reject(read_config(config_path))
    })
}
for (value in list("true", 1, NULL, c(TRUE, FALSE), list(value = TRUE))) check("invalid-align-samples", {
    bad <- cfg
    bad["align_samples"] <- list(value)
    jsonlite::write_json(bad, config_path, auto_unbox = TRUE, null = "null")
    reject(read_config(config_path), "align_samples")
})
for (text in c("[]", "null", "1", "{broken", r"({"organism":"a","organism":"b"})",
    r"({"organism":"a","organ\u0069sm":"b"})", r"({"x":[{"a":1,"a":2}]})")) check("JSON-structure-or-duplicate", {
    writeLines(text, config_path)
    reject(read_config(config_path))
})
check("valid-Boolean-option", {
    good <- cfg
    good$align_samples <- TRUE
    jsonlite::write_json(good, config_path, auto_unbox = TRUE)
    stopifnot(isTRUE(read_config(config_path)$align_samples))
})
tsv <- file.path(base, "strict.tsv")
for (text in c("gene_id\ta\tb\ng\t1\t2\textra", "gene_id\ta\tb\nx\tg\t1\t2",
    "gene_id\ta\tb\ng\t1", "gene_id\ta\tb\ng\t1\t2\t", "gene_id\ta\ta\ng\t1\t2",
    "gene_id\ta\t\ng\t1\t2", "gene_id\ta\tb\n\ng\t1\t2")) check("strict-TSV-rejection", {
    writeLines(text, tsv)
    reject(read_tsv_exact(tsv))
})
check("exact-TSV-identities", {
    writeLines("gene_id\t0001\t1\n0001\t10\t20\n1\t30\t40", tsv)
    parsed <- read_tsv_exact(tsv)
    stopifnot(identical(parsed[[1]], c("0001", "1")), identical(names(parsed)[-1], c("0001", "1")))
    stopifnot(identical(rownames(count_matrix(parsed)), c("0001", "1")))
})
for (token in c("TRUE", "FALSE", "1.5", "1.00000000000000001", "1e-9999", "-1", "NaN", "Inf", "2147483648", "1e308", "")) check("invalid-count-token", {
    writeLines(paste0("gene_id\ta\tb\ng\t", token, "\t20"), tsv)
    reject(count_matrix(read_tsv_exact(tsv)))
})
check("exact-decimal-and-exponent-integers", {
    writeLines("gene_id\ta\tb\ng\t1e3\t10e-1\nh\t1.0\t1.00", tsv)
    stopifnot(identical(unname(count_matrix(read_tsv_exact(tsv))), matrix(c(1000, 1, 1, 1), nrow = 2)))
})
check("R-count-boundary-and-library-sum", {
    writeLines("gene_id\ta\tb\ng\t2147483647\t20\nh\t2147483647\t30", tsv)
    stopifnot(library_totals(count_matrix(read_tsv_exact(tsv)), "input")$a == 4294967294)
})
check("BH-with-native-missing-and-filtered-values", {
    stopifnot(bh_audit(c(.01, .04, NA, .9), c(.02, .04, NA, NA))$missing_adjusted == 2)
    reject(bh_audit(c(.01, .04), c(.01, .04)), "BH")
    reject(bh_audit(c(NA, NA), c(NA, NA)), "unavailable")
    stopifnot(bh_audit(c(.1, .2), c(NA, NA))$status == "NOT_RUN")
})

number <- function(value) { value[value == "NA"] <- NA_character_; as.numeric(value) }
read_result <- function(folder) read_tsv_exact(file.path(folder, "results.tsv"))
fit_case <- function(method, label, x, md, config, expected = 0L, reason = NULL, mutate_inputs = NULL) {
    folder <- file.path(base, paste(method, label, sep = "-"))
    dir.create(folder)
    write.table(x, file.path(folder, "counts.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(md, file.path(folder, "samples.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    path <- file.path(folder, "config.json")
    if (is.character(config)) writeLines(config, path) else jsonlite::write_json(config, path, auto_unbox = TRUE, null = "null")
    files <- file.path(folder, c("counts.tsv", "samples.tsv", "config.json"))
    if (!is.null(mutate_inputs)) mutate_inputs(files)
    hashes <- tools::md5sum(files)
    code <- system2(file.path(R.home("bin"), "Rscript"), shQuote(c("recipes/rnaseq/run.R", method,
        files, file.path(folder, "output"))), stdout = file.path(folder, "stdout.log"), stderr = file.path(folder, "stderr.log"))
    if (code != expected) stop(paste("Unexpected exit", code,
        paste(readLines(file.path(folder, "stderr.log"), warn = FALSE), collapse = "\n")))
    stopifnot(identical(hashes, tools::md5sum(files)))
    status <- jsonlite::fromJSON(file.path(folder, "output", "analysis-status.json"))
    if (expected == 0L) stopifnot(status$analysis_status == "EXECUTED", status$model_fit_status == "COMPLETE")
    else {
        stopifnot(status$status == "FAIL", status$analysis_status != "EXECUTED")
        if (!is.null(reason)) stopifnot(grepl(reason, status$reason))
    }
    list(status = status, output = file.path(folder, "output"))
}
observations <- list()
for (method in c("deseq2", "edger")) {
    original <- file.path("artifacts/rnaseq-ci", paste0(method, "-unpaired"))
    tab <- read_tsv_exact(file.path(original, "counts.tsv"))
    md <- read_tsv_exact(file.path(original, "samples.tsv"))
    for (design in c("unpaired", "paired", "batch")) check(paste(method, design, "statistics-and-reversal"), {
        baseline <- file.path("artifacts/rnaseq-ci", paste(method, design, sep = "-"))
        forward <- read_result(file.path(baseline, "output"))
        p <- number(forward[[if (method == "deseq2") "pvalue" else "PValue"]])
        adj <- number(forward[[if (method == "deseq2") "padj" else "FDR"]])
        effect <- number(forward[[if (method == "deseq2") "log2FoldChange" else "logFC"]])
        stopifnot(bh_audit(p, adj)$status == "PASS", sum(adj[1:50] < .05, na.rm = TRUE) == 50)
        if (method == "deseq2") {
            wald <- 2 * pnorm(abs(number(forward$stat)), lower.tail = FALSE)
            stopifnot(max(abs(wald - p), na.rm = TRUE) < 1e-12)
        }
        observations[[paste(method, design, sep = "-")]] <- list(true_positives = sum(adj[1:50] < .05, na.rm = TRUE),
            false_positives = sum(adj[-(1:50)] < .05, na.rm = TRUE), median_planted_log2FC = median(effect[1:50]))
        config <- jsonlite::fromJSON(file.path(baseline, "config.json"), simplifyVector = FALSE)
        config$reference_level <- "treated"
        config$treatment_level <- "control"
        matched_md <- read_tsv_exact(file.path(baseline, "samples.tsv"))
        reversed <- fit_case(method, paste0("reverse-", design), tab, matched_md, config)
        reverse <- read_result(reversed$output)
        stopifnot(identical(forward[[1]], reverse[[1]]))
        reverse_effect <- number(reverse[[if (method == "deseq2") "log2FoldChange" else "logFC"]])
        observations[[paste(method, design, sep = "-")]]$max_reversal_log2FC_error <- max(abs(effect + reverse_effect))
        observations[[paste(method, design, sep = "-")]]$max_reversal_p_error <- max(abs(p - number(reverse[[if (method == "deseq2") "pvalue" else "PValue"]])), na.rm = TRUE)
        stopifnot(max(abs(effect + reverse_effect)) < 1e-6)
        stopifnot(max(abs(p - number(reverse[[if (method == "deseq2") "pvalue" else "PValue"]])), na.rm = TRUE) < 1e-6)
    })
    check(paste(method, "identity-roundtrip"), {
        x <- tab
        x[[1]][1:7] <- c("0001", "1", "0002", "0003", "123456789012345678901234567890", "gene.A-B_1", "NA")
        sample_ids <- c("0001", "1", "0002", "02", "2", "NA", "s-A", "s.A", "s_0", "123456789012345678901", "s11", "s12")
        names(x)[-1] <- sample_ids
        metadata <- md
        metadata$sample_id <- sample_ids
        metadata$subject_id <- sample_ids
        metadata$condition <- rep(c("01", "1"), each = 6)
        metadata$batch <- rep(c("01", "1"), 6)
        metadata$other_id <- paste0("000", seq_len(nrow(metadata)))
        config <- cfg
        config$reference_level <- "01"
        config$treatment_level <- "1"
        run <- fit_case(method, "identity", x, metadata, config)
        for (name in c("results.tsv", "normalized.tsv", "dispersion.tsv", "filtering.tsv")) {
            exported <- read_tsv_exact(file.path(run$output, name))
            stopifnot(identical(exported[[1]], x[[1]]))
        }
        stopifnot(identical(names(read_tsv_exact(file.path(run$output, "normalized.tsv")))[-1], sample_ids))
        stopifnot(identical(read_tsv_exact(file.path(run$output, "design.tsv"))$sample_id, sample_ids))
        stopifnot(identical(read_tsv_exact(file.path(run$output, "metadata.tsv")), metadata))
        stopifnot(identical(run$status$contrast, c("1", "01")))
        config$design <- "batch"
        batch_run <- fit_case(method, "identity-batch", x, metadata, config)
        stopifnot(identical(read_tsv_exact(file.path(batch_run$output, "metadata.tsv")), metadata))
    })
    check(paste(method, "native-name-collisions"), {
        metadata <- md; metadata$condition <- rep(c("A-B", "A.B"), each = 6)
        config <- cfg; config$reference_level <- "A-B"; config$treatment_level <- "A.B"
        run <- fit_case(method, "name-collision", tab, metadata, config)
        stopifnot(identical(run$status$contrast, c("A.B", "A-B")),
            identical(read_tsv_exact(file.path(run$output, "metadata.tsv"))$condition, metadata$condition))
    })
    check(paste(method, "paired-leading-zero-donors"), {
        metadata <- md
        metadata$subject_id <- rep(c("0001", "1", "01", "s4", "s5", "123456789012345678901"), 2)
        config <- cfg; config$design <- "paired"
        run <- fit_case(method, "paired-identity", tab, metadata, config)
        stopifnot(identical(read_tsv_exact(file.path(run$output, "metadata.tsv"))$subject_id, metadata$subject_id))
    })
    for (file_index in 1:2) check(paste(method, "unlabelled-leading-field", file_index), {
        run <- fit_case(method, paste0("ragged-", file_index), tab, md, cfg, expected = 1L,
            reason = "field count", mutate_inputs = function(files) {
                lines <- readLines(files[file_index])
                lines[-1] <- paste0("unlabelled\t", lines[-1])
                writeLines(lines, files[file_index])
            })
        stopifnot(run$status$analysis_status == "NOT_RUN")
    })
    check(paste(method, "explicit-realignment"), {
        config <- cfg; config$align_samples <- TRUE
        run <- fit_case(method, "realigned", tab, md[12:1, ], config)
        stopifnot(isTRUE(run$status$aligned_metadata), identical(read_result(run$output), read_result(file.path(original, "output"))))
    })
    for (label in c("all-zero", "low-count")) check(paste(method, label, "filtering"), {
        x <- tab
        n <- if (label == "all-zero") 1L else 50L
        x[seq_len(n), -1] <- if (label == "all-zero") "0" else "1"
        run <- fit_case(method, label, x, md, cfg)
        stopifnot(run$status$retained_genes == 600L - n)
        kept <- read_tsv_exact(file.path(run$output, "filtering.tsv"))
        result <- read_result(run$output)
        stopifnot(identical(result[[1]], kept[[1]][kept$retained == "TRUE"]))
    })
    check(paste(method, "postfilter-zero-library"), {
        x <- tab; x[, 2] <- "0"; x[600, -1] <- "0"; x[600, 2] <- "1"
        run <- fit_case(method, "postfilter-zero", x, md, cfg, expected = 1L, reason = "Post-filtering")
        stopifnot(run$status$analysis_status == "NOT_RUN")
    })
    check(paste(method, "every-gene-has-zero"), {
        x <- tab
        for (i in seq_len(nrow(x))) x[i, 2 + (i %% 12)] <- "0"
        run <- fit_case(method, "geometric-zero", x, md, cfg,
            expected = if (method == "deseq2") 1L else 0L,
            reason = if (method == "deseq2") "ratio size factors" else NULL)
        if (method == "deseq2") stopifnot(run$status$analysis_status == "NOT_RUN")
    })
    check(paste(method, "ignored-confounded-batch"), {
        metadata <- md; metadata$batch <- metadata$condition
        run <- fit_case(method, "ignored-batch", tab, metadata, cfg)
        stopifnot("batch" %in% run$status$design_audit$ignored_covariates,
            any(grepl("confounded", run$status$design_audit$risks)))
    })
    check(paste(method, "malformed-CLI-configuration"), {
        fit_case(method, "duplicate-config", tab, md, r"({"organism":"a","organism":"b"})",
            expected = 1L, reason = "Duplicate JSON")
    })
    check(paste(method, "actual-fit-diagnostics"), {
        status <- jsonlite::fromJSON(file.path(original, "output", "analysis-status.json"))
        stopifnot(nzchar(status$dispersion_fit$requested), nzchar(status$dispersion_fit$actual),
            is.list(status$diagnostics), status$adjustment_audit$status == "PASS")
        if (method == "edger") stopifnot(!any(grepl("Cook", status$limitations)))
        else stopifnot(status$dispersion_fit$actual %in% c("parametric", "local", "mean"), length(status$diagnostics) > 0)
    })
}
check("DESeq2-native-fit-failure-status", {
    x <- read_tsv_exact("artifacts/rnaseq-ci/deseq2-unpaired/counts.tsv")
    x[, -1] <- "100"
    md <- read_tsv_exact("artifacts/rnaseq-ci/deseq2-unpaired/samples.tsv")
    run <- fit_case("deseq2", "constant-fit-failure", x, md, cfg, expected = 1L)
    stopifnot(run$status$analysis_status == "FAILED", run$status$model_fit_status == "FAILED")
})
check("DESeq2-native-missing-p-values", {
    x <- read_tsv_exact("artifacts/rnaseq-ci/deseq2-unpaired/counts.tsv")
    x[600, 2] <- "100000000"
    md <- read_tsv_exact("artifacts/rnaseq-ci/deseq2-unpaired/samples.tsv")
    run <- fit_case("deseq2", "native-missing", x, md, cfg)
    result <- read_result(run$output)
    stopifnot(any(is.na(number(result$pvalue))), run$status$adjustment_audit$missing_p_values > 0,
        run$status$adjustment_audit$status == "PASS")
})
summary <- list(tests = length(checks), passed = sum(vapply(checks, function(x) x$status == "PASS", logical(1))),
    failed = sum(vapply(checks, function(x) x$status == "FAIL", logical(1))), checks = checks,
    new_synthetic_observations = observations, software = capture.output(sessionInfo()),
    source_md5 = as.list(tools::md5sum(c("recipes/rnaseq/run.R", "recipes/rnaseq/validation.R", "recipes/rnaseq/test-validation.R"))))
jsonlite::write_json(summary, file.path(base, "test-summary.json"), auto_unbox = TRUE, pretty = TRUE, null = "null", digits = NA)
print(c(tests = summary$tests, passed = summary$passed, failed = summary$failed))
if (summary$failed) {
    for (case in checks) if (case$status == "FAIL") message(case$name, ": ", case$reason)
    stop("Phase 7 regression failures; inspect test-summary.json")
}
