"""Synthetic paired-assay readiness and descriptive concordance; no learned integrator."""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from bioskills.omics import stable_pearson
from bioskills.science import (
    ScientificValidationError,
    begin_run,
    finish_run,
    reconcile_omics,
    write_json,
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
rng = np.random.default_rng(73)
latent = np.linspace(-2, 2, 8)
matrices, mappings = {}, {}
for name, prefix in [("transcript", "gene"), ("protein", "protein")]:
    samples = [f"{name}_{i}" for i in range(8)]
    matrices[name] = pd.DataFrame(
        8 + latent + rng.normal(0, 0.2, (4, 8)),
        index=[f"{prefix}_{i}" for i in range(4)],
        columns=samples,
    )
    mappings[name] = pd.DataFrame(
        {
            "specimen_id": [f"specimen_{i}" for i in range(8)],
            "subject_id": [f"subject_{i}" for i in range(8)],
            "split": ["train"] * 6 + ["test"] * 2,
            "timepoint": ["baseline"] * 8,
        },
        index=samples,
    )
# One protein-only specimen: keep the declared subject pairing consistent.
mappings["protein"].loc["protein_7", ["specimen_id", "subject_id"]] = [
    "specimen_extra",
    "subject_extra",
]
inputs = [Path(__file__)]
for name in matrices:
    for suffix, frame in [("matrix", matrices[name]), ("mapping", mappings[name])]:
        path = args.output / f"{name}-{suffix}.csv"
        frame.to_csv(path)
        inputs.append(path)
aligned, report = reconcile_omics(matrices, mappings)
assert len(report["matched_specimens"]) == 7
assert report["excluded_specimens"]["protein"] == ["specimen_extra"]
feature_map = pd.DataFrame(
    {"transcript": [f"gene_{i}" for i in range(4)], "protein": [f"protein_{i}" for i in range(4)]}
)
feature_map.to_csv(args.output / "synthetic-feature-map.csv", index=False)
# Scales are explicitly simulated log2 assay intensities. Correlate each declared
# one-to-one synthetic feature pair across matched specimens, without concatenation.
correlations = []
numerical_events = []
for row in feature_map.itertuples():
    correlations.append(
        {
            "gene": row.transcript,
            "protein": row.protein,
            "pearson_r": stable_pearson(
                aligned["transcript"].loc[row.transcript],
                aligned["protein"].loc[row.protein],
                events=numerical_events,
            ),
        }
    )
assert all(row["pearson_r"] > 0.8 for row in correlations)
write_json(args.output / "concordance.json", correlations)
bad = {k: v.copy() for k, v in mappings.items()}
bad["protein"].loc["protein_0", "subject_id"] = "wrong_subject"
try:
    reconcile_omics(matrices, bad)
except ScientificValidationError as exc:
    report["negative_control"] = {"status": "PASS", "detected": str(exc)}
else:
    raise AssertionError("Identity mismatch not detected")
report.update(
    {
        "analysis": "Descriptive matched-feature Pearson correlation of simulated log2 intensities",
        "integration_model": "NOT_RUN",
        "analysis_status": "EXECUTED",
        "numerical_evidence": {
            "status": "PASS",
            "events": numerical_events,
            "method": "shared stable_pearson; scoped numerical failure guards",
        },
        "timepoints": [
            {"specimen_id": specimen, "timepoint": "baseline"}
            for specimen in report["matched_specimens"]
        ],
        "limitations": report["limitations"]
        + [
            "Shared synthetic latent trend intentionally produces concordance",
            "No hypothesis testing, prediction, causal inference or real identifier mapping validation",
            "Train/test labels audited for subject leakage only; no model fit on either set",
        ],
    }
)
write_report(args.output, run, report)
write_claims(
    args.output / "claims.json",
    [
        {
            "claim": "Synthetic mapped feature pairs show positive descriptive concordance",
            "claim_type": "computed",
            "status": "PASS",
            "source_or_artifact": "concordance.json",
            "analysis_run_id": run["run_id"],
            "verification_method": "Pearson correlation after specimen reconciliation",
            "limitations": report["limitations"],
            "reviewer": "automated",
        }
    ],
)
finish_run(
    run,
    args.output,
    inputs + [args.output / "synthetic-feature-map.csv"],
    {"seed": 73, "scale": "simulated log2 intensities", "mapping": "synthetic one-to-one"},
)
print(f"PASS: paired-assay reconciliation and descriptive concordance. Artifacts: {args.output}")
