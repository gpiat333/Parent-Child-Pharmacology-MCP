# Current implementation

The local MCP is now policy .10. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Unit tests, MCP Inspector and evaluation drivers ran locally; model calls, grading and MLflow used existing Databricks services.

PubMed retrieval now returns PMID-level abstract coverage, separating missing text, unreturned records and request failures. The composite brief preserves the coverage. Both companion clients append a validated disclosure when needed, and a later successful refetch updates it. Titles alone are not outcome evidence. General instructions also preserve recall candidates and statuses, distinguish study comparators and unspecified specimens, and avoid unsupported methodological additions.

**592 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched both grade dimensions. These are not held-out or clinical validation. The 116 final application files are frozen. **MCP Inspector: 9/9 checks**, including the inventory of 30 tools, four prompts and four resources.

All **42 fresh capture rows** were graded and read back in MLflow, with zero scorer execution errors. Chats: **28/28 completed**, 28/28 expected routes and 28/28 tool-selection checks. Seven fixed stops made zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current research results: **21/21 fidelity passes** (0 fail, 0 N/A); **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 5/7; plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 1/6/0.

Fresh paired E01: fidelity pass; task fulfilled. The answer contains the required missing-abstract disclosure. All negative grades and rationales remain in the technical review.

Fidelity measures support in the captured reference pool. Task fulfillment measures completion of requested requirements. They are separate, fallible model judgments: a supported answer can omit an item; an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote checks and URL membership do not prove clinical truth or safety.

The evaluation cases and grader v3 core are unchanged; answers and tool-retrieved references are fresh, with normal source caches and snapshots. One answer per known development case, changing sources, model variability, a bounded shared pool and same-family grading limit interpretation. Only MCP has retrieval, workflow enforcement and notices. The main companion adds source review; the paired runner does not. R01 and R06 paired task flags concern completeness; R06’s rationale misdescribes which contact was shown. R03 has a label-wording fidelity flag. Scores remain unchanged for transparent review. No clinician adjudication or manual overrides occurred. This is a workflow comparison, not a clinical accuracy or speed claim.

## Outcome and report-context contract

`items` contains candidate source passages, grouped heuristically and not clinically adjudicated. `report_only_context` separately preserves FAERS query scope, timestamp, source URL, report terms and counts. It never confirms clinical outcomes or the source population.

When only report context is present, `outcome_or_effect_passages_retrieved` is false, `report_only_context_retrieved` is true, and `state` is `report_context_only`. `no_evidence_retrieved` is false because report material was retrieved; the explicit `empty_message` still identifies the lack of observed-outcome findings. The client must show both facts instead of turning an empty clinical row into an absence of all human reports. No rates, causation or safety conclusions are inferred. Other MCP clients must honor this display contract.

[Full report](../evaluation/abstract-disclosure-revision/REPORT.md). [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a05a172e30e8447ab5dd6adaea0236f5).
