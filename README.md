# Download the Complete Bioinformatics Agent Skills Collection

**[Download Bioinformatics-Agent-Skills-Complete.zip](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/raw/refs/heads/main/Bioinformatics-Agent-Skills-Complete.zip)**

One ZIP includes all **17 experimental Agent Skills**, executable scientific
validators, bioinformatics recipes and examples, the Python scientific toolkit,
R/Bioconductor analysis recipes, and installation and selection guides.
No Git clone is required.

Users who only need Agent Skills can copy the `.agents/skills/` folder without
installing scientific dependencies. Users who want to execute analyses can
install the optional scientific toolkit dependencies from the same archive.

The ZIP includes Python sources and runnable R recipes, with their dependency
manifests, schemas and MIT license. External scientific runtimes require explicit
installation. Evaluation evidence and development tools remain in the full
repository. Complete refers to the shipped collection, with no claim of complete
bioinformatics coverage. All skills remain experimental and have no clinical
validation. Start with [START_HERE.md](START_HERE.md),
[SKILL_INDEX.md](SKILL_INDEX.md), [INSTALL.md](INSTALL.md) or
[TOOLKIT_INSTALL.md](TOOLKIT_INSTALL.md). Verify the archive with [SHA256SUMS](SHA256SUMS).

## Bioinformatics Agent Skills

An experimental library of original, portable research instructions with executable
scientific readiness gates. It helps agents choose methods, detect invalid inputs,
record evidence and limit conclusions. It is not clinical software or a validated
replacement for scientific tools or expert review.

## What exists

- **17 Agent Skills:** ten foundation/maintainer skills and seven domain skills
  covering bulk RNA-seq, multi-omics, metabolic modeling, donor-aware pseudobulk,
  public metadata retrieval, enrichment and file-format inspection.
  [Generated catalog](docs/catalog.md).
- **Three executable synthetic examples:** RNA-seq QC/design readiness, paired-assay
  reconciliation/descriptive concordance, and COBRApy/GLPK FBA/pFBA/FVA with sensitivity
  and infeasibility controls.
- **Scientific gates and evaluation:** input identity, counts, independent replication,
  design rank, subject leakage, objective/bounds and solver checks. Seven deterministic
  scientific evaluation scenarios and five unexecuted agent-review scenarios.
- **Executable additions:** pinned DESeq2/edgeR synthetic fits, SBML/GPR and
  flux controls, descriptive cross-view association, pseudobulk aggregation,
  Fisher/BH ORA and public metadata plans. The original demonstrations retain
  their original scope.
- **Scientific validator CLI:** run `python -m bioskills --help` after
  installation. [Commands and reporting contracts](docs/validators.md).
- **Eight artifact schemas/templates**, four operational [personas](personas/biostatistician.md)
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

Canonical instructions are under `.agents/skills`. QUICK answers bounded
questions with essential checks. FULL supports explicitly requested reproducible
execution and evidence. The historical pilot recorded ten executions with
provisional 0 PASS, 4 FAIL and 6 BLOCKED. New Phase 3 behavioral cases are NOT_RUN.
See [Phase 3 execution status](docs/phase3-status.md) for exact tested scope.

## Scientific limits

The original RNA-seq demonstration remains **QC/readiness**. Separate pinned
R recipes execute actual DESeq2 and edgeR fits on synthetic data. The original
multi-omics demonstration output is matched-sample
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
