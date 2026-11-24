# Behavioral evaluation and reproducible interoperability

The library is experimental. Structural checks, synthetic calculations, agent
responses and independent biological validation are different evidence classes.
General agent effectiveness has not been established.

The Phase 2 pilot remains provisional 0 PASS/4 FAIL/6 BLOCKED. A separate
November 24 maintainer benchmark at 98a9456 completed 40 turns across ten
instruction skills. Preliminary unblinded AI-assisted review: baseline16 full
passes/4 incomplete, enabled18/2; no frozen-rubric critical failures observed.
Nineteen of twenty target reads and thirty total reads were observed. Activation
stays UNOBSERVABLE and original scientific grading stays NOT_RUN. One sample per
condition and unresolved backend configuration preclude causal/general claims.

The [dated review](maintainer-reviews/2026-11-24-instruction-behavioral-review.md)
separates immutable evidence from provisional criterion adjudication. The
[repository protocol](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/docs/phase9-benchmark-migration.md)
documents versioned triggers, repeats, progress, interruption/resume, blinded
exports, reviewer records and Linux/Codespaces limits. New definitions contain
68 development triggers across all 17 skills and ten compound held-out
preparations. These are not executed results; prepared held-outs are author-visible.
No new large live benchmark is automatically authorized.

The universal ZIP includes corrected instructions/references, versioned benchmark
fixtures as data, the extraction-record schema/template and a reproducible synthetic interoperability recipe. Benchmark execution/grading tools remain in the
development repository; raw evaluation reports and private artifacts are excluded. Keep the
full extraction and install toolkit dependencies, then run:

```text
python examples/pseudobulk-to-enrichment/run.py --output new-pipeline --prepare-only
```

This generates 600 genes/48 cells/12 donors with 50 planted synthetic genes and
checks exact conservation and IDs. Native DESeq2/edgeR and ORA stay NOT_RUN in
preparation mode. With pinned R/Bioconductor, omit --prepare-only to execute both
methods and downstream Fisher/BH checks. Use new output directories and preserve
actual exit status/provenance. The fixture checks all 600 filtering IDs, retained
exports, scientific eligibility and downstream hashes.

This is manually constructed executable interoperability, not autonomous agent
orchestration. Synthetic recovery is not biological/clinical validation.
Independent review, real-data calibration and blinded repeated behavioral
evaluation remain incomplete.
