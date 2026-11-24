"""Synthetic executable interoperability; this is not autonomous agent orchestration."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

from bioskills.expanded import ora, pseudobulk
from bioskills.science import begin_run, finish_run, validate_counts, write_json
from bioskills.validators import read_table

ROOT = Path(__file__).resolve().parents[2]
SEED = 9421


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    rng = np.random.default_rng(SEED)
    genes = [f"{i:06d}" for i in range(600)]
    donors = [f"{i:04d}" for i in range(1, 13)]
    mean = rng.uniform(60, 180, 600)
    means = np.tile(mean[:, None], (1, 12))
    means[:50, 6:] *= 4
    donor_counts = rng.negative_binomial(40, 40 / (40 + means))
    cells = pd.DataFrame(
        {
            "subject_id": np.repeat(donors, 4),
            "specimen_id": np.repeat([f"specimen-{d}" for d in donors], 4),
            "condition": ["control"] * 24 + ["treated"] * 24,
            "timepoint": ["baseline"] * 48,
            "cell_type": ["synthetic-T"] * 48,
            "batch": ["synthetic-one"] * 48,
        },
        index=[f"cell-{i:03d}" for i in range(48)],
    )
    values = np.zeros((600, 48), dtype=np.int64)
    for gene in range(600):
        for donor in range(12):
            values[gene, donor * 4 : (donor + 1) * 4] = rng.multinomial(
                int(donor_counts[gene, donor]), [0.25] * 4
            )
    counts = pd.DataFrame(values, index=genes, columns=cells.index)
    counts.to_csv(output / "cell-counts.tsv", sep="\t", index_label="gene_id")
    cells.to_csv(output / "cell-metadata.tsv", sep="\t", index_label="cell_id")
    bulk, metadata, audit = pseudobulk(
        counts,
        cells,
        organism="synthetic",
        reference="fixture-v1",
        count_generation=f"negative-binomial donor counts split by multinomial; seed {SEED}",
    )
    if bulk.shape != (600, 12) or list(bulk.index) != genes:
        raise ValueError("Pseudobulk identifier/shape invariant failed")
    if any(sum(int(x) for x in counts.loc[g]) != sum(int(x) for x in bulk.loc[g]) for g in genes):
        raise ValueError("Exact source-to-pseudobulk gene conservation failed")
    config = {
        "organism": "synthetic",
        "reference": "fixture-v1",
        "count_generation": f"synthetic-pseudobulk-seed-{SEED}",
        "measurement_type": "raw_counts",
        "design": "unpaired",
        "reference_level": "control",
        "treatment_level": "treated",
    }
    bulk.to_csv(output / "counts.tsv", sep="\t", index_label="gene_id")
    metadata.to_csv(output / "samples.tsv", sep="\t")
    write_json(output / "config.json", config)
    validate_counts(
        read_table(output / "counts.tsv"),
        read_table(output / "samples.tsv"),
        scale="raw_counts",
        organism="synthetic",
        reference="fixture-v1",
    )
    return genes, audit


def tail_probability(universe, selected, members, overlap):
    return sum(
        math.comb(members, x) * math.comb(universe - members, selected - x)
        for x in range(overlap, min(selected, members) + 1)
        if 0 <= selected - x <= universe - members
    ) / math.comb(universe, selected)


def validate_native(output, method, genes):
    folder = output / method
    status = json.loads((folder / "analysis-status.json").read_bytes())
    if status["analysis_status"] != "EXECUTED":
        raise ValueError("Native method did not complete")
    filtering = read_table(folder / "filtering.tsv")
    if list(filtering.index) != genes:
        raise ValueError("Native filtering export corrupted original gene identifiers")
    tested = filtering.index[filtering.retained == "TRUE"].tolist()
    for name in ("results.tsv", "normalized.tsv", "dispersion.tsv"):
        if list(read_table(folder / name).index) != tested:
            raise ValueError("Native retained-family identifiers differ")
    result = read_table(folder / "results.tsv")
    pkey, effect = ("padj", "log2FoldChange") if method == "deseq2" else ("FDR", "logFC")
    adjusted = pd.to_numeric(result[pkey].replace("NA", None), errors="raise")
    effects = pd.to_numeric(result[effect].replace("NA", None), errors="raise")
    selected = result.index[(adjusted < 0.05) & (effects > 0)].tolist()
    if not selected or not set(selected) < set(tested):
        raise ValueError("No scientifically eligible nonempty proper selected set")
    original_config = json.loads((output / "config.json").read_bytes())
    data = {
        "selected": selected,
        "tested": tested,
        "mappings": [
            {"source": g, "target": g, "organism": "synthetic", "reference": "fixture-v1"}
            for g in tested
        ],
    }
    enrichment = ora(
        data,
        {"synthetic_planted": genes[:50], "synthetic_comparison": genes[150:250]},
        organism=original_config["organism"],
        reference=original_config["reference"],
        database="synthetic-interoperability",
        release="v1",
    )
    probabilities = []
    for row in enrichment["results"]:
        p = tail_probability(len(tested), len(selected), row["eligible_members"], row["overlap"])
        if not math.isclose(row["pvalue"], p, rel_tol=2e-12, abs_tol=0):
            raise ValueError("Fisher probability differs from independent integer combinations")
        probabilities.append(p)
    expected = [0.0] * len(probabilities)
    running = 1.0
    order = sorted(range(len(probabilities)), key=probabilities.__getitem__)
    for rank in range(len(order), 0, -1):
        index = order[rank - 1]
        running = min(running, probabilities[index] * len(order) / rank)
        expected[index] = running
    for row, q in zip(enrichment["results"], expected, strict=True):
        if not math.isclose(row["padj"], q, rel_tol=2e-12, abs_tol=0):
            raise ValueError("BH differs from independent manual reference")
    if set(genes[:50]) - set(selected):
        raise ValueError(
            "Synthetic strong-effect positive control did not recover every planted gene"
        )
    write_json(output / f"{method}-enrichment.json", enrichment)
    return {
        "status": "EXECUTED",
        "filtering_ids_preserved": len(genes),
        "tested": len(tested),
        "selected_positive_effect_fdr_005": len(selected),
        "planted_recovered": 50,
        "nonplanted_selected": len(set(selected) - set(genes[:50])),
        "independent_fisher_bh": "PASS",
        "selection_rule": "BH-adjusted p <0.05 and effect >0",
        "provenance": {
            "counts_sha256": sha(output / "counts.tsv"),
            "native_results_sha256": sha(folder / "results.tsv"),
            "filtering_sha256": sha(folder / "filtering.tsv"),
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists():
        parser.error("Choose a new output directory; cached evidence must not be overwritten")
    output.mkdir(parents=True)
    run = begin_run()
    genes, audit = prepare(output)
    inputs = [
        output / name
        for name in (
            "cell-counts.tsv",
            "cell-metadata.tsv",
            "counts.tsv",
            "samples.tsv",
            "config.json",
        )
    ]
    hashes = {p.name: sha(p) for p in inputs}
    report = {
        "synthetic": True,
        "seed": SEED,
        "genes": 600,
        "cells": 48,
        "donors": 12,
        "planted_genes": 50,
        "aggregation": audit,
        "orchestration": "MANUALLY_CONSTRUCTED_EXECUTABLE_INTEROPERABILITY",
        "agent_execution": "NOT_RUN",
        "biological_validation": "NOT_RUN",
        "methods": {method: {"status": "NOT_RUN"} for method in ("deseq2", "edger")},
    }
    write_json(output / "pipeline-status.json", report)
    if not args.prepare_only:
        rscript = shutil.which("Rscript")
        if not rscript:
            report["blocker"] = "Rscript unavailable; aggregation executed, native DE/ORA NOT_RUN"
            write_json(output / "pipeline-status.json", report)
            print(report["blocker"], file=sys.stderr)
            return 2
        for method in report["methods"]:
            command = [
                rscript,
                str(ROOT / "recipes/rnaseq/run.R"),
                method,
                *(str(output / name) for name in ("counts.tsv", "samples.tsv", "config.json")),
                str(output / method),
            ]
            report["methods"][method] = {"status": "RUNNING", "command": command}
            write_json(output / "pipeline-status.json", report)
            try:
                completed = subprocess.run(command, capture_output=True, timeout=180, check=False)
            except subprocess.TimeoutExpired as error:
                (output / f"{method}.stdout").write_bytes(error.stdout or b"")
                (output / f"{method}.stderr").write_bytes(error.stderr or b"")
                report["methods"][method].update(
                    status="INCOMPLETE", reason="Native R timed out", exit_status=None
                )
                write_json(output / "pipeline-status.json", report)
                return 2
            except OSError as error:
                report["methods"][method].update(
                    status="NOT_RUN",
                    execution_status="FAILED",
                    reason=type(error).__name__,
                    exit_status=None,
                )
                write_json(output / "pipeline-status.json", report)
                return 2
            (output / f"{method}.stdout").write_bytes(completed.stdout)
            (output / f"{method}.stderr").write_bytes(completed.stderr)
            report["methods"][method] = {
                "status": "FAILED",
                "exit_status": completed.returncode,
                "command": command,
            }
            write_json(output / "pipeline-status.json", report)
            if completed.returncode:
                return 2
            try:
                report["methods"][method].update(validate_native(output, method, genes))
                if hashes != {p.name: sha(p) for p in inputs}:
                    raise ValueError("Scientific input files changed")
            except (ValueError, KeyError, OSError) as error:
                report["methods"][method].update(status="FAILED", reason=str(error))
                write_json(output / "pipeline-status.json", report)
                raise
            write_json(output / "pipeline-status.json", report)
    report["input_sha256"] = hashes
    report["output_sha256"] = {
        p.relative_to(output).as_posix(): sha(p)
        for p in output.rglob("*")
        if p.is_file() and p.name != "pipeline-status.json"
    }
    write_json(output / "pipeline-status.json", report)
    finish_run(
        run,
        output,
        [
            Path(__file__),
            ROOT / "recipes/rnaseq/run.R",
            ROOT / "recipes/rnaseq/validation.R",
            *inputs,
        ],
        {
            "synthetic": True,
            "seed": SEED,
            "native_methods": "NOT_RUN" if args.prepare_only else "EXECUTED",
        },
    )
    print(
        "PASS: exact synthetic preparation"
        if args.prepare_only
        else "PASS: synthetic pseudobulk, native DE and ORA interoperability"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
