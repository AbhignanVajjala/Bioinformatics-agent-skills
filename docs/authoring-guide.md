# Authoring and reviewing skills

Start with one scientific decision that an agent can get wrong. Write one valid case and one dangerous near-neighbor before writing instructions. Prefer a decision rule with explicit inputs to an open-ended request to “analyze” a modality.

1. Create `.agents/skills/<lowercase-hyphenated-name>/SKILL.md` using the template below. Name and directory must agree. State both trigger and exclusion in the description.
2. Define data provenance, organism/reference, experimental unit, question and resource limits. Distinguish optional context from information without which an analysis is not identifiable.
3. Write an ordered procedure with tool selection, assumptions, checks, stop/recovery rules and named artifacts. Deep supporting content belongs in `references/`; avoid copying the constitution into every file.
4. Add trigger cases and scientific negatives. An instruction-only case is NOT_RUN until an agent actually attempts it. Deterministic validators test code behavior, not model compliance.
5. Run structural checks and applicable tests/examples. Record exact command, result and limitations in the implementation status. Review licenses and source provenance before incorporating outside material.
6. Obtain domain and statistical review for maturity promotion. An author self-check or additional agent review must be labeled accurately.

## Original starter template

```markdown
---
name: chosen-skill-name
description: Use for a specific scientific task under named assumptions; exclude the most plausible inappropriate task.
metadata:
  maturity: experimental
---
# Scientific task
## Required inputs and preflight
Record context, permissions, units, versions, resources and missing prerequisites.
## Method selection and procedure
Give concrete conditional decisions and commands with explicit working directories.
## Validation and stop conditions
Specify input, computation, statistical, interpretation and provenance evidence.
## Output contract and interpretation
Name artifacts and the strongest supported claim; state what remains unknown.
## Examples and evaluation
Give valid and misleading cases, expected behavior and measurable completion criteria.
```

Maturity is experimental until documented review exists. `reviewed` requires recorded domain/methodological reviewers and resolved critical findings. `validated` additionally requires a stated scope, reproducible representative benchmarks and regression evidence; it does not mean clinical certification. No maturity label applies outside its evaluated scope.
