# Roadmap and maturity gates

## Phase 3 delivered scope and unfinished work

The active scope includes executable domain recipes, validator interfaces,
Quick/Full mode guidance, four additional domain skills and one universal distribution.
Execution evidence and exact limitations are in [Phase 3 status](phase3-status.md).
The variant-calling/interpretation, epigenomics, proteomics and workflow-engine
extensions from Milestone 3.5 remain NOT_IMPLEMENTED. Each needs a narrow
established-tool workflow, valid and invalid inputs, and independently reviewable
execution evidence before becoming a shipped skill.

Live public metadata retrieval, full pseudobulk differential-state modeling,
MOFA2/SNF, ranked enrichment and full binary format parsing remain NOT_RUN.
Real biological benchmarking and independent human review remain required.
The historical Phase 2 pilot remains provisional. New trigger/scientific cases
are separate NOT_RUN fixtures and have not been used to reinterpret that pilot.

The authoritative executed inventory is `implementation-status.md`. A file or a planned test below does not establish implementation. Current instructions and synthetic demonstrations are experimental.

## Next five priorities

1. Verify installation, discovery and invocation in named agent hosts and versions,
   with Codex as one example. Record actual evidence separately from vendor docs.
2. Use the existing evaluation harness under a fixed, reviewed protocol, preserving
   the provisional pilot judgments. The original 52 trigger/five scientific cases
   and new Phase 3 fixtures require genuine executions before effectiveness claims.
3. Obtain human reproduction and methodological review of the already executed
   pinned DESeq2/edgeR recipes. Review power, count provenance, contrasts, filtering
   and multiplicity before applying them to real studies.
4. Extend multi-omics and licensed organism SBML/FBC analyses only with explicit
   method scope, grouped validation, biological checks and negative controls.
5. Obtain independent biological validation and broader platform/native-runtime
   evidence. Existing Windows/Linux Python installs are distinct from agent-host
   discovery or scientific validation; macOS execution remains unverified.

Publication does not itself establish discovery, scientific validity or agent behavior.
Library expansion follows demonstrated reliability of the existing skills.

## P1 research capabilities

Dataset discovery requires access/terms verification, resolvable identifiers, checksum provenance and controlled-access refusal tests. Metadata validation needs alias collisions, reference mismatch, longitudinal units and exclusion-ledger fixtures. Statistical planning needs paired designs, missingness mechanisms, leakage and non-identifiability cases. Enrichment requires tested-universe and identifier-loss regressions. Visualization/reporting needs axes/uncertainty checks and artifact-grounded figure captions. Additional workflow documents for review, debugging and manuscript audit require end-to-end handoff examples and unresolved-blocker propagation.

## P2 domains and acceptance evidence

| Future domain | Evidence required before mature instructions |
|---|---|
| Genomics/variants | Reference-build/coordinate mismatch and germline/somatic controls; BAM/VCF parsing fixtures |
| Single-cell/spatial | Donor-level replication, doublets/ambient contamination, integration and pseudoreplication negatives |
| Proteomics | Identification FDR, peptide/protein ambiguity, missingness and batch sensitivity |
| Metabolomics | Annotation confidence, adduct ambiguity, drift and quantitative interpretation tests |
| Epigenomics | Peak/background controls, reference compatibility, replicate concordance |
| Cancer/survival | Censoring correctness, clinical confounders, purity and patient-level external validation |
| Microbial/metagenomics | Contamination, compositionality and database-version regressions |
| Structure/drug discovery | Structural provenance, decoy controls, docking uncertainty; reject efficacy claims |
| Metabolic engineering | Carbon/redox and growth-production tradeoffs with independent experimental validation plans |
| Phylogenetics/GWAS/scientific ML | Method-specific null controls, population structure/relatedness and leakage tests |

Workflow-engine integrations, containers, community benchmarks and wider persona coverage follow demonstrated use cases. No placeholder skill directories are shipped for this roadmap.
