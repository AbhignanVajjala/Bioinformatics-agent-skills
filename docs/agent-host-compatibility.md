# Agent-host compatibility and verification

The collection uses `SKILL.md` with YAML metadata and relative references,
following the [Agent Skills specification](https://agentskills.io/specification).
Canonical sources and the universal ZIP retain `.agents/skills/<name>/SKILL.md`.
Format compatibility, installation, automatic selection, file access and
scientific instruction-following are separate claims.

The paths below were checked against official documentation on **2026-11-20**.
They are documented setup options, not verified installations of this collection.
`~` means the user's home directory; it is not a literal Windows folder name.
No host/model sessions were launched for this documentation work.

| Agent host | Documented project / user locations | Format compatibility | Tested collection installation | Verified automatic discovery | Verified invocation of this collection | Known limits |
|---|---|---|---|---|---|---|
| Codex | `.agents/skills/` / `~/.agents/skills/` | Documented `SKILL.md` format; local parser checks pass | NOT_TESTED as a separate reproducible host-install acceptance test | NOT_TESTED as a general discovery claim | NOT_TESTED as a general invocation guarantee; historical staged CLI pilot observed four file reads across three turns | File reads do not prove activation or instruction-following; CLI sandbox/session results are version-specific |
| Claude Code | `.claude/skills/` / `~/.claude/skills/` | Documented skill format; this collection NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | Copy complete skill folders; host-specific syntax and local/cloud/session policies differ |
| Cursor | `.agents/skills/` or `.cursor/skills/` / corresponding user locations | Documented skill format; this collection NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | Local, remote and cloud availability depend on host settings and installation scope |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` alias / corresponding user locations | Documented skill format; this collection NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | Activation/consent, workspace scope and resource access must be checked in the chosen runtime |

Official sources: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills),
[Cursor](https://cursor.com/docs/skills),
[Gemini CLI](https://geminicli.com/docs/cli/skills/).
Vendor documentation describes its host; it does not validate this collection.

## Install and select

Extract the universal ZIP and keep a complete copy for scientific execution.
For instructions only, copy each entire skill folder, including `references/`,
to the location documented for your host. Review conflicts with existing skills
and retain the license. Keep the canonical archive unchanged when making a
host-specific installation copy.

Open the intended project, inspect the host's available-skill list, and select
a skill using its documented mechanism. For example, Codex accepts an explicit
`$bulk-rnaseq-differential-expression` request. This syntax is a Codex example,
not a universal invocation command. An explicit request to read a skill file
is a fallback instruction, not proof of automatic discovery.

Record host/version, OS, scope, discovered names, prompt, permissions, observed
file access and outputs before changing a NOT_TESTED cell. Assess scientific
behavior against fixed criteria separately. Do not weaken sandboxing, enable
network access or grant external-action permissions merely to improve a result.

## Existing evidence boundaries

The historical Codex CLI pilot completed ten turns. Provisional scientific
verdicts were 0 PASS, 4 FAIL and 6 BLOCKED. Its later access extractor confirmed
file reads, while semantic activation remained unverified. Read the preserved
[pilot provenance](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/agent-benchmark-provenance.md)
and [review](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/evals/reports/agent-benchmark-summary.md).

Python installation/CLI tests on Windows and Linux exercise the scientific
toolkit independently of an agent host. They establish neither host discovery
nor clinical validity. See [scientific evidence](scientific-evidence.md) and
[installation](../INSTALL.md).
