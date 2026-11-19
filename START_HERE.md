# Start here

All skills are experimental and require qualified review for high-stakes
interpretations. Complete refers to this shipped collection.

Download **Bioinformatics-Agent-Skills-Complete.zip**. This single universal
archive contains all 17 skills, every reference, the Python toolkit, synthetic
examples, schemas, templates and runnable R/Bioconductor recipes.

For instructions only, extract the archive and copy `.agents/skills/` into your
agent project, following [INSTALL.md](INSTALL.md). Reading and installing the
instructions needs no Python or R.

For execution, keep the same extraction intact, open a terminal at its root and
follow [TOOLKIT_INSTALL.md](TOOLKIT_INSTALL.md). The toolkit uses Python 3.12 for
its pinned scientific dependencies and optional
R 4.4.3/Bioconductor 3.20 for count-model fitting.

Select a skill by folder name or explicit invocation, for example
`$bulk-rnaseq-differential-expression`. See the [skill index](SKILL_INDEX.md).
Discovery and invocation depend on the agent host.

Use QUICK for a bounded question or inspection. It keeps essential checks in
the response and creates no mandatory artifacts. Request FULL for reproducible
execution, an audit or a benchmark. FULL records commands, versions, input hashes,
outputs, assumptions and limitations. Both modes preserve scientific safeguards.

The agent follows instruction files and calls available software. Actual
implementation scope varies by skill. A successful command cannot establish
biological validity. BLOCKED indicates a missing dependency or unresolved
prerequisite. NOT_RUN means the relevant computation or assessment did not execute.

For the bundled first-use example, install its dependencies and run
`python examples/expanded/run.py --output first-use-output` from its root.
It executes synthetic pseudobulk aggregation, Fisher/BH over-representation
analysis and FASTQ inspection. It makes no public data request and fits no
differential-state model.

Bulk RNA-seq fitting uses the pinned R packages. Metabolic analysis needs
COBRApy/GLPK. Cross-view analysis uses NumPy/pandas. ORA needs SciPy. Binary
genomics and H5AD parsing require optional external parsers. Consult each skill's
input contract and recipes before execution.
