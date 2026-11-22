> Current status: local policy .10, deployed .9 unchanged. Fresh chats and paired answers, unchanged grader v3. 592 server and 30 grader tests pass. No deployment or GitHub upload. See [current validation](DATABRICKS_VALIDATION.md). Earlier numbers and deployment statements below are historical.

> Historical 473-test milestone. The required-brief workflow remains active. Current 508-test results: [notice/citation correction](NOTICE_CITATION_REVISION.md).

# Evidence brief workflow correction

Policy 2026-11-21.3. Local prototype only. No deployment.

The earlier E01 question requested a daridorexant pregnancy evidence brief, but automatic tool selection chose individual sources. Its answer received a diagnostic task pass while its predeclared composite-tool check failed. The original 27/28 score is unchanged in the preceding run.

`core/workflows.py` recognizes explicit English requests to prepare or use an evidence brief and excludes incidental or negated mentions. `core/safety.py` attaches `requested_workflow.required_tool` only after all stop gates permit research. The companion enforces a named first tool call and rejects a missing tool, an answer without that call, or a batch that bypasses it. `medication_evidence_brief` still confirms identity internally. Additional lookups are allowed after the required call. The paired MCP arm enforces the same rule; the plain arm has no tools.

473 unit tests pass. The local inventory exposes 30 tools, four prompts and four resources. 28/28 chats completed, 28/28 expected routes and 28/28 required/allowed tool checks passed. Seven fixed stops made zero downstream evidence/model calls. Twenty direct protocol probes were retained.

Diagnostic grading of 21 research answers: 21 fidelity pass, 0 fail, 0 not assessable, and 19/21 tasks fulfilled. Seven paired questions produced 14 answers, with diagnostic task labels MCP 7/7 and plain 1/7. These are fallible model judgments, not clinical accuracy rates.

The 28 added regression cases cover mapping, actual E01/D05/D06 questions through full preflight, negations, stop priority, uncertainty, and client enforcement. During test development, a short technical English sentence was conservatively stopped by the existing language gate. Intent recognition is tested separately from language admission. No language threshold was relaxed. All stop rules remain higher priority than workflow routing.

The same cases, allowed/required tools, grader prompt and paired answer prompt were retained. A workflow pass is deterministic contract enforcement, not proof of better model selection or clinical performance. All raw failures, the archived timeout attempt, retry records and historical scores remain available. See [current report](../evaluation/brief-routing-revision/REPORT.md) and [raw diagnostic rationales](../evaluation/brief-routing-revision/grading-review.json).
