# Changelog

## 0.2.1 — universal distribution (Phase 3.11)

Supersedes the two-ZIP distribution with one
`Bioinformatics-Agent-Skills-Complete.zip`, preserving its public download URL.
The universal archive includes all 17 experimental skills and the entire
previous toolkit inventory: Python validators and scientific implementations,
synthetic examples, pinned R/Bioconductor recipes, schemas, templates and
dependency manifests. Shared mode and source records are also bundled.

Removes the redundant Toolkit ZIP and synchronizes installation instructions.
Adds independent extracted-package installation/CLI tests, binary-byte
preservation, portable-path and credential-pattern checks. Packaging and CI
enforce one archive and one checksum entry in SHA256SUMS. Version and checksum
metadata describe distribution only; scientific instructions, implementations,
benchmark criteria and historical judgments are preserved. All capabilities
remain experimental and have no clinical validation.

## 0.2.0 — experimental Phase 3

Adds pinned DESeq2/edgeR synthetic workflows, richer SBML/GPR and cross-view
recipes, seven scientific validator commands, shared Quick/Full instructions,
and four scoped domain skills. The collection now has 17 skills. Original
scientific gates and Phase 2 pilot verdicts are preserved.

Historically added a separate executable toolkit ZIP (superseded by 0.2.1) with a tested first-use example,
release metadata, installation guidance and a selection index. The original
Complete ZIP filename and URL remain stable. Both package checksums are in
SHA256SUMS. Toolkit dependencies require Python 3.12 and optional pinned R.
The validator report adds a new schema without changing the seven existing
artifact contracts.

See docs/phase3-status.md for executed scope, unresolved dependencies and
unfinished additional domains. This experimental release has no clinical
validation. Publication and CI state are recorded in implementation status.

## 0.1.0 — unreleased

Initial experimental skills, structured scientific artifacts, deterministic readiness gates,
synthetic examples and offline evaluation tooling. See implementation-status for execution
evidence and deferred capabilities. This version has not been published.
