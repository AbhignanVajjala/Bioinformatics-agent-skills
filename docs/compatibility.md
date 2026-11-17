# Compatibility boundaries

Canonical discovery path: `.agents/skills/<name>/SKILL.md`. The portable core uses Agent Skills YAML frontmatter with `name`, `description` and optional string metadata. Repository-level `AGENTS.md` supplies durable conventions. There are no required Aava keys, hooks, model routing or vendor-specific tools.

Current format/source verification and actual tested environments are recorded in `implementation-status.md` and `reference-analysis.md`. Do not infer live Codex discovery or agent execution from a passing local parser. A host must support repository skills; open the repository as its working directory and inspect available skills before relying on automatic invocation.

Core utilities target Python 3.11+. Scientific examples use optional numerical dependencies; no GPU, private data, credentials or API is needed for the included fixtures. External literature lookup and optional R/Bioconductor or large workflow engines are separate capabilities. Their absence must be reported rather than emulated with inappropriate statistics.

Linux is the development execution environment. Windows and macOS portability is an intention, not verified evidence, unless separately listed in the implementation log. Solver behavior, native wheels and path conventions require platform-specific validation. A CI configuration is not proof that a hosted CI run passed.
