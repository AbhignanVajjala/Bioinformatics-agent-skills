"""Run narrow synthetic domain recipes and record input/output provenance."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from bioskills.domain_workflows import cross_view_analysis, metabolic_recipe
from bioskills.science import begin_run, finish_run, require, write_json


def multiomics_example(output):
    output.mkdir(parents=True)
    rng = np.random.default_rng(731)
    samples = [f"s{i}" for i in range(8)]
    latent = np.arange(8)
    matrices = {
        "rna": pd.DataFrame(
            rng.poisson(50 + latent * 15, (4, 8)),
            columns=samples,
            index=[f"gene{i}" for i in range(4)],
        ),
        "protein": pd.DataFrame(
            5 + latent + rng.normal(0, 0.1, (4, 8)),
            columns=samples,
            index=[f"protein{i}" for i in range(4)],
        ),
    }
    maps = {
        name: pd.DataFrame(
            {
                "specimen_id": samples,
                "subject_id": samples,
                "timepoint": ["baseline"] * 8,
                "split": ["train"] * 6 + ["test"] * 2,
            },
            index=samples,
        )
        for name in matrices
    }
    declarations = {
        "rna": {
            "scale": "raw_counts",
            "modality": "rna",
            "namespace": "synthetic_gene",
            "reference": "synthetic-v1",
            "count_generation": "Poisson seed731",
        },
        "protein": {
            "scale": "log2_intensity",
            "modality": "protein",
            "namespace": "synthetic_protein",
            "reference": "synthetic-v1",
        },
    }
    feature_map = pd.DataFrame({"rna": matrices["rna"].index, "protein": matrices["protein"].index})
    # Actual files are loaded again to exercise the normal input entry point.
    inputs = []
    for name in matrices:
        for suffix, frame in (("matrix", matrices[name]), ("mapping", maps[name])):
            path = output / f"{name}-{suffix}.csv"
            frame.to_csv(path)
            inputs.append(path)
    loaded = {name: pd.read_csv(output / f"{name}-matrix.csv", index_col=0) for name in matrices}
    loaded_maps = {name: pd.read_csv(output / f"{name}-mapping.csv", index_col=0) for name in maps}
    report = cross_view_analysis(loaded, loaded_maps, declarations, feature_map)
    require(len(report["correlations"]) == 4, "fixture", "Cross-view result absent.")
    return report, inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", choices=["metabolic", "multiomics"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("Output directory must be empty")
    run = begin_run()
    if args.domain == "metabolic":
        report = metabolic_recipe(args.output)
        inputs = [args.output / "synthetic-model.xml"]
    else:
        report, inputs = multiomics_example(args.output)
    write_json(args.output / "results.json", report)
    finish_run(
        run,
        args.output,
        inputs + [Path(__file__)],
        {"synthetic": True, "seed": 731, "method": args.domain},
    )
    print("PASS: synthetic recipe executed")


if __name__ == "__main__":
    main()
