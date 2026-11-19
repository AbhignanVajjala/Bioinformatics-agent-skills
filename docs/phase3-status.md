# Phase 3 implementation and execution status

All skills remain EXPERIMENTAL. Historical Phase 2 observations retain their
original verdicts. Status entries below describe capabilities separately from
biological or clinical validation.

| Capability | Implementation state | Reporting state | Evidence |
|---|---|---|---|
| Pinned DESeq2 and edgeR count-model recipes | IMPLEMENTED_NOT_EXECUTED | NOT_RUN until CI results are verified | R 4.4.3 / Bioconductor 3.20 job and synthetic positive/negative checks |
| SBML/GPR metabolic recipe | IMPLEMENTED_NOT_EXECUTED | BLOCKED locally by libsbml import policy | Linux execution pending |
| Cross-view multi-omics baseline | IMPLEMENTED_AND_TESTED | PASS for the synthetic descriptive baseline | Local recipe and nine Python checks executed |
| Validator CLI, Quick/Full modes and expanded skills | NOT_IMPLEMENTED | NOT_RUN | Subsequent dependency-ordered milestones |
| Dual distribution and first-use toolkit | NOT_IMPLEMENTED | NOT_RUN | Existing lightweight archive remains available |

IMPLEMENTED_AND_TESTED maps to PASS only for the executed scope.
IMPLEMENTED_NOT_EXECUTED maps to NOT_RUN. OPTIONAL_DEPENDENCY_MISSING maps to
BLOCKED. EXPERIMENTAL describes maturity, independently of execution status.
NOT_IMPLEMENTED maps to NOT_RUN. Any scientific gate failure remains FAIL.

The R recipe pins primary package versions and rejects other versions at run
time. Its transitive installed dependency inventory is recorded in sessionInfo.
This is a versioned release environment, with no claim that every transitive
dependency has a content-addressed lock.

Remaining scientific work includes external biological validation, reviewed
normalization and missingness assumptions, real licensed organism models and
independent human methodological review.

Local checkpoint commands used the existing Python 3.12.10 environment:
`pytest -q --junitxml artifacts/phase3/m31.xml` gave 133 passed and 10 skipped.
The skips include eight existing COBRA-dependent tests and two new ones because
Windows Application Control blocks libsbml. The multi-omics recipe executed at
`artifacts/phase3/multiomics`. Skill validation, catalog and package checks pass.
Milestone 3.1 remains pending the R/Bioconductor and Linux metabolic CI evidence.
