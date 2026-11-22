# Current implementation

This revision changes the grader and submission documents only. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Tests and the replay driver ran locally; grader calls and MLflow used the existing Databricks services.

Grader v3 fixes E01 source-to-answer misattribution. Negative content findings must quote the candidate answer; omissions must identify a requested requirement. Stable citation IDs bind to original answer URLs. Cached scores must match the grader code, model and exact inputs. The first structurally valid judgment is retained, including failures. Up to two correction attempts are allowed only for invalid schema or attribution; raw attempts remain available. No manual pass overrides were made.

Fresh local tests: **562 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched fidelity and task expectations. These controls are not held-out or clinical validation. All 114 frozen application files are unchanged; 93 runtime files were verified during the prior .9 deployment. The prior inventory of 30 tools, four prompts and four resources is unchanged and was not re-probed this revision.

All **42 retained rows** were reevaluated and read back in MLflow with zero scorer execution errors. No answer or source retrieval was regenerated. Retained chats: **28/28 completed**, 28/28 expected routes and 28/28 tool checks. Seven fixed stops contain zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current grader v3 research results: **20/21 fidelity passes**, 1 failure, 0 N/A; **20/21 tasks fulfilled**. Paired tasks: **MCP 6/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 0/5/2.

E01 main now passes. The paired E01 answer still omits the required disclosure of absent abstracts, so that genuine task failure remains. The false dose allegations have been removed without modifying either answer.

Fidelity means support in the captured reference pool; task fulfillment means meeting requested output requirements. These are separate, fallible model judgments. A supported answer can omit a required item, and an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote validation and URL membership do not prove claim support or clinical safety.

This is a controlled grader replay of the same answers and evidence, not a new sample or improvement in model behavior. Known development cases, one retained answer each, bounded shared references and a same-family judge limit interpretation. Only MCP originally had retrieval, workflow enforcement and fixed notices. No clinician adjudication or new latency comparison was performed. Initial grader candidates, raw attempts and all current negative grades are preserved.

## Outcome and report-context contract

`items` contains candidate source passages, grouped heuristically and not clinically adjudicated. `report_only_context` separately preserves FAERS query scope, timestamp, source URL, report terms and counts. It never confirms clinical outcomes or the source population.

When only report context is present, `outcome_or_effect_passages_retrieved` is false, `report_only_context_retrieved` is true, and `state` is `report_context_only`. `no_evidence_retrieved` is false because report material was retrieved; the explicit `empty_message` still identifies the lack of observed-outcome findings. The client must show both facts instead of turning an empty clinical row into an absence of all human reports. No rates, causation or safety conclusions are inferred. Other MCP clients must honor this display contract.

[Full report](../evaluation/grader-attribution-revision/REPORT.md). [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/28581b73dddf4472844828dc40bb9ca4).
