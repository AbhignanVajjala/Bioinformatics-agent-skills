# metabolic-modeling demonstration

From the repository root, after `python -m pip install -e '.[dev,examples]'`:

```sh
python examples/metabolic-modeling/run.py --output artifacts/metabolic-modeling
```

On a managed machine with a read-only home, first set `XDG_CACHE_HOME` and
`MPLCONFIGDIR` to writable directories under the checkout (see installation guide).

Expected exit: 0 only after numerical/readiness assertions and negative controls pass.
Missing dependencies produce a nonzero import failure; no analysis is fabricated.
Outputs include input fixtures, `validation_report.json`, `claims.json` and
`analysis_run.json` with hashes, versions, actual command, timestamps and parameters.
Use a fresh output directory for each run to avoid mixing artifacts.

Toy COBRApy/GLPK FBA, pFBA, FVA and constraint sensitivity; not a genome-scale biological model.

All input data are generated locally by original project code, with explicit fixed
seeds where stochastic. No patient data or external dataset is downloaded. Synthetic
fixtures follow the project license. Mapping IDs are invented and never represent
real accessions. This is an execution regression, not scientific evidence about an organism.

See [the skill](../../.agents/skills/genome-scale-metabolic-modeling/SKILL.md). The tests in
[tests/test_science.py](https://github.com/AbhignanVajjala/Bioinformatics-agent-skills/blob/main/tests/test_science.py) include the invalid alternatives.
