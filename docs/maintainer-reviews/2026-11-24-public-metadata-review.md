# Public bioinformatics metadata retrieval maintainer investigation — November 24, 2026

Reviewer: **Abhignan Vajjala**. Human-directed maintainer self-review with
ChatGPT-assisted scripts in Codespaces, not independent external peer review.
Independent methodological and biological validation remain incomplete.

## Supplied historical evidence

Source `98a9456132fb474996f4c5d566065925ed79551b`, package 0.2.2, November 24,
2026. Environment: Python 3.12.3, NumPy 2.2.6, pandas 2.2.3, SciPy 1.15.3.
Original directories: `artifacts/my-combined-domain-audit-qAgil0` and
`artifacts/my-final-domain-audit-9j6Ml3`. Original files are unavailable here;
no original hashes or execution records are reconstructed. The supplied first
batch was 51 checks (26 PASS/16 INVESTIGATE/9 ASSESS); the second was 49
(18/19/12). Combined **100: 44 PASS/35 INVESTIGATE/21 ASSESS** across four
skills, not per-skill totals, accuracy rates or distinct defect counts.
Assessment-only cases also exposed confirmed numerical defects.

Null accession caused TypeError; unsupported source ordinary ValueError;
dry_run="false" incorrectly remained a dry run. Negative/Boolean pages and
Ensembl pagination correctly rejected. Mocked wrong Ensembl ID/type, API error,
empty object, wrong GEO accession/summary UID, summary error, negative count and
duplicate IDs were accepted; missing search fields raised KeyError.

Three **historical live** requests succeeded on November 24 at the original
source above. GEO GSE10072: search110/first20, human array study of cigarette
smoking/lung adenocarcinoma, including series and related sample/platform records.
SRA SRP000001: search9, XML study/experiment/sample/run/organism relationships,
human structural variation. Ensembl ENSG00000141510: Gene, homo_sapiens, TP53,
identity matched. Original live-geo.json/live-sra.json/live-ensembl.json were under
artifacts/my-final-domain-audit-9j6Ml3 and are unavailable locally. These establish
transport and partial identity, not complete annotation correctness. Earlier
releases' recorded **NOT_RUN** status is preserved as history.

## Correction and separate new execution

[Client](../../src/bioskills/retrieval.py) validates source-specific structure,
UID inventory, pagination, Ensembl gene/version and GEO/SRA relationships. GEO
related accessions use series membership/links; SRA typed XML fragments are parsed
without assuming a standalone XML document. Missing evidence remains partial;
contradictions fail. Status distinguishes transport, verified scope, no records,
empty pages, malformed/partial responses, identity and network/service failure.

Responses stay <=1 MiB, timeout15 seconds, one429 retry with delay0.34–5 seconds;
malformed/nonfinite Retry-After uses fallback. No credentials/raw datasets are
requested. Evidence includes source hashes, Python version, time/URLs, HTTP
metadata, transport type, raw base64 bodies and independently checkable SHA-256.
Routine tests remain offline. Schema/template define structure, not truth.

New corrected-client commands (separate from historical supplied observations):

```text
python examples/public-metadata/run.py geo GSE10072 --live --output artifacts/phase8/live-validated/geo.json
python examples/public-metadata/run.py sra SRP000001 --live --output artifacts/phase8/live-validated/sra.json
python examples/public-metadata/run.py ensembl ENSG00000141510 --live --output artifacts/phase8/live-validated/ensembl.json
```

All returned METADATA_RETRIEVED / VERIFIED_SCOPE / live, actual HTTP200, one
attempt per request. GEO110/20, twenty verified relationships; SRA9/9, nine
verified relationships; Ensembl one gene relationship (TP53/version21). This is
scoped page/relationship validation, not all-study or raw-count provenance.
Local reports retain bounded bodies; all body lengths/hashes and retrieval
schemas were independently checked. No raw/private runtime data are committed.
The following newly generated report hashes are not historical artifact hashes:

| New report / UTC time | SHA-256 |
|---|---|
| geo.json / 2026-11-24T15:01:27.860272+00:00 | 494e3b6bfca143fd7b80e5d7a60d18ba87fd0ffbd81f6396ce4a410933d33b2f |
| sra.json / 2026-11-24T15:01:31.589666+00:00 | bf960a3b979bd2e6e468e20249f8e54714c704016280f7c608fc0ff04ad2efde |
| ensembl.json / 2026-11-24T15:01:34.780619+00:00 | fb55cb0a95b51e9dbdc0b87192169ffb5654fab57babd6b0483b6466bf2ec2ec |

Raw response SHA-256, in request order:
GEO search 21f93c004f815ccccb6b4bef9e878bc7e6b15c2d5207dbfc29262310599e78fa;
GEO summary fed17a2bfec455754eec93cdce0654c04dc5fbf4871b1f03e62ee56171d32e08;
SRA search 7d9c202c7ca10c50f486ae307ca5a706351316d3e9b7ef3209fd28fdd3d3632b;
SRA summary 90fa88b35b4f0d4fa2aeb41890b03945980607ed1efa355b11edc82169cc8ff6;
Ensembl d8ad69a5418292b7f3a94a096eb3fa9c4699a58aefd5e9bf0e1744f9b720cf3d.

Regressions: tests/test_retrieval_integrity.py and tests/test_domain_integration.py.
The prior unrealistic metadata mock was replaced with provider-shaped required
fields and UID inventory; the uncontrolled KeyError expectation becomes a
MALFORMED_RESPONSE status assertion. Original benchmark prompts/verdicts and
scientific mathematics were not revised. Unavailable releases, organisms,
assemblies and measurement provenance remain unknown. Independent review and
exhaustive live schema coverage remain incomplete.

## Newly consulted primary references — 2026-11-24

[Official NLM E-utilities guide](https://dataguide.nlm.nih.gov/eutilities/utilities.html)
for search pagination/summary UIDs; [Ensembl lookup](https://rest.ensembl.org/documentation/info/lookup)
and [stable-ID/version semantics](https://useast.ensembl.org/info/genome/stable_ids/index.html);
[NCBI SRA metadata relationships](https://www.ncbi.nlm.nih.gov/sra/docs/submitmeta/).
The NCBI Bookshelf reference browser encountered verification restrictions;
no bypass was attempted. New ordinary public API requests above succeeded.
