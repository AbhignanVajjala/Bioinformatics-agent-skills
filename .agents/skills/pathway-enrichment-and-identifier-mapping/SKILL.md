---
name: pathway-enrichment-and-identifier-mapping
description: "Execute scoped over-representation analysis with an eligible tested universe, audited gene mapping and multiple-testing control; use for pathway associations, not selected-only backgrounds or causal pathway activation claims."
metadata:
  maturity: experimental
---

# Pathway enrichment and gene identifier mapping

## Execution modes

Use QUICK for bounded questions and FULL for reproducible execution. Follow the
[mode policy](references/modes.md). Essential safeguards apply in both modes.

## Inputs and preflight

Selected/tested identifiers, source-to-target mappings, organism, annotation release and versioned gene sets.

## Method selection and procedure

1. Define ORA versus ranked enrichment before analysis. For ORA, require a selected
   list, eligible tested-gene universe, organism, annotation release and gene-set
   database/version. Preserve upstream ranking unchanged if it exists.
2. Audit source-to-target mappings. The implemented baseline requires one-to-one
   complete mapping. Record dropped or ambiguous IDs and resolve them under a
   separate policy before using it. Reject duplicate input IDs and selected-only
   universes.
3. Use SciPy Fisher exact tests for over-representation. Intersect gene-set
   membership with the tested universe, record duplicate memberships, and apply
   BH across the entire supplied pathway family.
4. Export overlap counts, raw p-values, adjusted p-values, family size, mapping
   policy and database release. Review the appropriateness of BH dependence
   assumptions for the research question.
5. Report pathway associations with uncertainty. Enrichment alone does not prove
   pathway activation, mechanism, causation or clinical utility. Ranked enrichment
   requires a separately executed established tool and remains NOT_RUN here.

## Validation and evidence

Stop dependent analysis for failed input, identity, scale or design gates.
Record actual execution status and preserve inputs. Obtain qualified human
methodological review before high-stakes interpretation. All fixtures are synthetic.

## Recipes and limitations

Read the [input contract](references/input-contract.md),
[recipes](references/recipes.md) and [troubleshooting](references/troubleshooting.md).

Example invocation follows.

> $pathway-enrichment-and-identifier-mapping audit the tested universe and mappings, then run ORA with pathway FDR.
