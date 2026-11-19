"""First-use synthetic pseudobulk, enrichment and format demonstration."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from bioskills.expanded import inspect_format, ora, pseudobulk
from bioskills.science import begin_run, finish_run, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    if out.exists() and any(out.iterdir()):
        parser.error("Output directory must be empty")
    out.mkdir(parents=True, exist_ok=True)
    run = begin_run()
    rng = np.random.default_rng(731)
    cells = pd.DataFrame(
        {
            "subject_id": np.repeat(["d1", "d2", "d3", "d4"], 4),
            "specimen_id": np.repeat(["sp1", "sp2", "sp3", "sp4"], 4),
            "condition": ["control"] * 8 + ["treated"] * 8,
            "cell_type": ["synthetic_cell"] * 16,
            "timepoint": ["baseline"] * 16,
        },
        index=[f"cell{i}" for i in range(16)],
    )
    counts = pd.DataFrame(
        rng.poisson(10, (20, 16)), columns=cells.index, index=[f"g{i}" for i in range(20)]
    )
    counts.to_csv(out / "cell-counts.csv")
    cells.to_csv(out / "cell-metadata.csv")
    bulk, metadata, audit = pseudobulk(
        counts, cells, organism="synthetic", reference="v1", count_generation="Poisson seed731"
    )
    bulk.to_csv(out / "pseudobulk.csv")
    metadata.to_csv(out / "samples.csv")
    tested = [f"g{i}" for i in range(20)]
    data = {
        "selected": tested[:5],
        "tested": tested,
        "mappings": [
            {"source": g, "target": g, "organism": "synthetic", "reference": "v1"} for g in tested
        ],
    }
    gene_sets = {"synthetic_enriched": tested[:5], "synthetic_null": tested[10:]}
    write_json(out / "enrichment-input.json", {"data": data, "gene_sets": gene_sets})
    result = ora(
        data,
        gene_sets,
        organism="synthetic",
        reference="v1",
        database="synthetic",
        release="v1",
    )
    assert result["results"][0]["padj"] < 0.01
    path = out / "synthetic.fastq"
    path.write_text("@synthetic\nACGT\n+\nIIII\n")
    formats = inspect_format(path)
    write_json(
        out / "results.json",
        {"synthetic": True, "pseudobulk": audit, "ora": result, "format": formats},
    )
    finish_run(run, out, [Path(__file__), path, out / "cell-counts.csv",
                         out / "cell-metadata.csv", out / "enrichment-input.json"],
               {"synthetic": True, "seed": 731})
    print("PASS: pseudobulk aggregation, Fisher/BH ORA and FASTQ inspection executed")


if __name__ == "__main__":
    main()
