# Current implementation

The existing **mcp-mc Databricks sandbox app was updated** with completeness changes on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks.

The evidence brief now preserves FAERS report-only context beside empty outcome rows without treating counts as established clinical outcomes. Shared production instructions require neutral source-attributed framing and distinguish numeric concentrations from administered doses. Both paired arms receive those instructions. The answer prompt changed; the 28 questions, criteria and grader v2 did not. Earlier repairs retain source sections, adult and population label evidence, explicit empty-year counts, FAERS scope caveats and distinct maternal endpoints. All **12 separate deployed routing probes passed**, and the original paraphrase question still called the brief first. Safety stops retain priority.

Fresh local suite: **562 tests passed**, including 31 additional cases across the completeness repairs, with zero failures, errors or skips. All **93 deployed runtime files** match the staged source; 114 server/client files were frozen. Active inventory: **30 tools, four prompts and four resources**. Runtime checks: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures, retaining partial/empty statuses.

Chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. First-attempt completion: 28/28. Completed answers were not regenerated.

Research grades across 21 answers: **21 fidelity passes**, 0 failures, 0 N/A; **20/21 tasks fulfilled**. URL membership: 21/21. Paired task fulfillment: **MCP 6/7, plain model 1/7**. Paired fidelity pass/fail/N/A: MCP 7/0/0; plain 1/4/2. All **42 final MLflow rows** were read back with applicable scores and zero scorer execution errors.

Fidelity means support in the captured reference pool; task fulfillment means meeting the requested lookup or output requirements. These are separate model judgments. The plain model has no retrieval tools, so honest abstention can leave a source-lookup task incomplete. An unfulfilled task does not mean every statement was false. N/A is excluded from fidelity rates. URL membership is not claim support.

Known development questions, one retained completed sample each, changing sources, a same-family judge, bounded references and no clinician adjudication limit interpretation. E01 task flags quote reference doses absent from the answers. Raw grades retained; no clinician review. Exact negatives and technical observations remain visible without score overrides. Only MCP has retrieval, workflow enforcement and fixed notices. This compares workflows, not isolated model ability or clinical accuracy; no speed advantage is established. Required notices do not eliminate false reassurance or harmful framing.

## Outcome and report-context contract

`items` contains candidate source passages, grouped heuristically and not clinically adjudicated. `report_only_context` separately preserves FAERS query scope, timestamp, source URL, report terms and counts. It never confirms clinical outcomes or the source population.

When only report context is present, `outcome_or_effect_passages_retrieved` is false, `report_only_context_retrieved` is true, and `state` is `report_context_only`. `no_evidence_retrieved` is false because report material was retrieved; the explicit `empty_message` still identifies the lack of observed-outcome findings. The client must show both facts instead of turning an empty clinical row into an absence of all human reports. No rates, causation or safety conclusions are inferred. Other MCP clients must honor this display contract.


[Full report](../evaluation/report-context-revision/REPORT.md). [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/4985cc9db298488c8c18bbd1c84735be).
