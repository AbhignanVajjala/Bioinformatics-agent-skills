# Bioinformatics Agent Skills

An experimental library of original, portable research instructions with executable
scientific readiness gates. It helps agents choose methods, detect invalid inputs,
record evidence and limit conclusions. It is not clinical software or a validated
replacement for scientific tools or expert review.

## What exists

- **13 Agent Skills:** ten engineering/research foundations plus bulk RNA-seq,
  multi-omics and genome-scale metabolic modeling guidance. [Generated catalog](docs/catalog.md).
- **Three executable synthetic examples:** RNA-seq QC/design readiness, paired-assay
  reconciliation/descriptive concordance, and COBRApy/GLPK FBA/pFBA/FVA with sensitivity
  and infeasibility controls.
- **Scientific gates and evaluation:** input identity, counts, independent replication,
  design rank, subject leakage, objective/bounds and solver checks. Seven deterministic
  scientific evaluation scenarios and five unexecuted agent-review scenarios.
- **Seven artifact schemas/templates**, four operational [personas](personas/biostatistician.md)
  and three staged [workflows](workflows/README.md). Role instructions do not spawn reviewers.

All skills have experimental maturity. See [implementation status](docs/implementation-status.md)
for actual commands, test evidence, exact inventory and unfinished work.

## Quick start

From this checkout, Python 3.11+:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,examples]'
export XDG_CACHE_HOME="$PWD/.cache"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
pytest -q
python scripts/validate_skills.py
python scripts/build_catalog.py --check
python examples/bulk-rnaseq/run.py --output artifacts/my-first-bulk-run
python examples/multiomics/run.py --output artifacts/my-first-omics-run
python examples/metabolic-modeling/run.py --output artifacts/my-first-model-run
python scripts/run_evals.py --output artifacts/my-evaluations.json
```

Example output directories must be empty or new. Each run writes data/model fixtures,
scientific results, a five-level validation report, claim ledger and provenance with
input/output hashes, software versions and actual commands. Input fixtures are synthetic;
no private datasets or paid APIs are used. See [installation](docs/installation.md) for
reproduction constraints, optional dependencies, lint checks and platform limitations.

Open this repository in Codex and request, for example:

> `$bulk-rnaseq-differential-expression` audit my counts, sample identities and design before choosing a model.

> `$genome-scale-metabolic-modeling` inspect media, objective and feasibility before interpreting predicted flux.

Canonical instructions are under `.agents/skills`. Metadata was checked against the
retrieved official Agent Skills specification. Codex runtime discovery and the 52 supplied
trigger prompts have not been evaluated with a configured agent runtime. Explicitly reading
a skill's SKILL.md is the fallback; keep the complete checkout for shared references.

## Scientific limits

RNA-seq demonstration output is **QC/readiness, not differential expression**: no R,
DESeq2, edgeR or limma model was run. Multi-omics demonstration output is matched-sample
exploration, not a fitted MOFA/SNF model or validated predictor. Metabolic outputs are
steady-state predictions in an intentionally tiny synthetic model, not measured biological
flux or a real genome-scale organism model. Integer-looking values cannot prove raw-count
provenance. Declared specimen IDs cannot prove biological identity. Two replicates per
condition pass a minimum gate, not a power or adequacy assessment.

Automated checks are separate from biological interpretation and human review. No clinical
validity, peer-review status, novelty or model-performance improvement is claimed.
Read the [scientific integrity rules](docs/scientific-integrity.md) and [roadmap](docs/roadmap.md).

## Layout

```text
.agents/skills/     canonical instructions and domain references
src/bioskills/     deterministic scientific gates and provenance helpers
examples/         bulk-rnaseq, multiomics, metabolic-modeling
schemas/          seven JSON Schema contracts
templates/        example artifacts and authoring template
personas/         four bounded review roles
workflows/        three staged scientific procedures
tests/            structural, unit, scientific and CLI integration tests
evals/            trigger/scientific cases, rubrics and actual run evidence
scripts/          skill validation, catalog generation, evaluation runner
docs/             design, standards, installation, status and roadmap
.github/          CI, contribution and issue templates
```

## Sources, licensing and contribution

Original repository code, instructions and synthetic fixtures use the [MIT license](LICENSE).
The uploaded reference archive has no verified redistribution license; none of its skill
bodies or assets were republished. [Reference analysis](docs/reference-analysis.md) records
architecture choices and license uncertainty. This is not an official Aava product and
claims no affiliation with nf-core or GA4GH. External software retains its own licenses.

Contribute meaningful valid/invalid fixtures and documented assumptions; see
[CONTRIBUTING](CONTRIBUTING.md), [authoring guide](docs/authoring-guide.md),
[security policy](SECURITY.md) and [citation metadata](CITATION.cff).
