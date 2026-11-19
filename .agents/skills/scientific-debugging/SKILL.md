---
name: scientific-debugging
description: "Diagnose reproducible scientific pipeline failures in formats, metadata, design, numerical computation or interpretation; use on unexpected errors or inconsistent results, not to tune analyses until they become significant."
metadata:
  maturity: experimental
---

# Scientific debugging

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Inputs and preflight
Collect the exact failing command, exit status, input hashes, environment/solver versions, expected behavior and actual output. Redact sensitive identifiers from logs without destroying join information. Preserve inputs and failing artifacts; reproduce in a new output directory.

## Method selection and procedure
1. Classify the first failed layer: parsing/integrity, computation, statistical identifiability, biological interpretation or provenance. A downstream empty plot may originate in an earlier sample mismatch rather than plotting code.
2. Reproduce the failure on the smallest subset that preserves the scientific dependency. For pairing, keep complete donor pairs; for rank deficiency, retain the design structure; for metabolic infeasibility, preserve the constraints causing it.
3. Test one explicit hypothesis at a time. Examples: count columns and metadata order differ; a covariate duplicates treatment; proteomics uses log2 units while another table has raw intensity; exchange lower bounds close the carbon source.
4. Inspect data types, dimensions, missingness, duplicate IDs, units and reference versions before changing algorithms. For regression check rank and residual degrees of freedom. For solvers inspect status, feasibility tolerances, objective and bounds before reading flux values.
5. Apply the smallest supported correction. Save a transformation/mapping record; do not silently relabel samples, round TPM to counts, drop awkward subjects or relax constraints solely to obtain the desired outcome.
6. Add a regression case for the original failure plus a valid control. Rerun affected downstream stages with new provenance and compare intended invariants, not only exit codes.
7. Explain scientific ramifications: changing sample mapping or a design formula changes the estimand; fixing a file delimiter may not. Mark previous outputs invalid where needed.

## Validation and stops
A disappearing exception is insufficient if the scientific failure remains. Halt when repair requires unverifiable identities, irrecoverable confounding or an unsupported method. Escalate a disagreement about biological plausibility rather than deleting unusual but valid observations. Never retry unchanged operations indefinitely or disable TLS/checksum verification to obtain dependencies.

## Outputs and interpretation
Produce `failure-reproduction.md`, the minimal synthetic reproducer where possible, `diagnosis.md`, regression evidence and a list of invalidated outputs. Keep failed attempts and successful corrections distinct.

## Examples and definition of done
Positive: diagnose FBA infeasibility by comparing medium uptake bounds with a forced biomass lower bound, retaining the infeasible case in tests. Negative: remove a batch covariate until a treatment p-value becomes small.
Done means the causal failure hypothesis has evidence, the regression fails on the broken case and passes on the corrected case, and downstream consequences are documented. An unexplained intermittent success remains unresolved.
