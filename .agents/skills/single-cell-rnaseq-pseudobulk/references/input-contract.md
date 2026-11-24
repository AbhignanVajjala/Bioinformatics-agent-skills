# Pseudobulk input and evidence contract

`bioskills.expanded.pseudobulk(counts, cells, organism=..., reference=...,
count_generation=..., paired=False)` returns counts, sample metadata and an audit.
Declare nonblank scalar provenance strings and a genuine Boolean paired flag.
Require gene-by-cell raw counts and exactly aligned cell metadata containing
subject_id, specimen_id, condition, timepoint, cell_type and batch. Duplicate
columns, blank labels, specimen-context conflicts and non-string categorical
identities reject. Preserve exact string gene/cell/specimen/donor identities,
including "0001" versus "1"; timepoints may be homogeneous finite numbers or strings.

Boolean, fractional, negative, nonfinite and unsupported numeric counts reject.
Exact integer/text sources and every source/aggregate library and gene aggregate
must fit signed int64 (maximum 9223372036854775807). Float sources are limited
to exactly represented integral values <=2^53-1. Python integer arithmetic precedes
conversion. Check exact gene and library conservation; report large totals as
decimal strings. The observed four-cell 2^62 fixture rejects before wrapped export.
The historical 2^53+1 integer case was exact and remains supported generically.
R compatibility is separately reported: counts <=2147483647 and libraries <=2^53-1.

Two conditions are supported. Record donors, specimens, populations, cells and
per-population independent donor counts, declared design, rank, residual degrees
of freedom and blocking reasons. Include condition, paired donor and variable
batch in design review. Unpaired structural absence is not missing pairing.
Complete paired donor-condition observations are required per population;
repeated/longitudinal designs beyond one pair require another model.

Aggregation can execute while population inference is blocked. Readiness is
READY_FOR_DESIGN_REVIEW, never validated design or differential expression.
Differential-state modeling stays NOT_RUN. Upstream QC, identity truth, power,
cell annotation and biological validity are not authenticated by these checks.
