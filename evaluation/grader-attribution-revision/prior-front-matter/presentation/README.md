# Presentation and demonstration

The updated deck has 49 slides: 15 main and 34 hidden appendix slides. The red title disclaimer and six safety risks remain.

The existing **mcp-mc Databricks sandbox app was updated** with completeness changes on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks.

Chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. First-attempt completion: 28/28. Completed answers were not regenerated.

Research grades across 21 answers: **21 fidelity passes**, 0 failures, 0 N/A; **20/21 tasks fulfilled**. URL membership: 21/21. Paired task fulfillment: **MCP 6/7, plain model 1/7**. Paired fidelity pass/fail/N/A: MCP 7/0/0; plain 1/4/2. All **42 final MLflow rows** were read back with applicable scores and zero scorer execution errors.

Fidelity means support in the captured reference pool; task fulfillment means meeting the requested lookup or output requirements. These are separate model judgments. The plain model has no retrieval tools, so honest abstention can leave a source-lookup task incomplete. An unfulfilled task does not mean every statement was false. N/A is excluded from fidelity rates. URL membership is not claim support.

Known development questions, one retained completed sample each, changing sources, a same-family judge, bounded references and no clinician adjudication limit interpretation. E01 task flags quote reference doses absent from the answers. Raw grades retained; no clinician review. Exact negatives and technical observations remain visible without score overrides. Only MCP has retrieval, workflow enforcement and fixed notices. This compares workflows, not isolated model ability or clinical accuracy; no speed advantage is established. Required notices do not eliminate false reassurance or harmful framing.

The partial .8 run retained 557 tests, research fidelity 20/21 and tasks 18/21; its full paired phase was intentionally not run after report-context and framing omissions were identified. The intermediate .6 run retains 548 tests, research fidelity 20/21 and tasks 20/21, and paired tasks MCP 5/7 and plain 1/7. The failed .7 payload-only pilot is preserved separately. Earlier .5 retains 531 tests, research fidelity 21/21 and tasks 18/21, with paired tasks MCP 5/7 and plain 0/7. Earlier .4 retains 508 tests, research fidelity 19/21 and tasks 19/21, with paired tasks MCP 7/7 and plain 0/7. These are historical totals. Saved demos illustrate .4, not current .9 validation.

The video is a historical local replay. Statements in the recording that nothing was deployed describe its recording time; the sandbox app was subsequently updated. Current validation is in [the evaluation report](../evaluation/report-context-revision/REPORT.md). Prior deck and DOCX files are archived.
