# Presentation and demonstration

The updated deck has 49 slides: 15 main and 34 hidden appendix slides. The red title disclaimer and six safety risks remain.

The existing **mcp-mc Databricks sandbox app was updated** with the routing fix on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks.

Chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. First-attempt completion: 28/28. Completed answers were not regenerated.

Research grades across 21 answers: **21 fidelity passes**, 0 failures, 0 N/A; **18/21 tasks fulfilled**. URL membership: 21/21. Paired task fulfillment: **MCP 5/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 4/3/0; plain 2/4/1. All **42 final MLflow rows** were read back with applicable scores and zero assessment errors.

Fidelity means support in the captured reference pool; task fulfillment means meeting the requested lookup or output requirements. These are separate model judgments. The plain model has no retrieval tools, so honest abstention can leave a source-lookup task incomplete. Zero fulfilled tasks does not mean every statement was false. N/A is excluded from fidelity rates. URL membership is not claim support.

Known development questions, one retained completed sample each, changing sources, a same-family judge, bounded references and no clinician adjudication limit interpretation. Only MCP has retrieval, workflow enforcement and fixed notices. Raw negative grades remain visible. This compares workflows, not isolated model ability or clinical accuracy; no speed advantage is established. Required notices do not eliminate false reassurance or harmful framing.

The preceding Databricks .4 run remains under `evaluation/databricks-validation-2026-11-21` with 508 local tests, 19/21 fidelity and 19/21 tasks; its paired tasks were MCP 7/7 and plain 0/7. Earlier local runs also remain. These are historical totals. Saved demo images and video illustrate the prior .4 revision, not current .5 validation.

The video is a historical local replay. Statements in the recording that nothing was deployed describe its recording time; the sandbox app was subsequently updated. Current validation is in [the evaluation report](../evaluation/brief-paraphrase-revision/REPORT.md). Prior deck and DOCX files are archived.
