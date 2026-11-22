# Databricks validation

The existing **mcp-mc Databricks sandbox app was updated** with the routing fix on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks.

The missed “Give me a pregnancy evidence brief for lamotrigine” request now requires `medication_evidence_brief` first. Give/show/send variants share object grammar with their negations. All **12 separate deployed routing probes passed**, and the original missed question completed with the brief as the first evidence tool. Whole-question stops still take priority. These checks are separate from the unchanged 28-case benchmark; matching remains heuristic.

Fresh local suite: **531 tests passed**, including 23 new routing regressions, with zero failures, errors or skips. All **93 deployed runtime files** match the staged source; 112 server/client files were frozen. Active inventory: **30 tools, four prompts and four resources**. Runtime checks: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures, retaining partial/empty statuses.

Chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. First-attempt completion: 28/28. Completed answers were not regenerated.

Research grades across 21 answers: **21 fidelity passes**, 0 failures, 0 N/A; **18/21 tasks fulfilled**. URL membership: 21/21. Paired task fulfillment: **MCP 5/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 4/3/0; plain 2/4/1. All **42 final MLflow rows** were read back with applicable scores and zero assessment errors.

Fidelity means support in the captured reference pool; task fulfillment means meeting the requested lookup or output requirements. These are separate model judgments. The plain model has no retrieval tools, so honest abstention can leave a source-lookup task incomplete. Zero fulfilled tasks does not mean every statement was false. N/A is excluded from fidelity rates. URL membership is not claim support.

Known development questions, one retained completed sample each, changing sources, a same-family judge, bounded references and no clinician adjudication limit interpretation. Only MCP has retrieval, workflow enforcement and fixed notices. Raw negative grades remain visible. This compares workflows, not isolated model ability or clinical accuracy; no speed advantage is established. Required notices do not eliminate false reassurance or harmful framing.

[Full report](../evaluation/brief-paraphrase-revision/REPORT.md). [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/5b578ac30be1410380b9b144f0c54ed6).
