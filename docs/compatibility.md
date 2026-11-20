# Compatibility boundaries

Version 0.2.2 supplies one universal `Bioinformatics-Agent-Skills-Complete.zip`
containing the skills and Python/R toolkit. It retains `.agents/skills` paths;
the instructions can be read or copied without Python or R. Scientific execution
requires the documented dependencies from the same extraction. Host discovery and execution tools remain
host-dependent. Use Python 3.12 for the pinned toolkit scientific wheels.
R recipes enforce R 4.4.3, Bioconductor 3.20, DESeq2 1.46.0 and edgeR 4.4.2.
The R CI job has executed synthetic fits. Prior local Windows libsbml imports
were blocked by Application Control; hosted Windows and Linux extracted-package
jobs executed the metabolic workflows. Those records do not guarantee every
machine's native dependencies. Basic signatures do not replace binary parsers.
Consult [Phase 3 status](phase3-status.md) for each capability.

Canonical discovery path: `.agents/skills/<name>/SKILL.md`. The portable core uses Agent Skills YAML frontmatter with `name`, `description` and optional string metadata. Repository-level `AGENTS.md` supplies durable conventions. There are no required Aava keys, hooks, model routing or vendor-specific tools.

The [host matrix](agent-host-compatibility.md) separates official installation
documentation from tested collection installation, discovery and invocation.
Codex is one documented example. Other hosts' behaviors remain NOT_TESTED for
this collection; a passing parser does not establish host integration.
Historical Codex CLI evidence remains in the original evaluation records.
Current and historical environments are recorded in the implementation status
and reference analysis. See [scientific evidence](scientific-evidence.md) for
the distinction between runtime execution and scientific validity.

Core utilities target Python 3.11+. Scientific examples use optional numerical dependencies; no GPU, private data, credentials or API is needed for the included fixtures. External literature lookup and optional R/Bioconductor or large workflow engines are separate capabilities. Their absence must be reported rather than emulated with inappropriate statistics.

Python tests execute locally on Windows and in Linux CI, with platform-specific
skips recorded in the implementation log. macOS execution remains unverified.
Solver behavior and native wheels require platform-specific validation. A CI
configuration is not proof that a hosted CI run passed.
