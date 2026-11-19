# Pathway enrichment and gene identifier mapping input contract

Selected/tested identifiers, source-to-target mappings, organism, annotation release and versioned gene sets.

Python, pandas and SciPy 1.15.3 Fisher exact/BH functions.

Use the API documented in the full repository. Keep specimen, donor, assay,
reference and unit declarations explicit. Protect private metadata and never
infer unrecorded identity or provenance. Reject malformed or scientifically
incompatible inputs before downstream inference.

The API is `bioskills.expanded.ora(data, gene_sets, organism=...,
reference=..., database=..., release=...)`. Data has `selected` and `tested`
lists plus a `mappings` list of records with `source`, `target`, `organism`
and `reference`. Both source and target must be unique and all tested source
IDs must map. The selected set must be a proper subset of the eligible tested
set. `gene_sets` maps term names to lists of target IDs. Duplicate membership
and members outside the universe are counted in the output. BH correction
covers every supplied gene set, including sets with no selected overlap.
