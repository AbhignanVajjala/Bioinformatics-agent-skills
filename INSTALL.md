# Install Bioinformatics Agent Skills

The single universal `Bioinformatics-Agent-Skills-Complete.zip` contains all
17 Agent Skills and their references, the executable Python toolkit, synthetic
examples, R/Bioconductor recipes, schemas, templates, dependency manifests,
the [skill index](SKILL_INDEX.md), [first steps](START_HERE.md), release information
and the MIT [LICENSE](LICENSE). Every skill is experimental
and has no clinical validation. Scientific and high-stakes interpretations
require qualified human review.

## Install the collection in Codex

1. Extract the ZIP into a new directory. No Python or R installation is needed
   to read or install the instructions.
2. Copy its `.agents/skills/` folder into your Codex project's `.agents/skills/`.
   The result must be `.agents/skills/<skill-name>/SKILL.md` under the project
   root. Merge existing folders carefully, reviewing any filename conflicts.
3. Open that project in Codex. Check the available skills, then select a skill
   by name or request it explicitly in your prompt, for example:

   > `$bulk-rnaseq-differential-expression` audit my counts, sample identities,
   > and design before choosing a model.

You can also request `$multiomics-integration` or
`$genome-scale-metabolic-modeling`. Folder names under `.agents/skills/`
identify the other skills. If skills do not appear, restart Codex and check
that your file manager copied the hidden `.agents` folder. You may explicitly
ask the agent to read the relevant `SKILL.md` and its linked references.
[Codex skill discovery](https://learn.chatgpt.com/docs/build-skills).

## Use individual skills with other tools

Copy an entire `.agents/skills/<skill-name>/` folder, including its
`references/` directory when present, to the skill location documented by
your agent host. Keep `SKILL.md` and the relative reference paths together.
Retain this MIT license with redistributed copies. Follow your host's guidance
for enabling and selecting a skill.
[Agent Skills format](https://agentskills.io/specification).

Compatibility, available tools, explicit invocation syntax, and automatic
discovery depend on the agent host. Inspect what your host loads and adapt
installation paths as needed.

## Execute scientific workflows from the same ZIP

Downloading and extracting these instruction files requires no Git clone or
Python installation. The agent host and any scientific software used for a
research task have their own requirements.

Keep the extracted archive intact and open a terminal at its root, alongside
`pyproject.toml`. Follow [TOOLKIT_INSTALL.md](TOOLKIT_INSTALL.md) to create an
isolated environment, install dependencies and run the first-use demonstration
or [validator CLI](docs/validators.md). All bundled scientific commands resolve
from that root. Copying only the skill folders does not copy executable resources;
use the complete extraction when running those commands.

Python 3.12 is recommended for the pinned scientific dependencies. COBRApy needs
working GLPK/libsbml native dependencies. DESeq2 and edgeR require the separately
installed, pinned R/Bioconductor environment. No interpreter, binary library or
external data is silently installed or downloaded by extraction.

Development tests, evaluation reports, personas, staged workflow instructions and
repository maintenance scripts remain in the
[full repository](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills).
