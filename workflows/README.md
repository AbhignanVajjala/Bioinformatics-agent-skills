# Workflow execution contract

Workflows are sequential procedures by default. Assign one actual actor to each stage and record identity/run, inputs, outputs, status and unresolved issues. One actor may use several role documents, but must label these sequential role passes. Separate processes are only independent within their stated scope; shared instructions/model outputs do not establish blinded peer review.

Fan out only stages with immutable, validated inputs and no dependencies on one another. Each worker owns named artifacts; the coordinator reconciles conflicts and preserves minority findings. CRITICAL and MAJOR unresolved findings block dependent inference. Use `templates/handoff.json` and `templates/validation_report.json`; do not reduce failures to a generic quality score. No workflow grants publication, paid-compute, data-sharing or destructive-operation permission.
