# Artifact templates

These JSON files are editable examples, not completed analyses. `analysis_run.json` uses conspicuous sentinel timestamps, exit status -1 and a `template-not-executed` run ID; replace these with actual execution records. Never cite a template as evidence.

Validate against the corresponding `schemas/<name>.schema.json` using JSON Schema Draft 2020-12 with format checking enabled. `tests/test_schemas.py` demonstrates this invocation. Array entries may be empty when not yet known; downstream analysis gates still require essential context and evidence. Manifest subject IDs and condition arrays, if provided, follow sample-ID order. Prefer a separate explicit mapping table for real multi-assay data. Store sensitive mappings outside public artifacts.

Check actual file hashes, command outcomes and timestamp order separately. Schema-valid text cannot prove its assertions. Custom example reports may be narrower demonstration artifacts; do not claim conformance without running the corresponding schema validator.
