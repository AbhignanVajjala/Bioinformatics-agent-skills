# Phase 4 presentation and scientific-claim audit

Date: 2026-11-20. Baseline: `afd14e927e49a06df3ad7268532769c6e93002fb`.
This is an automated documentation audit, not independent human peer review.

## Platform-reference classification

The [baseline occurrence census](../references/phase4-presentation-audit.json)
records each matching line and term in every baseline Git-tracked Markdown,
CFF, JSON, workflow YAML and TOML document. It retains file/line locators instead
of copying historical runtime details. Sixteen files contain matches: 24 lines
are category 1, 125 category 2 and three category 3. The scan is lexical;
the claim dispositions below require source/evidence review separately.

| Category | Baseline examples and disposition |
|---|---|
| 1: necessary platform-specific instructions | `INSTALL.md` and `docs/installation.md` Codex paths/examples; shell/OS setup in `TOOLKIT_INSTALL.md`; runtime/CI limitations. Preserve accurate examples, add a neutral introduction and a documented-versus-tested host matrix. Canonical `.agents/skills/`, all skill bodies, `AGENTS.md`, evaluation-runner APIs and tests remain intact. |
| 2: historical development/evaluation evidence | Existing implementation/development logs, reference analysis, publication audit, Phase 3 status, pilot scores/reviews/provenance and R execution provenance. Preserve original records and model/runtime details. New dated status entries precede historical log bodies without editing them. |
| 3: unnecessary single-host presentation | README's general quick start framed as opening in Codex; compatibility prose singled out Codex for a general parser/discovery limit; roadmap's general discovery priority named only Codex. Replace general framing with agent-host wording, retain Codex as an explicit example, and keep its historical evidence. |

The baseline index's `$skill-name` examples are retained and explicitly labeled
as Codex notation. Other hosts' selection syntax and actual discovery are not
inferred from those examples. No mechanical replacement of platform names was
performed. Source code and CLI terminology are necessary runtime interfaces,
not evidence of exclusive project identity.

## Capability, validation and attribution dispositions

| Claim area | Source/evidence examined | Public disposition |
|---|---|---|
| Skill count and taxonomy | All canonical skill paths and generated index | 17 experimental skills: seven domain, ten foundation/maintainer; do not count foundation instructions as biological methods |
| Seven validators | `NAMES`, API/CLI dispatch, valid/scientific-invalid/malformed fixtures | State exactly the implemented gates, numerical/metadata limits and dependency blockers |
| RNA-seq | Native R recipe, test driver, pinned environment and hashed execution record | Actual DESeq2/edgeR fits distinguished from original Python readiness example; no biological discovery claim |
| Metabolic modeling | COBRApy recipe, numerical gates and negative controls | Toy steady-state predictions, not measured flux or validated engineering benefit |
| Multi-omics | Reconciliation, scale declarations, feature mapping and Pearson code/tests | Descriptive two-assay cross-view baseline; no MOFA2/SNF, causal or predictive claim |
| Added domain utilities | Pseudobulk/ORA/format/client implementations and fixtures | Aggregation, Fisher/BH, scoped text/signature inspection and mocked metadata tests only; unexecuted scope stays NOT_RUN |
| Python/R/CI results | Preserved run IDs, reports, test implementations and distribution logs | Separate structural checks, deterministic gates, synthetic execution, platform installation and human scientific review |
| Agent pilot | Original score JSON, review, manifests/rubric and access-provenance document | Preserve provisional 0 PASS/4 FAIL/6 BLOCKED; four observed reads do not prove instruction-following or effectiveness |
| Maintainer identity | User-provided project role, repository ownership and existing Git history | Name Abhignan Vajjala as initiator/maintainer, retain contributors credit and existing author strings; no sole-code-authorship inference |
| AI assistance and human review | Development history and explicit task disclosure | Acknowledge substantial AI assistance including OpenAI Codex; independent human methodological/biological review remains incomplete |
| Citation and licensing | CFF 1.2.0 schema, original citation credit and MIT LICENSE | Use valid person/contact fields, retain contributor entity, invent no DOI/ORCID/affiliation; leave LICENSE unchanged |

The [machine-readable claim ledger](../references/phase4-scientific-claim-ledger.json)
links these scoped claims to artifacts and marks the automated reviewer as
non-independent, with human approval pending. The
[documentation source record](../references/phase4-documentation-sources.json)
records official host/format sources and the citation schema hash.

## Remaining review boundary

The [technical walkthrough](maintainer-technical-walkthrough.md) contains blank
human execution/reviewer/environment/findings fields marked NOT_REVIEWED.
No human review, experimental validation, new agent behavior or improved
scientific reasoning was manufactured for presentation. Full validation and
publication outcomes belong in the new dated implementation-status entry.

## Exact changed-file inventory

Eight new files:

- `docs/agent-host-compatibility.md`
- `docs/development-and-ai-assistance.md`
- `docs/maintainer-technical-walkthrough.md`
- `docs/phase4-presentation-audit.md`
- `docs/scientific-evidence.md`
- `references/phase4-documentation-sources.json`
- `references/phase4-presentation-audit.json`
- `references/phase4-scientific-claim-ledger.json`

Twenty updated files:

- `README.md`, `START_HERE.md`, `INSTALL.md`, `TOOLKIT_INSTALL.md`
- `SKILL_INDEX.md`, `CONTRIBUTING.md`, `CITATION.cff`, `RELEASE.json`, `CHANGELOG.md`
- `docs/architecture.md`, `docs/compatibility.md`, `docs/installation.md`, `docs/roadmap.md`
- `docs/implementation-status.md`, `docs/development-progress.md` (new dated entries only)
- `pyproject.toml` (version/maintainer metadata only)
- `scripts/build_catalog.py` (generated index wording only)
- `scripts/package_skills.py` (six documentation entries added to the curated inventory)
- `Bioinformatics-Agent-Skills-Complete.zip`, `SHA256SUMS`

No scientific source, test assertion, evaluation record, skill instruction,
AGENTS.md, LICENSE or GitHub Actions workflow is changed. Generated test reports,
temporary environments and the downloaded validation schema remain ignored.
