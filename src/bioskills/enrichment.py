"""Scoped ORA with an outcome-independent universe-membership eligibility rule."""

from bioskills.inputs import require_text
from bioskills.science import require
from bioskills.validators import check_enrichment_background


def ora(data, gene_sets, *, organism, reference, database, release):
    from scipy.stats import false_discovery_control, fisher_exact

    check_enrichment_background(data, organism=organism, reference=reference, multiple_testing="BH")
    require_text(database, "database")
    require_text(release, "release")
    require(
        isinstance(gene_sets, dict) and bool(gene_sets),
        "gene_sets",
        "A supplied pathway family is required.",
    )
    mapping = {row["source"]: row["target"] for row in data["mappings"]}
    tested = {mapping[x] for x in data["tested"]}
    selected = {mapping[x] for x in data["selected"]}
    rows, inventory = [], []
    for name, members in sorted(gene_sets.items(), key=lambda item: str(item[0])):
        require_text(name, "pathway_id")
        require(isinstance(members, list), "gene_sets", "Pathway members must be a list.")
        for member in members:
            require_text(member, "pathway_member")
        membership = set(members)
        eligible = membership & tested
        audit = {
            "gene_set": name,
            "supplied_members": len(members),
            "unique_members": len(membership),
            "eligible_members": len(eligible),
            "duplicate_memberships": len(members) - len(membership),
            "members_outside_universe": len(membership - tested),
        }
        audit["eligibility"] = (
            "ELIGIBLE"
            if eligible
            else "EMPTY_GENE_SET"
            if not membership
            else "NO_UNIVERSE_MEMBERS"
        )
        inventory.append(audit)
        if not eligible:
            continue
        overlap = len(selected & eligible)
        table = [
            [overlap, len(selected) - overlap],
            [len(eligible) - overlap, len(tested - selected - eligible)],
        ]
        result = fisher_exact(table, alternative="greater")
        rows.append({**audit, "overlap": overlap, "pvalue": float(result.pvalue)})
    if rows:
        adjusted = false_discovery_control([row["pvalue"] for row in rows], method="bh")
        for row, value in zip(rows, adjusted, strict=True):
            row["padj"] = float(value)
    return {
        "analysis_status": "EXECUTED" if rows else "NOT_RUN",
        "status": "COMPUTED" if rows else "NO_TESTABLE_PATHWAYS",
        "method": "one-sided Fisher ORA with BH",
        "database": database,
        "release": release,
        "organism": organism,
        "reference": reference,
        "eligibility_policy": "Prespecified >=1 tested-universe member; no selection-overlap or p-value filtering",
        "supplied_family": len(gene_sets),
        "testing_family": len(rows),
        "eligible_family": len(rows),
        "family_audit": inventory,
        "excluded_pathways": [row for row in inventory if row["eligibility"] != "ELIGIBLE"],
        "results": rows,
        "mapping_policy": "one-to-one without dropped tested genes",
        "limitations": [
            "Association does not establish pathway activation or causation",
            "Universe, annotations and multiplicity policy require methodological review",
            "Ranked enrichment and biological validation are NOT_RUN",
        ],
    }
