"""Generate the skill index from canonical metadata."""

import argparse
import json
from validate_skills import ROOT, parse_skill


def render():
    lines = [
        "# Skill catalog",
        "",
        "All skills are experimental; structural checks do not establish agent reliability.",
        "",
        "| Skill | Trigger |",
        "|---|---|",
    ]
    for path in sorted((ROOT / ".agents/skills").glob("*/SKILL.md")):
        meta = parse_skill(path)
        lines.append(
            f"| [{meta['name']}](../{path.relative_to(ROOT).as_posix()}) | {meta['description'].replace('|', '/')} |"
        )
    return "\n".join(lines) + "\n"


def render_index():
    release = json.loads((ROOT / "RELEASE.json").read_bytes())
    lines = [
        "# Skill selection index",
        "",
        f"Collection {release['version']}. All skills are EXPERIMENTAL. "
        "Execution status is scoped to the capability, with independent human review pending.",
        "",
        "| Skill and task | Required inputs | Tools and runtime | Example invocation | Capability status and executable scope |",
        "|---|---|---|---|---|",
    ]
    implemented = {
        "bulk-rnaseq-differential-expression": (
            "Counts, subject metadata and design",
            "Pinned R/DESeq2/edgeR",
            "Synthetic model fitting and Python readiness",
        ),
        "genome-scale-metabolic-modeling": (
            "SBML/FBC, objective, medium and model context",
            "Python/COBRApy/GLPK",
            "SBML, FBA/pFBA/FVA and perturbations",
        ),
        "multiomics-integration": (
            "Assay matrices, specimen maps, declared scales and feature map",
            "Python/NumPy/pandas",
            "Descriptive cross-view association",
        ),
        "single-cell-rnaseq-pseudobulk": (
            "Raw gene-by-cell counts and cell/specimen/donor mapping",
            "Python/NumPy/pandas",
            "Pseudobulk sums and readiness; differential state NOT_RUN",
        ),
        "public-bioinformatics-data-retrieval": (
            "Source, public accession and metadata intent",
            "Python urllib, optional public network",
            "Metadata client with mocked tests; live retrieval NOT_RUN",
        ),
        "pathway-enrichment-and-identifier-mapping": (
            "Selected/tested IDs, mapping, organism and versioned gene sets",
            "Python/SciPy",
            "Fisher ORA plus BH; ranked enrichment NOT_RUN",
        ),
        "bioinformatics-file-formats": (
            "File and declared reference/context",
            "Python, optional external binary parsers",
            "Text inspection and signatures; full binary parsing NOT_RUN",
        ),
    }
    foundation_inputs = {
        "bioinformatics-skill-authoring": "Capability boundary, sources and valid/invalid fixtures",
        "research-reproducibility-audit": "Exact inputs, environment, commands, hashes and prior outputs",
        "research-specification": "Research question, experimental units, conditions and covariates",
        "research-task-decomposition": "Accepted plan, dependencies, evidence gates and resources",
        "scientific-agent-orchestration": "Task graph, permissions, runtime and reviewer provenance",
        "scientific-context-engineering": "Session state, dataset manifest, decisions and handoff",
        "scientific-debugging": "Failing command, immutable inputs, versions and expected behavior",
        "scientific-prompt-engineering": "Task, source corpus, output fields and abstention contract",
        "source-grounded-scientific-reasoning": "Claims, sources, organism and verified identifiers",
        "verification-before-scientific-claims": "Proposed claims, methods and actual evidence artifacts",
    }
    for path in sorted((ROOT / ".agents/skills").glob("*/SKILL.md")):
        meta = parse_skill(path)
        name = meta["name"]
        inputs, tools, scope = implemented.get(
            name,
            (
                foundation_inputs.get(name, "Research question and applicable evidence"),
                "Agent host and task-specific tools",
                "Instruction workflow; behavioral effectiveness unverified",
            ),
        )
        state = (
            "IMPLEMENTED_AND_TESTED (scoped synthetic or mocked checks)"
            if name in implemented
            else "EXPERIMENTAL (instruction workflow)"
        )
        task = meta["description"].replace("|", "/")
        lines.append(
            f"| [{name}](.agents/skills/{name}/SKILL.md) — {task} | {inputs} | {tools} | "
            f"`$" + name + f"` | {state}. {scope} |"
        )
    lines += [
        "",
        "For executed evidence and capability reporting states, read the full repository's "
        "Phase 3 development status. A documented workflow is not execution evidence.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for relative, result in (("docs/catalog.md", render()), ("SKILL_INDEX.md", render_index())):
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != result:
                raise SystemExit("catalog/index stale: run python scripts/build_catalog.py")
        else:
            path.write_text(result, encoding="utf-8")
