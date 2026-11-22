# Presentation and demonstration

49 slides: 15 main and 34 hidden appendix slides. The exact red title disclaimer and six safety risks remain.

The local MCP is now policy .10. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Unit tests, MCP Inspector and evaluation drivers ran locally; model calls, grading and MLflow used existing Databricks services.

All **42 fresh capture rows** were graded and read back in MLflow, with zero scorer execution errors. Chats: **28/28 completed**, 28/28 expected routes and 28/28 tool-selection checks. Seven fixed stops made zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current research results: **21/21 fidelity passes** (0 fail, 0 N/A); **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 5/7; plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 1/6/0.

Fresh paired E01: fidelity pass; task fulfilled. The answer contains the required missing-abstract disclosure. All negative grades and rationales remain in the technical review.

Fidelity measures support in the captured reference pool. Task fulfillment measures completion of requested requirements. They are separate, fallible model judgments: a supported answer can omit an item; an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote checks and URL membership do not prove clinical truth or safety.

The evaluation cases and grader v3 core are unchanged; answers and tool-retrieved references are fresh, with normal source caches and snapshots. One answer per known development case, changing sources, model variability, a bounded shared pool and same-family grading limit interpretation. Only MCP has retrieval, workflow enforcement and notices. The main companion adds source review; the paired runner does not. R01 and R06 paired task flags concern completeness; R06’s rationale misdescribes which contact was shown. R03 has a label-wording fidelity flag. Scores remain unchanged for transparent review. No clinician adjudication or manual overrides occurred. This is a workflow comparison, not a clinical accuracy or speed claim.

The previous .9 answers, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The fresh .10 run changes application code and instructions as well as answers and live sources, so differences are not a controlled causal estimate. Older .5 figures (531 tests, research tasks 18/21 and paired MCP 5/7) remain historical. Prior raw evidence is preserved. Saved demo images and video illustrate .4.

Current validation: [evaluation report](../evaluation/abstract-disclosure-revision/REPORT.md). Prior deck and DOCX versions are archived.
