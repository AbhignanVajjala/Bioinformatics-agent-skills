# Reference inspection and independent implementation

Inspected 2026-11-17: user-supplied Skills.zip, SHA256
`bdb141719e8f00d8eecb97d130e274027d2379b8cc925fe7cfb08c48d66d0a65`.
107 files under skills/; ignored Apple resource-fork entries. Archive read through
Python zipfile without extraction or executing its scripts. README advertises 59 core
skills (46 tools, 4 workflows, 9 personas); additional advanced files exist, so that
advertised count is not a verified inventory of installable skills.

Reviewed README, template and representative prompt-eng, context-eng, spec-driven-dev,
parallel-agents, task-breakdown, incremental-impl, source-driven-dev, tdd-practice,
quality-review, data-pipeline, systematic-debugging_advance,
verification-before-completion_advance and subagent-driven-development_advance material.

| Pattern | Independent adaptation |
|---|---|
| Work divided into definition, implementation and verification | Research specification followed by explicit input, statistical, numerical, interpretation and provenance gates |
| Inputs and outputs made explicit | Dataset manifests, claim ledgers and named analysis artifacts |
| Context supplied progressively | Canonical SKILL.md discovery; focused references loaded on demand |
| Small verified increments | Three executable synthetic scientific examples with invalid-input regression tests |
| Source-based decisions | Official tool references, checked-source status and unresolved evidence |
| Root-cause debugging | Separate metadata, design, environment, optimization and biological explanations |
| Separate implementation/review roles | Named reviewer provenance; subagent execution is not human scientific peer review |
| Dependency-aware parallel tasks | Independent file ownership and integration checks; scientific gates remain sequential when dependent |

Rejected assumptions: Aava-specific IDE lifecycle, backend synchronization, model routing,
custom frontmatter such as compose/whenToUse/type, hooks, model budgets and implicit
subagent creation. A Markdown persona has no execution authority. Publication is not an
automatic final stage of analysis. Successful tests do not establish biological validity.

## Licensing decision

No LICENSE/COPYING/copyright file was found. A scan of Markdown mentions found generic
license-review advice, not a grant to redistribute the archive. Its authorship and any
upstream advanced material's license remain unverified. An uploaded copy is not a
redistribution license. No skill body, custom template, script, asset or proprietary
configuration was copied into this repository. Only general architectural ideas informed
original work. The project's MIT license applies to its original files, not Skills.zip.
This is not an official Aava product and has no claimed Aava, nf-core or GA4GH affiliation.

## Standards evidence

Read https://raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx
on 2026-11-17 (HTTP 200), the official source of https://agentskills.io/specification.
The validator implements its required name/description and optional field constraints.
It also rejects unknown fields and duplicate YAML keys as project policy. Local link
checks verify paths, not external URLs or anchor semantics.

The requested https://learn.chatgpt.com/docs/build-skills and agentskills.io host returned
HTTP 403 here. Official https://raw.githubusercontent.com/openai/codex/main/docs/skills.md
was fetched; it redirects readers to https://developers.openai.com/codex/skills, which
was blocked by the outbound proxy. Consequently current Codex runtime discovery is
NOT_TESTED; .agents/skills follows the requested convention without inventing host
features. Cross-host compatibility requires actual host tests.
