# Presentation and demonstration

The updated deck has 49 slides: 15 main and 34 hidden appendix slides. The exact red title disclaimer and six safety risks remain.

This revision changes the grader and submission documents only. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Tests and the replay driver ran locally; grader calls and MLflow used the existing Databricks services.

All **42 retained rows** were reevaluated and read back in MLflow with zero scorer execution errors. No answer or source retrieval was regenerated. Retained chats: **28/28 completed**, 28/28 expected routes and 28/28 tool checks. Seven fixed stops contain zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current grader v3 research results: **20/21 fidelity passes**, 1 failure, 0 N/A; **20/21 tasks fulfilled**. Paired tasks: **MCP 6/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 0/5/2.

E01 main now passes. The paired E01 answer still omits the required disclosure of absent abstracts, so that genuine task failure remains. The false dose allegations have been removed without modifying either answer.

Fidelity means support in the captured reference pool; task fulfillment means meeting requested output requirements. These are separate, fallible model judgments. A supported answer can omit a required item, and an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote validation and URL membership do not prove claim support or clinical safety.

This is a controlled grader replay of the same answers and evidence, not a new sample or improvement in model behavior. Known development cases, one retained answer each, bounded shared references and a same-family judge limit interpretation. Only MCP originally had retrieval, workflow enforcement and fixed notices. No clinician adjudication or new latency comparison was performed. Initial grader candidates, raw attempts and all current negative grades are preserved.

Historical grader v2 on these same .9 answers reported research fidelity 21/21, tasks 20/21, and paired tasks MCP 6/7, plain 1/7. It contained the E01 attribution error. The older .5 runtime reported 531 tests, research tasks 18/21 and paired MCP 5/7, plain 0/7. Other intermediate runs remain archived. Saved demos illustrate .4; their scores and deployment statements describe that recording, not the present revision.

Current validation: [evaluation report](../evaluation/grader-attribution-revision/REPORT.md). Prior deck and DOCX files are archived.
