---
name: research-task-decomposition
description: "Convert an accepted scientific plan into dependency-ordered tasks with evidence gates, resource budgets and recovery; use for multistage analyses, not to split dependent patient data across train and test or bypass unresolved design problems."
metadata:
  maturity: experimental
---

# Research task decomposition

## Inputs and preflight
Obtain the research specification, immutable input locations, access restrictions, environment, compute budget and intended deliverables. Identify missing design decisions before scheduling. A decomposition cannot repair an invalid estimand or establish dataset access rights.

## Method selection and procedure
1. Map dependencies from input integrity through computation, statistical diagnostics, interpretation and reporting. Example: sample identity validation precedes count/design validation, which precedes DE, which precedes enrichment with the tested-gene background.
2. For each task write a contract: ID, scientific question, required input hashes, owner role, tools/version, output paths, gate, resource ceiling, recovery and downstream consumers. Choose a unit small enough to rerun without recomputing unrelated stages.
3. Parallelize only tasks with immutable shared inputs and distinct outputs. Independent assay QC can run concurrently; preprocessing learned from data must stay inside its training fold. Parallelism must not break subject grouping or use held-out outcomes.
4. Estimate storage, memory and runtime from data dimensions. Start with a small licensed fixture; use bounded workers. Do not silently launch paid compute or download large controlled-access resources.
5. Treat gate failure as a dependency failure. If sample mapping fails, block integration and interpretation instead of scheduling them on partial guessed joins. Preserve unaffected validated tasks and record what was invalidated.
6. Define retries by diagnosis: malformed input needs repair and a new input version; unsupported solver needs environment correction; an unidentified treatment effect needs design reconsideration, not repeated execution.
7. Integrate outputs by their declared contracts. Record stage status PASS, WARN, FAIL, BLOCKED or NOT_RUN and the actual artifact; never collapse a critical failure into a mean readiness score.

## Validation and stops
Check the dependency graph is acyclic and that every consumer has an existing validated producer. Inspect planned output collisions and non-idempotent operations. Stop scheduling a downstream claim when its source computation is stale, failed or unrun. Ask for permission only where a task requires an external/destructive action not already authorized.

## Outputs and interpretation
Produce `task-graph.json`, `task-contracts.md`, and `handoff.json`. A completed task means its acceptance check ran and the evidence is available; the number of completed tasks says nothing about scientific merit.

## Examples and definition of done
Positive: split a multi-omics study into identity audit, independent assay QC, integration selection, grouped evaluation and evidence review. Negative: run enrichment first because DE is slow and fill gene identifiers later.
Done means every task has inputs, outputs, a measurable gate and a safe recovery path. Evaluate a failed upstream identity check and confirm downstream integration remains BLOCKED rather than PASS.
