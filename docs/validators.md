# Scientific validator interface

Run from an installed full checkout or toolkit with `python -m bioskills --help`.
Input tables use their first column as row identifiers and CSV or TSV delimiters.
Files are read without modification. Outputs must be new paths.

```text
python -m bioskills check_counts --input counts.tsv --config context.json --output count-check.json
python -m bioskills check_sample_ids --input counts.tsv --metadata samples.tsv --output id-check.json
python -m bioskills check_design_rank --input design.tsv --output design-check.json
python -m bioskills check_replication --input samples.tsv --config design.json --output unit-check.json
python -m bioskills check_fba_status --input model.xml --output flux-check.json
python -m bioskills check_leakage --input partitions.tsv --output leakage-check.json
python -m bioskills check_enrichment_background --input genes.json --config enrichment.json --output background-check.json
```

Exit 0 means implemented checks passed, including a WARN for an explicitly
requested sample reordering. Exit 2 means a scientific gate failed. Exit 3
means an optional runtime is unavailable. Exit 1 means input, format or
configuration could not be parsed. Invalid command syntax is argparse exit 2.
Scientific reports distinguish statuses and reasons in JSON. The output file
contains input basenames and hashes. Stdout emits a compact status object.
No patient or subject values are printed.

Count configuration requires `scale: raw_counts`, `organism`, `reference`
and `count_generation`. These are declared provenance and must be verified
upstream. Counts and exact integer library sums must be <=2^53-1; larger inputs
are outside the supported binary64 count scope and fail before floating summation.
Matrix labels must be homogeneous nonblank strings or finite numeric labels;
mixed-type labels are rejected without coercion. Real finite values are required
and complex observations cannot be silently cast.
Boolean raw counts are rejected. Bulk validate_counts additionally checks the
R recipe per-count limit of 2147483647; generic check_counts keeps its wider
scope for other workflows. Metadata columns must be unique before field access.
File readers preserve categorical identities, including leading zeros and long
numeric-looking labels, as exact strings and reject ragged records. Homogeneous
numeric labels in generic Python APIs remain supported; mixed numeric/text labels
are rejected before serialization can collapse distinct identities.
These gates do not authenticate the declared assay or its count universe.
Provenance must be verified
upstream. Sample matching rejects a permuted sheet by default. Configuration
`allow_reorder: true` returns metadata row positions for an explicit in-memory
order. Replication configuration accepts `paired: true` for one specimen per
subject per condition. Independent conditions require distinct declared subjects.
The minimum subject gate supplies no power guarantee.

Design matrices must be numeric with unique row and column IDs. The checker
reports rank and residual degrees of freedom. It cannot rule out unmeasured
confounding. Partition metadata uses `subject_id` and `split`, with split
labels train/test/validation. Identity errors and learned preprocessing leakage
need additional evidence.

Enrichment JSON has `selected`, `tested` and `mappings` lists. Mapping records
contain `source`, `target`, `organism` and `reference`. The baseline requires
one-to-one complete mapping. Ambiguity or dropped identifiers require an audited
policy before this baseline can proceed. Configuration specifies `organism`,
`reference` and `multiple_testing: BH`. This validator checks the declared
background and policy. An enrichment calculation is a separate workflow.

The FBA command requires COBRApy/GLPK, an SBML or COBRA JSON model, nonzero
objective and finite ordered bounds. It checks actual solver status, residuals
and flux bound violations. Optimal flux remains a model prediction.
