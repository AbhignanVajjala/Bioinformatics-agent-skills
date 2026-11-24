# Gene-level DE; native statistical safeguards remain enabled.
# Rscript recipes/rnaseq/run.R METHOD COUNTS.tsv SAMPLES.tsv CONFIG.json OUTPUT
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 5L) stop("Usage: run.R deseq2|edger counts.tsv samples.tsv config.json output")
method <- args[1]
out <- args[5]
if (dir.exists(out) && length(list.files(out, all.files = TRUE, no.. = TRUE))) stop("Output directory must be empty")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
status <- list(analysis_status = "NOT_RUN", status = "NOT_RUN", method = method,
    stage = "configuration", model_fit_status = "NOT_RUN", command = commandArgs(),
    started_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC"),
    source_md5 = as.list(tools::md5sum(c("recipes/rnaseq/run.R", "recipes/rnaseq/validation.R", "recipes/rnaseq/environment.json"))))
diagnostics <- list()
record_diagnostic <- function(condition, kind) {
    diagnostics[[length(diagnostics) + 1L]] <<- list(stage = status$stage, kind = kind,
        message = conditionMessage(condition))
    # Native messages and warnings are deliberately not muffled.
}
tryCatch(withCallingHandlers({
    source("recipes/rnaseq/validation.R", local = TRUE)
    if (!method %in% c("deseq2", "edger")) stop("Unknown method")
    cfg <- read_config(args[4])
    status$stage <- "input_validation"
    tab <- read_tsv_exact(args[2])
    md <- read_tsv_exact(args[3])
    if (ncol(tab) < 3L || !all(c("sample_id", "subject_id", "condition") %in% names(md))) stop("Missing counts or metadata fields")
    if (anyDuplicated(tab[[1]]) || anyDuplicated(md$sample_id)) stop("Duplicate identifiers")
    if (any(!nzchar(trimws(as.matrix(md)))) || any(!nzchar(trimws(tab[[1]])))) stop("Blank identifiers or metadata")
    if (!setequal(names(tab)[-1], md$sample_id)) stop("Mismatched sample identifiers")
    reordered <- !identical(names(tab)[-1], md$sample_id)
    if (reordered && !isTRUE(cfg$align_samples)) stop("Permuted metadata requires explicit align_samples=true")
    md <- md[match(names(tab)[-1], md$sample_id), , drop = FALSE]
    counts <- count_matrix(tab)
    status$input_libraries <- library_totals(counts, "Input")
    rownames(md) <- md$sample_id
    if (cfg$reference_level == cfg$treatment_level || !setequal(unique(md$condition), c(cfg$reference_level, cfg$treatment_level))) stop("Explicit two-condition contrast required")
    replication <- tapply(md$subject_id, md$condition, function(x) length(unique(x)))
    if (any(replication < 2L)) stop("Absent independent biological replication; minimum does not establish power")
    # Preserve external text in metadata.tsv. Explicit internal coding prevents
    # modeling-package make.names collisions, never merges original identities.
    # Fit in one canonical orientation independent of requested contrast. Native
    # refitting with a different reference can introduce small numerical changes.
    # Reversal should change the contrast, not normalization/dispersion/fitting.
    condition_levels <- sort(unique(md$condition), method = "radix")
    condition_codes <- setNames(c("level1", "level2"), condition_levels)
    treatment_code <- condition_codes[[cfg$treatment_level]]
    reference_code <- condition_codes[[cfg$reference_level]]
    contrast_sign <- if (treatment_code == "level2") 1 else -1
    model_md <- data.frame(condition = factor(unname(condition_codes[md$condition]),
        levels = c("level1", "level2")), row.names = md$sample_id)
    mappings <- list(condition = data.frame(original = condition_levels,
        model_level = c("level1", "level2")))
    used <- "condition"
    if (cfg$design == "paired") {
        pairs <- table(md$subject_id, md$condition)
        if (any(pairs != 1L)) stop("Paired design requires one specimen per subject and condition")
        donor <- encode_factor(md$subject_id, "donor")
        model_md$donor <- donor$factor
        mappings$subject_id <- donor$mapping
        used <- c(used, "subject_id")
        formula <- ~ donor + condition
    } else {
        if (anyDuplicated(md$subject_id)) stop("Technical or repeated specimens cannot be independent subjects")
        formula <- ~ condition
        if (cfg$design == "batch") {
            if (!"batch" %in% names(md)) stop("Missing batch")
            batch <- encode_factor(md$batch, "batch")
            if (nlevels(batch$factor) < 2L) stop("Batch design requires at least two batch levels")
            model_md$batch <- batch$factor
            mappings$batch <- batch$mapping
            used <- c(used, "batch")
            formula <- ~ batch + condition
        }
    }
    ignored <- setdiff(names(md), c("sample_id", "subject_id", used))
    risks <- "Condition association is not a treatment-specific causal effect"
    batch_table <- NULL
    if ("batch" %in% names(md)) {
        batch_table <- table(md$batch, md$condition)
        if (nrow(batch_table) > 1L && all(rowSums(batch_table > 0) == 1L))
            risks <- c(risks, "Declared batch is confounded with condition; unadjusted effects cannot separate them")
    }
    if (length(ignored)) risks <- c(risks, "Supplied covariates excluded from the selected formula are not adjusted")
    status$design_audit <- list(used_covariates = used, ignored_covariates = ignored,
        adjusted = setdiff(used, "condition"), risks = risks, factor_coding = mappings,
        condition_batch_table = if (!is.null(batch_table)) as.data.frame(batch_table) else NULL)
    design <- model.matrix(formula, data = model_md)
    rank <- qr(design)$rank
    if (rank < ncol(design)) stop("Rank-deficient design; batch correction cannot recover treatment")
    residual_df <- nrow(design) - rank
    if (residual_df <= 0L) stop("No residual degrees of freedom")
    term <- match("condition", attr(terms(formula), "term.labels"))
    coefficient <- colnames(design)[which(attr(design, "assign") == term)]
    if (length(coefficient) != 1L) stop("Condition coefficient is ambiguous")
    versions <- list(R = as.character(getRversion()), Bioconductor = as.character(BiocManager::version()))
    spec <- jsonlite::fromJSON("recipes/rnaseq/environment.json")
    pkg <- if (method == "deseq2") "DESeq2" else "edgeR"
    for (name in c(pkg, "jsonlite", "BiocManager")) {
        versions[[name]] <- as.character(packageVersion(name))
        if (versions[[name]] != spec[[name]]) stop("Analysis package differs from pinned specification")
    }
    if (versions$R != spec$R || versions$Bioconductor != spec$Bioconductor) stop("Analysis environment differs from pinned specification")
    status$software_versions <- versions
    status$requested_normalization <- if (method == "deseq2") "ratio" else "TMM"
    status$requested_dispersion_fit <- if (method == "deseq2") "parametric" else "edgeR estimateDisp + QL robust=FALSE"
    status$stage <- "filtering"
    set.seed(731)
    if (method == "deseq2") {
        keep <- rowSums(counts >= 10) >= 2
    } else {
        y <- edgeR::DGEList(counts = counts)
        keep <- edgeR::filterByExpr(y, design = design)
    }
    if (sum(keep) < 10) stop("Too few expressed genes for this dispersion recipe")
    retained <- counts[keep, , drop = FALSE]
    status$retained_libraries <- library_totals(retained, "Post-filtering")
    if (method == "deseq2" && !any(rowSums(retained > 0) == ncol(retained)))
        stop("DESeq2 ratio size factors require a retained gene positive in every sample; choose a separately justified normalization policy, not an automatic substitute")
    status$stage <- "model_fitting"
    status$model_fit_status <- "STARTED"
    if (method == "deseq2") {
        dds <- DESeq2::DESeqDataSetFromMatrix(retained, model_md, formula)
        dds <- DESeq2::DESeq(dds, fitType = "parametric", sfType = "ratio", quiet = FALSE)
        actual_fit <- attr(DESeq2::dispersionFunction(dds), "fitType")
        if (is.null(actual_fit)) stop("Actual dispersion fit could not be recorded")
        normalization <- list(requested = "ratio", actual = "median-of-ratios",
            size_factors = as.list(setNames(DESeq2::sizeFactors(dds), md$sample_id)))
        dispersion_fit <- list(requested = "parametric", actual = actual_fit)
        result_object <- DESeq2::results(dds, contrast = c("condition", treatment_code, reference_code), alpha = 0.05)
        result <- as.data.frame(result_object)
        if (!"condition_level2_vs_level1" %in% DESeq2::resultsNames(dds)) stop("Named DESeq2 contrast coefficient absent")
        status$native_contrast_coefficient <- "condition_level2_vs_level1"
        normalized <- DESeq2::counts(dds, normalized = TRUE)
        diagnostic <- data.frame(gene_id = rownames(dds), dispersion = DESeq2::dispersions(dds))
        adjustment_audit <- bh_audit(result$pvalue, result$padj)
        result_metadata <- S4Vectors::metadata(result_object)
        adjustment_audit$independent_filter_threshold <- result_metadata$filterThreshold
        adjustment_audit$independent_filter_quantile <- result_metadata$filterTheta
        limitations <- "DESeq2 native independent filtering and Cook outlier handling may yield NA p-values/adjusted values; no shrinkage"
    } else {
        y <- y[keep, , keep.lib.sizes = FALSE]
        y <- edgeR::calcNormFactors(y, method = "TMM")
        normalization <- list(requested = "TMM", actual = "TMM", factors = as.list(setNames(y$samples$norm.factors, md$sample_id)),
            effective_library_sizes = as.list(setNames(y$samples$lib.size * y$samples$norm.factors, md$sample_id)))
        y <- edgeR::estimateDisp(y, design)
        fit <- edgeR::glmQLFit(y, design, robust = FALSE)
        contrast <- setNames(rep(0, ncol(design)), colnames(design))
        contrast[[coefficient]] <- contrast_sign
        status$native_contrast_coefficient <- coefficient
        test <- edgeR::glmQLFTest(fit, contrast = contrast)
        result <- edgeR::topTags(test, n = Inf, sort.by = "none", adjust.method = "BH")$table
        normalized <- edgeR::cpm(y, log = FALSE)
        diagnostic <- data.frame(gene_id = rownames(y), dispersion = y$tagwise.dispersion)
        dispersion_fit <- list(requested = "edgeR estimateDisp + QL robust=FALSE", actual = "edgeR estimateDisp + QL robust=FALSE")
        adjustment_audit <- bh_audit(result$PValue, result$FDR)
        limitations <- "edgeR filterByExpr prefilter, TMM and quasi-likelihood robust=FALSE; normalized.tsv is CPM, not DESeq2 normalized counts"
    }
    status$model_fit_status <- "COMPLETE"
    status$normalization <- normalization
    status$dispersion_fit <- dispersion_fit
    status$adjustment_audit <- adjustment_audit
    status$stage <- "result_validation"
    normalization_values <- unlist(normalization[setdiff(names(normalization), c("requested", "actual"))])
    if (any(!is.finite(normalized)) || any(!is.finite(normalization_values)) || any(normalization_values <= 0)) stop("Invalid normalization output or factors")
    if (!identical(rownames(result), rownames(retained)) || !identical(rownames(normalized), rownames(retained)) ||
        !identical(diagnostic$gene_id, rownames(retained))) stop("Output gene identifiers differ from retained family")
    status$stage <- "export"
    pdf(file.path(out, "dispersion.pdf"))
    if (method == "deseq2") DESeq2::plotDispEsts(dds) else edgeR::plotBCV(y)
    dev.off()
    write.table(data.frame(gene_id = rownames(result), result), file.path(out, "results.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    normalized_export <- data.frame(gene_id = rownames(normalized), normalized, check.names = FALSE)
    names(normalized_export)[1] <- names(tab)[1]
    write.table(normalized_export, file.path(out, "normalized.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(diagnostic, file.path(out, "dispersion.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(data.frame(gene_id = rownames(counts), retained = keep), file.path(out, "filtering.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(data.frame(sample_id = rownames(design), design, check.names = FALSE), file.path(out, "design.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(md, file.path(out, "metadata.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    status <- c(status, list(design = paste(deparse(formula), collapse = ""), rank = rank, residual_df = residual_df,
        contrast = c(cfg$treatment_level, cfg$reference_level), contrast_coefficient = coefficient,
        contrast_sign = contrast_sign, fit_orientation = condition_levels,
        aligned_metadata = reordered, retained_genes = sum(keep),
        inputs_md5 = as.list(tools::md5sum(args[2:4])),
        adjustment = "BH", alpha = 0.05, shrinkage = "NOT_RUN", biological_validation = "NOT_RUN",
        limitations = c("Synthetic execution is not biological validation", "FDR families and confounding require study-specific review", limitations)))
    status$analysis_status <- "EXECUTED"
    status$status <- "PASS"
    status$stage <- "complete"
    status$diagnostics <- diagnostics
    status$finished_at <- format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
    writeLines(capture.output(sessionInfo()), file.path(out, "sessionInfo.txt"))
    jsonlite::write_json(status, file.path(out, "analysis-status.json"), auto_unbox = TRUE, pretty = TRUE, digits = NA)
}, warning = function(w) record_diagnostic(w, "warning"), message = function(m) record_diagnostic(m, "message")), error = function(e) {
    status$status <- "FAIL"
    if (status$model_fit_status != "NOT_RUN") status$analysis_status <- "FAILED"
    if (status$model_fit_status == "STARTED") status$model_fit_status <- "FAILED"
    status$reason <- conditionMessage(e)
    status$finished_at <- format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
    status$diagnostics <- diagnostics
    status$emitted_artifacts <- list.files(out)
    status$inputs_md5 <- as.list(tools::md5sum(args[2:4]))
    jsonlite::write_json(status, file.path(out, "analysis-status.json"), auto_unbox = TRUE, pretty = TRUE, digits = NA)
    message(conditionMessage(e))
    quit(status = 1)
})
