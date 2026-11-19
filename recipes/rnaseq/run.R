# Gene-level DE using native DESeq2 or edgeR quasi-likelihood APIs.
# Rscript recipes/rnaseq/run.R METHOD COUNTS.tsv SAMPLES.tsv CONFIG.json OUTPUT
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 5L) stop("Usage: run.R deseq2|edger counts.tsv samples.tsv config.json output")
method <- args[1]
if (!method %in% c("deseq2", "edger")) stop("Unknown method")
out <- args[5]
if (dir.exists(out) && length(list.files(out, all.files = TRUE, no.. = TRUE))) stop("Output directory must be empty")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
status <- list(analysis_status = "NOT_RUN", method = method)
tryCatch({
    cfg <- jsonlite::fromJSON(args[4])
    required <- c("organism", "reference", "count_generation", "measurement_type", "design", "reference_level", "treatment_level")
    if (!all(required %in% names(cfg)) || any(!nzchar(unlist(cfg[required])))) stop("Missing input provenance or design")
    if (cfg$measurement_type != "raw_counts") stop("Count scale must be declared raw_counts; integer appearance cannot verify provenance")
    if (!cfg$design %in% c("unpaired", "paired", "batch")) stop("Unsupported design")
    tab <- read.delim(args[2], check.names = FALSE, stringsAsFactors = FALSE)
    md <- read.delim(args[3], check.names = FALSE, stringsAsFactors = FALSE)
    if (anyDuplicated(names(tab)) || anyDuplicated(names(md))) stop("Duplicate column identifiers")
    if (ncol(tab) < 3L || nrow(tab) == 0L || !all(c("sample_id", "subject_id", "condition") %in% names(md))) stop("Missing counts or metadata fields")
    if (anyNA(tab) || anyNA(md) || anyDuplicated(tab[[1]]) || anyDuplicated(md$sample_id)) stop("Missing values or duplicate identifiers")
    if (any(!nzchar(trimws(as.matrix(md)))) || any(!nzchar(trimws(tab[[1]])))) stop("Blank identifiers or metadata")
    if (!setequal(names(tab)[-1], md$sample_id)) stop("Mismatched sample identifiers")
    reordered <- !identical(names(tab)[-1], md$sample_id)
    if (reordered && !isTRUE(cfg$align_samples)) stop("Permuted metadata requires explicit align_samples=true")
    md <- md[match(names(tab)[-1], md$sample_id), , drop = FALSE]
    counts <- as.matrix(tab[-1])
    if (!is.numeric(counts) || any(!is.finite(counts)) || any(counts < 0) || any(counts != floor(counts)) || any(counts > .Machine$integer.max)) stop("Invalid integer counts")
    rownames(counts) <- tab[[1]]
    if (any(colSums(counts) <= 0)) stop("Zero library total")
    rownames(md) <- md$sample_id
    if (cfg$reference_level == cfg$treatment_level || !setequal(unique(md$condition), c(cfg$reference_level, cfg$treatment_level))) stop("Explicit two-condition contrast required")
    md$condition <- factor(md$condition, levels = c(cfg$reference_level, cfg$treatment_level))
    replication <- tapply(md$subject_id, md$condition, function(x) length(unique(x)))
    if (any(replication < 2L)) stop("Absent independent biological replication; this minimum does not establish power")
    if (cfg$design == "paired") {
        pairs <- table(md$subject_id, md$condition)
        if (any(pairs != 1L)) stop("Paired design requires one specimen per subject and condition")
        md$donor <- factor(md$subject_id)
        formula <- ~ donor + condition
    } else {
        if (anyDuplicated(md$subject_id)) stop("Technical or repeated specimens cannot be independent subjects")
        formula <- ~ condition
        if (cfg$design == "batch") {
            if (!"batch" %in% names(md)) stop("Missing batch")
            md$batch <- factor(md$batch)
            formula <- ~ batch + condition
        }
    }
    design <- model.matrix(formula, data = md)
    rank <- qr(design)$rank
    if (rank < ncol(design)) stop("Rank-deficient design; batch correction cannot recover treatment")
    residual_df <- nrow(design) - rank
    if (residual_df <= 0L) stop("No residual degrees of freedom")
    versions <- list(R = as.character(getRversion()), Bioconductor = as.character(BiocManager::version()))
    spec <- jsonlite::fromJSON("recipes/rnaseq/environment.json")
    pkg <- if (method == "deseq2") "DESeq2" else "edgeR"
    if (versions$R != spec$R || versions$Bioconductor != spec$Bioconductor || as.character(packageVersion(pkg)) != spec[[pkg]]) stop("Analysis environment differs from pinned specification")
    versions[[pkg]] <- as.character(packageVersion(pkg))
    set.seed(731)
    if (method == "deseq2") {
        keep <- rowSums(counts >= 10) >= 2
        if (sum(keep) < 10) stop("Too few expressed genes for this dispersion recipe")
        dds <- DESeq2::DESeqDataSetFromMatrix(counts[keep, , drop = FALSE], md, formula)
        # Native fitting and outlier/independent-filter handling remain enabled.
        dds <- DESeq2::DESeq(dds, quiet = TRUE)
        result <- as.data.frame(DESeq2::results(dds, contrast = c("condition", cfg$treatment_level, cfg$reference_level), alpha = 0.05))
        normalized <- DESeq2::counts(dds, normalized = TRUE)
        pdf(file.path(out, "dispersion.pdf"))
        DESeq2::plotDispEsts(dds)
        dev.off()
        diagnostic <- data.frame(gene_id = rownames(dds), dispersion = DESeq2::dispersions(dds))
    } else {
        y <- edgeR::DGEList(counts = counts)
        keep <- edgeR::filterByExpr(y, design = design)
        if (sum(keep) < 10) stop("Too few expressed genes for this dispersion recipe")
        y <- y[keep, , keep.lib.sizes = FALSE]
        y <- edgeR::calcNormFactors(y, method = "TMM")
        y <- edgeR::estimateDisp(y, design)
        fit <- edgeR::glmQLFit(y, design, robust = FALSE)
        contrast <- rep(0, ncol(design))
        contrast[ncol(design)] <- 1
        test <- edgeR::glmQLFTest(fit, contrast = contrast)
        result <- edgeR::topTags(test, n = Inf, sort.by = "none", adjust.method = "BH")$table
        normalized <- edgeR::cpm(y, log = FALSE)
        pdf(file.path(out, "dispersion.pdf"))
        edgeR::plotBCV(y)
        dev.off()
        diagnostic <- data.frame(gene_id = rownames(y), dispersion = y$tagwise.dispersion)
    }
    write.table(data.frame(gene_id = rownames(result), result), file.path(out, "results.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(data.frame(gene_id = rownames(normalized), normalized), file.path(out, "normalized.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(diagnostic, file.path(out, "dispersion.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(data.frame(gene_id = rownames(counts), retained = keep), file.path(out, "filtering.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
    write.table(design, file.path(out, "design.tsv"), sep = "\t", quote = FALSE)
    status <- list(analysis_status = "EXECUTED", status = "PASS", method = method,
        design = paste(deparse(formula), collapse = ""), rank = rank, residual_df = residual_df,
        contrast = c(cfg$treatment_level, cfg$reference_level), aligned_metadata = reordered,
        retained_genes = sum(keep), software_versions = versions,
        inputs_md5 = as.list(tools::md5sum(args[2:4])),
        adjustment = "BH", alpha = 0.05, shrinkage = "NOT_RUN",
        limitations = c("Synthetic execution is not biological validation", "FDR families require study-specific review", "DESeq2 independent filtering and Cook outlier handling may yield NA p-values"))
    writeLines(capture.output(sessionInfo()), file.path(out, "sessionInfo.txt"))
    jsonlite::write_json(status, file.path(out, "analysis-status.json"), auto_unbox = TRUE, pretty = TRUE)
}, error = function(e) {
    status$status <- "FAIL"
    status$reason <- conditionMessage(e)
    jsonlite::write_json(status, file.path(out, "analysis-status.json"), auto_unbox = TRUE, pretty = TRUE)
    message(conditionMessage(e))
    quit(status = 1)
})
