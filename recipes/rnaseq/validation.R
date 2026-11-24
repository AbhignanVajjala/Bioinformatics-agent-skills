# Strict contracts: exact text identities; no implicit row names or object keys.
read_utf8 <- function(path) {
    bytes <- readBin(path, what = "raw", n = file.info(path)$size)
    if (any(bytes == as.raw(0))) stop("NUL bytes are unsupported")
    text <- iconv(rawToChar(bytes), from = "UTF-8", to = "UTF-8", sub = NA)
    if (is.na(text)) stop("Input must be valid UTF-8")
    text
}

read_config <- function(path) {
    text <- read_utf8(path)
    if (!jsonlite::validate(text)) stop("Malformed JSON configuration")
    # Inspect lexical structure BEFORE object parsing; decode isolated key tokens
    # so escaped key aliases also collide. jsonlite validates grammar first.
    tokens <- regmatches(text, gregexpr(r"("(?:[^"\\]|\\.)*"|[{}\[\]:,]|[^[:space:]{}\[\]:,]+)", text, perl = TRUE))[[1]]
    p <- 1L
    walk <- function(depth = 0L) {
        if (depth > 32L) stop("Configuration nesting exceeds supported scope")
        token <- tokens[p]
        p <<- p + 1L
        if (token == "{") {
            keys <- character()
            if (tokens[p] != "}") repeat {
                key <- jsonlite::fromJSON(tokens[p])
                if (key %in% keys) stop("Duplicate JSON object key")
                keys <- c(keys, key)
                p <<- p + 2L
                walk(depth + 1L)
                if (tokens[p] != ",") break
                p <<- p + 1L
            }
            p <<- p + 1L
        } else if (token == "[") {
            if (tokens[p] != "]") repeat {
                walk(depth + 1L)
                if (tokens[p] != ",") break
                p <<- p + 1L
            }
            p <<- p + 1L
        }
    }
    walk()
    if (tokens[1] != "{") stop("Configuration must be one JSON object")
    cfg <- jsonlite::fromJSON(text, simplifyVector = FALSE)
    required <- c("organism", "reference", "count_generation", "measurement_type",
        "design", "reference_level", "treatment_level")
    if (!all(required %in% names(cfg))) stop("Missing input provenance or design field")
    if (any(!names(cfg) %in% c(required, "align_samples"))) stop("Unsupported configuration field")
    for (field in required) {
        value <- cfg[[field]]
        if (!is.character(value) || length(value) != 1L || is.na(value) || !nzchar(trimws(value)))
            stop(paste("Required nonblank scalar string:", field))
    }
    if (cfg$measurement_type != "raw_counts") stop("Count scale must be raw_counts; provenance cannot be authenticated from values")
    if (!cfg$design %in% c("unpaired", "paired", "batch")) stop("Unsupported design")
    if ("align_samples" %in% names(cfg) &&
        (!is.logical(cfg$align_samples) || length(cfg$align_samples) != 1L || is.na(cfg$align_samples)))
        stop("align_samples must be a JSON Boolean")
    cfg
}

read_tsv_exact <- function(path) {
    text <- gsub("\r\n", "\n", read_utf8(path), fixed = TRUE)
    if (grepl("\r", text, fixed = TRUE)) stop("Malformed line ending")
    if (endsWith(text, "\n")) text <- substr(text, 1L, nchar(text) - 1L)
    lines <- head(strsplit(paste0(text, "\n__END__"), "\n", fixed = TRUE)[[1]], -1L)
    if (length(lines) < 2L || any(!nzchar(lines))) stop("TSV needs a header and nonempty records")
    fields <- lapply(lines, function(line) head(strsplit(paste0(line, "\t__END__"), "\t", fixed = TRUE)[[1]], -1L))
    header <- fields[[1]]
    if (any(!nzchar(trimws(header))) || anyDuplicated(header)) stop("Blank or duplicate TSV header")
    if (any(lengths(fields) != length(header))) stop("TSV field count differs from header; implicit row names are forbidden")
    result <- as.data.frame(do.call(rbind, fields[-1]), stringsAsFactors = FALSE, check.names = FALSE)
    names(result) <- header
    result
}

count_matrix <- function(tab) {
    tokens <- as.matrix(tab[-1])
    pattern <- r"(^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$)"
    if (any(!grepl(pattern, tokens, perl = TRUE))) stop("Invalid numeric count token; Boolean counts are unsupported")
    parse_integer <- function(token) {
        negative <- startsWith(token, "-")
        token <- sub("^[+-]", "", token)
        parts <- strsplit(token, "[eE]")[[1]]
        coefficient <- parts[1]
        digits <- sub("^0+", "", gsub(".", "", coefficient, fixed = TRUE))
        if (!nzchar(digits)) return(0)
        if (negative) stop("Counts must be nonnegative")
        exponent <- if (length(parts) == 2L) parts[2] else "0"
        if (nchar(exponent) > 6L) stop("Count exponent is outside supported integer scope")
        fraction <- if (grepl(".", coefficient, fixed = TRUE)) sub("^[^.]*\\.", "", coefficient) else ""
        shift <- as.integer(exponent) - nchar(fraction)
        if (shift < 0L) {
            if (-shift >= nchar(digits) || grepl("[1-9]", substr(digits, nchar(digits) + shift + 1L, nchar(digits))))
                stop("Count token is fractional before floating conversion")
            digits <- substr(digits, 1L, nchar(digits) + shift)
        } else {
            if (nchar(digits) + shift > 10L) stop("Count exceeds the supported R integer range")
            digits <- paste0(digits, paste(rep("0", shift), collapse = ""))
        }
        if (nchar(digits) > 10L) stop("Count exceeds the supported R integer range")
        as.numeric(digits)
    }
    # Fast exact path for ordinary integer text; general decimal/exponent tokens
    # are checked lexically so sub-ulp fractions/underflow cannot become integers.
    if (all(grepl("^[+]?[0-9]+$", tokens))) {
        digits <- sub("^0+", "", sub("^\\+", "", tokens))
        if (any(nchar(digits) > 10L)) stop("Count exceeds the supported R integer range")
        digits[digits == ""] <- "0"
        numeric_values <- as.numeric(digits)
    } else numeric_values <- vapply(as.vector(tokens), parse_integer, numeric(1))
    counts <- matrix(numeric_values, nrow = nrow(tokens), dimnames = list(tab[[1]], names(tab)[-1]))
    if (any(!is.finite(counts)) || any(counts < 0) || any(counts != floor(counts)) || any(counts > .Machine$integer.max))
        stop("Invalid integer counts; each count must be between zero and 2147483647")
    counts
}

library_totals <- function(counts, stage) {
    totals <- colSums(counts)
    if (any(!is.finite(totals)) || any(totals <= 0) || any(totals > 2^53 - 1))
        stop(paste(stage, "library totals must be finite, positive and <=2^53-1; review filtering and input counts"))
    as.list(totals)
}

encode_factor <- function(values, prefix) {
    original <- unique(values)
    codes <- paste0(prefix, seq_along(original))
    list(factor = factor(codes[match(values, original)], levels = codes),
        mapping = data.frame(original = original, model_level = codes, stringsAsFactors = FALSE))
}

bh_audit <- function(p, adjusted) {
    if (length(p) != length(adjusted) || !any(is.finite(p)) ||
        any(!is.na(p) & (!is.finite(p) | p < 0 | p > 1)) ||
        any(!is.na(adjusted) & (!is.finite(adjusted) | adjusted < 0 | adjusted > 1)))
        stop("Invalid or entirely unavailable gene-level statistical results")
    family <- !is.na(adjusted)
    if (any(family & !is.finite(p))) stop("Adjusted values require corresponding finite p-values")
    # Native independent filtering determines the DESeq2 adjustment family.
    raw <- p[family]
    ordering <- order(raw)
    m <- length(raw)
    expected <- numeric(m)
    # Independent ordered/monotone BH implementation, not the package's p.adjust.
    if (m) expected[ordering] <- pmin(1, rev(cummin(rev(raw[ordering] * m / seq_len(m)))))
    if (any(!is.finite(adjusted[family])) || any(abs(expected - adjusted[family]) > 1e-12))
        stop("Independent BH verification failed")
    list(finite_p_values = sum(is.finite(p)), adjusted_family = sum(family),
         missing_p_values = sum(is.na(p)), missing_adjusted = sum(is.na(adjusted)),
         status = if (any(family)) "PASS" else "NOT_RUN", tolerance = 1e-12,
         comparison = "independent ordered monotone BH on the native adjustment family")
}
