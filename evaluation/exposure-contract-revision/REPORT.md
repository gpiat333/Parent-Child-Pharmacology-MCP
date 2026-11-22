# Intermediate .8 evaluation — superseded

This is a preserved development run, not the final full benchmark or current submission deck/DOCX. See [final report-context revision](../report-context-revision/REPORT.md).

All 28 chats completed. Research fidelity: 20/21; tasks fulfilled: 18/21. All 28 expected routes and required/allowed tool checks passed; all seven fixed stops made zero downstream evidence/model calls. Research and stop MLflow rows were read back (28 total), with zero assessment errors.

The R01 paired pilot passed fidelity and task checks and retained numeric concentrations. Its two answers remain saved, but a full seven-question paired comparison was intentionally not run for this superseded version. There is no full .8 paired score.

The research run revealed two further presentation issues: E01 omitted retrieved FAERS report context while showing an empty outcome axis, and S6-pregnancy added “generally reassuring” as its own conclusion. D05's separate task failure quotes doses present in reference evidence but absent from the answer; the [exact-text audit](grader-attribution-audit.json) retains that error without changing its score. All three raw task failures remain in the total.

The final repair keeps report-only context separate from established outcomes and instructs neutral source-attributed framing. No completed .8 answer was regenerated. All 114 frozen source files, 557 local test results, 93 deployed runtime hashes, raw captures and model grades are preserved. The existing sandbox was updated for this run; no GitHub upload occurred. No clinician adjudication occurred.
