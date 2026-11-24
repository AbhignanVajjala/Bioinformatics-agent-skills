# ORA input, eligibility and multiplicity contract

`bioskills.expanded.ora(data, gene_sets, organism=..., reference=...,
database=..., release=...)` requires nonblank scalar string declarations.
Data is an object with selected/tested lists and a mappings list of records
containing exact nonblank string source, target, organism and reference fields.
Require complete one-to-one mappings, unique source/target IDs and a nonempty
selected proper subset of the eligible tested universe. Preserve leading zeros
and namespaces. Missing fields, malformed/ambiguous mappings, reference mismatch
and numeric identifiers raise controlled ScientificValidationError. Serialized
validator/config boundaries reject duplicate JSON keys, including escaped aliases.

Gene sets are a nonempty object of nonblank string pathway IDs to lists of
nonblank string target IDs. Invalid records reject the input, rather than being
silently discarded. Duplicate memberships are deduplicated and counted.

Prespecified eligibility: at least one member in the tested universe, independent
of selected overlap or observed p-value. Valid empty sets and sets with no eligible
members are excluded as EMPTY_GENE_SET and NO_UNIVERSE_MEMBERS. Eligible pathways
with zero selected overlap remain in testing and BH adjustment. Empty selected
lists reject. No eligible pathways returns NO_TESTABLE_PATHWAYS / analysis NOT_RUN.

Report the supplied family, every pathway's supplied/unique/eligible size,
duplicates and outside-universe members, exclusion reasons, eligible/testing
family and actual BH denominator. Compute one-sided Fisher exact ORA and BH over
the entire eligible family. The two-pathway 20-gene/five-selected control retains
p=1/choose(20,5), q=2/choose(20,5); the eligible null pathway has p=q=1.
The eligibility change does not change Fisher arithmetic. Association is not
activation or causality; ranked enrichment and biological validation remain NOT_RUN.
