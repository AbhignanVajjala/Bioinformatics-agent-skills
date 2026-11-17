"""Synthetic count QC; deliberately does not perform differential expression."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bioskills.science import (
    ScientificValidationError,
    begin_run,
    finish_run,
    validate_counts,
    write_report,
    write_claims,
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
if args.output.exists() and any(args.output.iterdir()):
    parser.error(
        "Output directory must be empty; preserve prior run artifacts and choose a new path."
    )
args.output.mkdir(parents=True, exist_ok=True)
run = begin_run()
rng = np.random.default_rng(42)
samples = [f"synthetic_{i}" for i in range(6)]
counts = pd.DataFrame(
    rng.negative_binomial(10, 0.2, size=(100, 6)),
    index=[f"gene_{i}" for i in range(100)],
    columns=samples,
)
metadata = pd.DataFrame(
    {
        "subject_id": samples,
        "condition": ["control"] * 3 + ["treated"] * 3,
        "batch": ["a", "b", "a", "b", "a", "b"],
    },
    index=samples,
)
counts.to_csv(args.output / "counts.csv")
metadata.to_csv(args.output / "samples.csv")
broken = metadata.iloc[::-1]
broken.to_csv(args.output / "samples-misaligned.csv")
context = dict(
    scale="raw_counts", organism="synthetic; no real organism", reference="synthetic_gene_ids_v1"
)
report = validate_counts(counts, metadata, **context)
try:
    validate_counts(counts, broken, **context)
except ScientificValidationError as exc:
    report["negative_control"] = {"status": "PASS", "detected": str(exc)}
else:
    raise AssertionError("Misalignment was not detected")
libraries = counts.sum(axis=0)
assert (libraries > 0).all() and report["design_rank"] == 3
fig, ax = plt.subplots(figsize=(7, 3))
ax.bar(samples, libraries, color="#0072B2")
ax.set(ylabel="Synthetic library count total", title="QC only: six independent synthetic samples")
ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig(args.output / "library-sizes.png")
plt.close(fig)
report.update(
    {
        "method_selection": "Eligible for expert review of DESeq2 ~ batch + condition on declared raw integer counts; not executed.",
        "differential_expression": "NOT_RUN",
        "biological_interpretation": "NOT_RUN: synthetic data",
        "reviewer": "automated gates only",
    }
)
write_report(args.output, run, report)
write_claims(
    args.output / "claims.json",
    [
        {
            "claim": "Declared independent two-group design has full column rank",
            "claim_type": "computed",
            "status": "PASS",
            "source_or_artifact": "validation_report.json",
            "analysis_run_id": run["run_id"],
            "verification_method": "matrix rank and replication gates",
            "limitations": "No DE, power or biological validation",
            "reviewer": "automated",
        }
    ],
)
finish_run(
    run,
    args.output,
    [args.output / "counts.csv", args.output / "samples.csv", Path(__file__)],
    {"seed": 42, **context},
)
print(f"PASS: RNA-seq readiness/QC; DE NOT_RUN. Artifacts: {args.output}")
