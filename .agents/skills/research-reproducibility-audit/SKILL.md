---
name: research-reproducibility-audit
description: "Audit and rerun research artifacts using exact inputs, environments, parameters and provenance; use before handoff or release, not to certify biological validity from repeatable output alone."
metadata:
  maturity: experimental
---

# Research reproducibility audit

## Execution modes

Use QUICK for bounded questions and FULL for explicitly requested reproducible
work. Follow the [mode policy](references/modes.md). Named output lists below
apply to FULL execution when relevant. Essential safeguards apply in both modes.


## Inputs and preflight
Require source revision or source hashes, original input manifests, environment/lockfiles, parameter sets, seeds, actual commands, output artifacts and exclusions. Check data/software licenses and access permissions before arranging a rerun. Do not retrieve controlled data or expose credentials merely to complete an audit.

## Method selection and procedure
1. Construct a provenance graph from each reported result to input hashes, transformation steps and software. Include reference genome/annotation, model version, database release and identifier mapping where applicable.
2. Inspect input availability separately from authority: an accession may resolve but not identify the exact release; a private dataset may be legitimate but unavailable to the reviewer. Report these as distinct limitations.
3. Recreate the declared environment using pinned versions or record where resolution is not exact. Capture interpreter, scientific packages, solver and operating system. Floating container tags and unversioned databases are reproducibility risks.
4. Execute the documented command in a clean output directory. Record start/end timestamps, exit status, commands and hashes. A nonzero command must not be hidden by a logging pipeline. Never overwrite user data to reproduce a run.
5. Compare expected invariant outcomes. Use exact hashes for deterministic text/data, numerical tolerances justified by method/solver for floating point, and label-equivalence rather than raw order for arbitrary cluster labels. Predetermine tolerances rather than widen them until tests pass.
6. Audit preprocessing, exclusions, random seeds, feature selection, fold assignment and multiple-testing universe. Confirm train/test separation includes imputation, scaling and tuning.
7. Report technical repeatability, independent reproducibility and scientific validity separately. Reviewer access to the same cached output is not a rerun; a shared environment limits independence.

## Validation and stops
Verify checksums before accepting cached artifacts and ensure outputs are fresh for the selected target. Stop a reproducibility claim if input versions or commands cannot be recovered. Preserve honest PARTIAL/BLOCKED explanations in the narrative and use the project's validation statuses per check. Do not invent a Git commit in an unborn repository.

## Outputs and interpretation
Produce `reproducibility-audit.md`, an executed `analysis-run.json`, output comparisons, and `handoff.json`. Include missing prerequisites and exact next commands. Repeatability alone cannot rescue a confounded or biologically inappropriate analysis.

## Examples and definition of done
Positive: independently rerun a synthetic metabolic fixture and compare objective and mass-balance residuals within a fixed tolerance. Negative: call a screenshot reproducible because it visually matches an earlier plot.
Done means each requested rerun has executed evidence or a precise blocker, every comparison has a documented criterion, and the independence of the audit is stated.
