# Current implementation

The existing **mcp-mc Databricks sandbox app was updated** on November 21, 2026 at the user's request. No GitHub push or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. The evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks. The 508 unit tests are the prior verified local baseline on unchanged source, not a new remote unit run.

Local unchanged-source baseline: **508 unit tests passed** with no failures, errors or skips. Active Databricks inventory: **30 tools, four prompts and four resources**. All **93 deployed runtime files** match the staged source; all 112 frozen server/client files remain unchanged. Runtime probes: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures (including partial/empty statuses).

Final chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. Initial completion was 24/28; four HTTP 429 attempts were archived before sequential retry. Completed answers were not regenerated.

Research grades: **19 fidelity pass, 2 fail, 0 not assessable; 19/21 tasks fulfilled**. URL membership: 21/21. Paired tasks: **MCP 7/7, plain 0/7**. Paired fidelity pass/fail/N/A: MCP 5/2/0; plain 1/5/1. N/A is excluded from fidelity rates. All **42 final MLflow rows** were read back with applicable scores and zero assessment errors.

These are known development cases, one completed sample each, with changing sources, a same-family diagnostic judge, bounded references and no independent clinician adjudication. Only MCP has retrieval, workflow enforcement and fixed notices. URL membership does not establish claim support. Neither clinical accuracy nor a speed advantage is established. An extra ‘Give me a pregnancy evidence brief…’ paraphrase failed to select the required workflow; this remains outside the unchanged 28-case benchmark. Required notices do not eliminate false reassurance or harmful framing.

No application source changed in this deployed rerun. Required notices, the composite-first matcher and corrected citation scanner remain as in [the notice revision](NOTICE_CITATION_REVISION.md). See [current Databricks evidence](DATABRICKS_VALIDATION.md) and [contracts](SAFETY_AND_EVIDENCE.md).
