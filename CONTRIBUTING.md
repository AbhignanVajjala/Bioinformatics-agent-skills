# Contributing

Read [AGENTS.md](AGENTS.md), the [authoring guide](docs/authoring-guide.md),
[scientific integrity rules](docs/scientific-integrity.md) and
[development disclosure](docs/development-and-ai-assistance.md).
Keep changes narrow and preserve existing scientific and evaluation evidence.

## Contribution and attribution record

AI-assisted contributions are welcome. Disclose material assistance in the PR:
tool/model when known, affected work, implementation decisions, verification
performed and unresolved uncertainty. Do not claim personal implementation or
human review that did not occur. AI tools are not human coauthors or reviewers.
Credit identifiable human contributions and third-party sources accurately;
retain applicable licenses and existing Git attribution.

Abhignan Vajjala is the project initiator and maintainer. Maintainer acceptance
of a software change is separate from independent scientific approval.
Record the actual author, reviewer, review scope and independence in the PR.

## Scientific changes and reproducibility

State the question/estimand, experimental unit, organism/reference, data scale,
replication, confounding, missingness, multiplicity and leakage assumptions that
apply. Supply valid, scientifically invalid, malformed and relevant boundary
fixtures. A test that expects a scientific rejection must check the failure
status and reason, not merely an exception of any kind.

Record exact commands, source revision, tool versions, parameters, seeds,
immutable input/output hashes and actual artifacts. Separate executed, skipped,
blocked and NOT_RUN work. Use synthetic or appropriately licensed public
fixtures; document provenance, access terms and identifier mappings. Do not
include patient data, secrets, unsupported citations or source material whose
redistribution license is uncertain.

Run pytest, Ruff lint/format, skill validation, catalog, mode synchronization and
package freshness checks from [development installation](docs/installation.md).
For changed scientific gates, execute the relevant examples and established
software, including pinned R CI where applicable. Documentation-only work must
keep scientific sources and historical judgments unchanged. Update the
implementation status with actual results and limitations.

## Review and approval responsibilities

Passing tests verifies tested software behavior; it does not establish biological
correctness or improved agent reasoning. A human methodological review must
identify the person, relevant scope, actual reproduction, findings and unresolved
issues. Use the [technical walkthrough](docs/maintainer-technical-walkthrough.md)
as a starting point without pre-filling its completion fields. An AI role pass
does not constitute independent peer review. Maintainers assess code, evidence,
credit and scope for merging; qualified independent reviewers assess scientific
assumptions before any stronger maturity or interpretation claim.

All initial skills are experimental. Reviewed requires a named relevant human methodological
review with scope and unresolved findings recorded. Validated additionally requires a
versioned evaluation protocol, independent evidence, and explicit scope; passing structural
checks alone cannot promote maturity. Maintainers do not certify clinical applications.
Version incompatible artifact or method changes explicitly and document migrations.
