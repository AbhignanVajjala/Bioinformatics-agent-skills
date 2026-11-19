# Install Bioinformatics Agent Skills

This package contains the complete collection of Agent Skills, their bundled
method references, and the MIT [LICENSE](LICENSE). Every skill is experimental
and has no clinical validation. Scientific and high-stakes interpretations
require qualified human review.

## Install the collection in Codex

1. Extract the ZIP into the root of your Codex project. The extracted
   `.agents/skills/` folder should sit directly under the project root.
2. If your extractor creates a folder named after the ZIP, copy its entire
   `.agents` folder into your project root. Merge existing folders carefully,
   reviewing any filename conflicts.
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

## Scientific examples and full repository

Downloading and extracting these instruction files requires no Git clone or
Python installation. The agent host and any scientific software used for a
research task have their own requirements.

Executable scientific examples and shared resources outside the skills directory,
including schemas, templates, workflows, evaluation evidence, and development
tools, are available in the
[full repository](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills).
They are excluded from this lightweight skills package. Commands in the skill
instructions that refer to those resources require the full repository and its
documented dependencies.
