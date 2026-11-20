# Installation and invocation

The collection follows the Agent Skills format: `SKILL.md` metadata/instructions
with relative references. Canonical sources remain in `.agents/skills/`.
Choose an agent host using the [compatibility matrix](agent-host-compatibility.md),
which records documented paths and unverified behaviors separately. The toolkit
also runs directly from a terminal without an agent host.

The universal ZIP contains all skills, executable Python validators, synthetic
examples and R recipes. [Toolkit installation](../TOOLKIT_INSTALL.md) uses an
isolated Python 3.12 environment. The optional
R/Bioconductor recipes have a separately pinned environment. Begin with
[START_HERE.md](../START_HERE.md) and the [skill index](../SKILL_INDEX.md).

Download the complete collection once:
[Bioinformatics-Agent-Skills-Complete.zip](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/raw/refs/heads/main/Bioinformatics-Agent-Skills-Complete.zip)
and follow [INSTALL.md](../INSTALL.md), also included inside the ZIP.
Extracting the package or copying `.agents/skills/` requires no Git clone,
Python or R installation. Keep the extraction intact for scientific execution.
The full repository setup below additionally supplies development tests and
evaluation infrastructure, which are excluded from the ZIP.

From the repository root, Python 3.11+ (tested: Linux x86_64, Python 3.12.14):

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev,examples]'
export XDG_CACHE_HOME="$PWD/.cache"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
python -m pip check
pytest -q
python scripts/validate_skills.py
python scripts/build_catalog.py --check
ruff check .
ruff format --check .
python examples/bulk-rnaseq/run.py --output artifacts/bulk-rnaseq
python examples/multiomics/run.py --output artifacts/multiomics
python examples/metabolic-modeling/run.py --output artifacts/metabolic-modeling
python scripts/run_evals.py --output evals/reports/latest.json
```

Writable cache directories are needed when the platform home is read-only; COBRApy and
Matplotlib use them. On Windows use .venv\Scripts\Activate.ps1 and PowerShell environment
assignments. Windows validation and native dependency limits are recorded in
the implementation status; macOS execution remains unverified. No GPU, credentials,
private data or external services are needed after dependencies are installed.

`pip install -e '.[dev]'` installs core validators without the optional scientific examples.
COBRApy uses the GLPK binding supplied by swiglpk, not a proprietary solver license.
Direct versions are pinned in pyproject.toml; requirements-tested.txt captures the tested
transitive environment. To reproduce it, install with
`python -m pip install -r requirements-tested.txt` then `python -m pip install -e . --no-deps`.
This is a tested environment snapshot, not a cross-platform or hashed artifact lock.

## Agent-host setup

Use [INSTALL.md](../INSTALL.md) for instruction-only copying. Other hosts may
require a different directory or selector; preserve the complete skill folder
and references. Format compatibility alone does not establish discovery or
scientific instruction-following. Consult the [host matrix](agent-host-compatibility.md).

### Codex example

Open this repository as the working directory. Canonical instruction folders are in
`.agents/skills/<name>/SKILL.md`. Ask, for example:

- `$bulk-rnaseq-differential-expression audit these counts and sample metadata before modeling.`
- `$multiomics-integration reconcile specimen identities and check subject-level leakage.`
- `$genome-scale-metabolic-modeling inspect media and objective before interpreting FBA.`

If the host does not discover skills, explicitly ask it to read the corresponding
SKILL.md and follow its linked references; do not imply auto-discovery was tested.
Keep this checkout intact: shared references and examples may be outside individual
skill folders. A copied single folder alone is not a tested full installation.
Metadata follows the retrieved Agent Skills specification. Actual Codex discovery and
model-driven trigger behavior remain NOT_TESTED in this execution session.

The bundled R/Bioconductor differential-expression recipes use a separate pinned
installation and have executed synthetic CI evidence. This Python quick start
does not run them. MOFA/SNF fitting remains NOT_RUN. Do not describe RNA-seq QC
as DESeq2 results.
