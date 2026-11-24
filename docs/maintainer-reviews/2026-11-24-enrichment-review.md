# Pathway enrichment and identifier mapping maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Human-directed maintainer self-review with
ChatGPT-assisted scripts in Codespaces, not independent external peer review.
Independent methodological and biological validation remain incomplete.

## Supplied historical evidence

Source `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2, November 24,
2026. Environment: Python 3.12.3, NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3.
Original directories: `artifacts/my-combined-domain-audit-qAgil0` and
`artifacts/my-final-domain-audit-9j6Ml3`. Original files are unavailable here;
no original hashes or execution records are reconstructed. The supplied first
batch was 51 checks (26 PASS/16 INVESTIGATE/9 ASSESS); the second was 49
(18/19/12). Combined **100: 44 PASS/35 INVESTIGATE/21 ASSESS** across four
skills, not per-skill totals, accuracy rates or distinct defect counts.
Assessment-only cases also exposed confirmed numerical defects.

Whitespace database/release, blank/whitespace/numeric pathway IDs, numeric
database ID and numeric mapping target were accepted; missing tested raised
KeyError. Numeric target changed overlap **5 to 4**, p **0.00006449948400412796
to 0.0010319917440660474**. This is identifier validation failure, not incorrect
Fisher arithmetic. Empty/outside-universe sets returned p=1 and counted in BH;
a family with no eligible member could claim execution. Duplicate memberships
were correctly counted/deduplicated and empty selected lists rejected.

Preserved gates reject selected genes outside the tested universe, selected-only
backgrounds under the scoped policy, incomplete mappings, duplicate targets and
reference mismatches. No namespace conversion or invented mappings is introduced.

The independently calculated baseline probability is **1/choose(20,5) =
0.00006449948400412796**, BH q **0.00012899896800825592** for two eligible
pathways; null p=q=1. The supplied independent 20-pathway comparison used integer
combinations/manual BH: Fisher/BH agreement True/True, maximum p difference
1.1102230246251565e-16 and q difference 0.0. These are mathematical synthetic
checks, not empirical pathway validation.

## Correction and regression evidence

[ORA](../../src/bioskills/enrichment.py) validates structure/declarations/exact
string identities before mapping. Shared serialized boundaries reject duplicate
JSON keys. Eligibility is prespecified **>=1 tested-universe member**, independent
of selected overlap or p-value. Invalid records reject; valid empty/outside sets
are audited exclusions; eligible zero-overlap sets stay in BH. No eligible sets
returns NO_TESTABLE_PATHWAYS / analysis NOT_RUN.

| Criterion | New evidence / acceptance condition |
|---|---|
| Structure/types | Missing keys, numeric/blank declarations/IDs and malformed records produce controlled errors |
| Family | Supplied/eligible counts, sizes, duplicates, exclusions and actual BH denominator recorded |
| Null pathways | Eligible zero-overlap pathways remain tested; no p-dependent exclusion |
| Arithmetic | Exact combination tails plus manual BH independently compared for 20 synthetic sets |
| Identity chain | Leading-zero/long DE IDs retained through explicit one-to-one mapping |

Automated regressions: tests/test_enrichment_integrity.py and
 tests/test_domain_integration.py. Native DE outputs are generated in pinned R CI,
not fabricated for ordinary offline tests. Commands/counts are in
[implementation status](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/implementation-status.md). Ranked enrichment is
**NOT_RUN**; association does not establish pathway activation, causality or
clinical utility. Universe suitability, annotation quality and dependency
assumptions require independent methodological review.

Primary calculation references: [SciPy 1.15.3 Fisher exact](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.fisher_exact.html)
and [BH implementation](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.stats.false_discovery_control.html)
(previously consulted).
