# Compatibility boundaries

Version 0.2.1 supplies one universal `Bioinformatics-Agent-Skills-Complete.zip`
containing the skills and Python/R toolkit. It retains `.agents/skills` paths;
the instructions can be read or copied without Python or R. Scientific execution
requires the documented dependencies from the same extraction. Host discovery and execution tools remain
host-dependent. Use Python 3.12 for the pinned toolkit scientific wheels.
R recipes enforce R 4.4.3, Bioconductor 3.20, DESeq2 1.46.0 and edgeR 4.4.2.
The R CI job has executed synthetic fits. Windows libsbml is blocked by the
current Application Control policy, so metabolic execution is checked in Linux
CI. Basic file signatures do not substitute for optional binary parsers.
Consult [Phase 3 status](phase3-status.md) for each capability.

Canonical discovery path: `.agents/skills/<name>/SKILL.md`. The portable core uses Agent Skills YAML frontmatter with `name`, `description` and optional string metadata. Repository-level `AGENTS.md` supplies durable conventions. There are no required Aava keys, hooks, model routing or vendor-specific tools.

Current format/source verification and actual tested environments are recorded in `implementation-status.md` and `reference-analysis.md`. Do not infer live Codex discovery or agent execution from a passing local parser. A host must support repository skills; open the repository as its working directory and inspect available skills before relying on automatic invocation.

Core utilities target Python 3.11+. Scientific examples use optional numerical dependencies; no GPU, private data, credentials or API is needed for the included fixtures. External literature lookup and optional R/Bioconductor or large workflow engines are separate capabilities. Their absence must be reported rather than emulated with inappropriate statistics.

Python tests execute locally on Windows and in Linux CI, with platform-specific
skips recorded in the implementation log. macOS execution remains unverified.
Solver behavior and native wheels require platform-specific validation. A CI
configuration is not proof that a hosted CI run passed.
