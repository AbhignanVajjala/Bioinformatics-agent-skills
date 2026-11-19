---
name: bioinformatics-skill-authoring
description: "Author or review a reusable scientific Agent Skill with precise triggers, methods, evidence gates and adversarial evaluations; use for library contributions, not to generate placeholder skills or certify untested biomedical expertise."
metadata:
  maturity: experimental
---

# Bioinformatics skill authoring

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Inputs and preflight
Require a bounded scientific capability, intended users, required data/tool types, neighboring skills, authoritative sources and available test fixtures. Verify current Agent Skills metadata requirements before changing the format. Use original instructions; an uploaded or public file is not permission to redistribute its text.

## Method selection and procedure
1. Define one decision boundary: when the skill should trigger, when a neighboring skill is appropriate and when the requested analysis is scientifically invalid. Write two positive and two negative trigger prompts before the body.
2. Identify scientific prerequisites: organism/reference, experimental unit, data scale, independent replication, permissions and resources. Make essential missing context a stop condition rather than an opportunity to improvise.
3. Write actionable method-selection rules and a procedure with named artifacts. Teach established tools and their assumptions; do not reimplement statistical methods to avoid installing a trusted package.
4. Add input, computational, statistical, interpretation and provenance gates with explicit statuses. Include at least one realistic invalid-data fixture that must block analysis and one valid small fixture with asserted output.
5. Place the canonical skill at `.agents/skills/<name>/SKILL.md`. Use YAML `name` and `description`, optional string-valued `metadata`, and relative references inside the skill for deep material. Keep host-specific adapters optional and avoid undocumented metadata keys.
6. Record source URLs, versions, access status and date; distinguish inspected documentation from suggestions. Link primary literature only after verifying bibliographic details. Keep source licenses separate from the original contribution's license.
7. Run repository skill validation, unit/scientific tests and examples actually affected. Evaluate trigger behavior with a configured runtime if available; otherwise report NOT_RUN and retain the cases for later use. Structural checks cannot prove scientific quality.
8. Request domain and statistical review appropriate to the scope. Record reviewer provenance and unresolved severity. Mark new skills experimental until transparent evidence supports stronger maturity.

## Validation and stops
Reject overlapping generic descriptions, examples that never call real tools, absent failure gates and references to nonexistent scripts. Stop claiming readiness if only metadata validation passed. Do not create empty skill folders to fill a taxonomy; record the capability in the roadmap.

## Outputs and interpretation
Produce the skill folder, reference notes, trigger/scientific fixtures, test evidence and change rationale. A skill is an instruction artifact; its tests support only the exercised behaviors and do not certify an agent's general performance.

## Examples and definition of done
Positive: add a donor-aware pseudobulk skill with a cell-as-replicate negative case and a small executed fixture. Negative: clone a generic “analyze the data” body into twenty assay names.
Done means a maintainer can identify input contracts, exact procedure, method boundaries, expected artifacts and falsifiable tests, with all unrun checks labeled.
