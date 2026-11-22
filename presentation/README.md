# Presentation and demonstration

49 slides: 15 main and 34 hidden appendix slides. The title retains the exact red prototype disclaimer. Saved demo images/video illustrate historical .4 outputs. Current .12 results are from fresh captures and a separate fixed-snapshot benchmark.

Current source **0.12.0**, policy **2026-11-21.12**. The existing Databricks App remains on .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. MCP/chat/paired drivers and Phoenix ran locally; models and MLflow used Databricks. A separate Databricks serverless notebook ran the frozen source tests. Code is pushed only to the existing private GitHub repository. No App deployment, access-policy change, public release or official GSA submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **686/686 locally; 686/686 in Databricks**, no failures or skips | Contract/regression tests, not clinical correctness |
| Grader tests and controls | **30/30 unit tests; 10/10 synthetic fidelity controls** | Development checks, not independent adjudication |
| MCP Inspector | **9/9 checks** | 30 tools, four prompts, four resources; bounded protocol checks |
| Fresh chat routes and tools | **28/28 expected routes; 28/28 tool checks** | Known development questions |
| Fixed stops | **7/7**, zero downstream calls | Heuristic boundaries, not triage validation |
| Research answers | **21/21 fidelity passes; 18/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain model 0/7** | Seven known questions; unequal workflow capabilities |
| Paired fidelity pass/fail/N/A | **MCP 6/1/0; plain 1/5/1** | N/A is excluded from fidelity rates |
| Citation and trace checks | **21/21 URL membership; 42 unique MLflow rows verified** | Membership is not support for a claim |
| New fixed-snapshot benchmark | **3/10 exact answers; 7/10 generated final answers** | Separate Phoenix benchmark; three conservative routing stops and other retrieval/reasoning gaps |


Fidelity asks whether claims are supported by the captured, bounded evidence pool. Task fulfillment asks whether the requested requirements were met. They are separate, fallible same-family model judgments. Quote checks and URL membership do not establish relevance, medical truth or safety. All negative grades and raw rationales are retained; there were no manual score overrides or clinician adjudication.

The 28 development questions and seven paired questions retain grader v3 and the prior case definitions. There is one retained completed answer per case/arm; live sources, source caches, snapshots and generation variability affect results. Only MCP has retrieval, preflight and required notices. The companion also has a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer did not receive. No clinical-accuracy, speed or general-superiority claim follows.

The separate ten-question Phoenix benchmark uses a fixed MPRINT snapshot, independently explored read-only questions, an XML/CSV registry and exact string comparison. Only the two MPRINT evidence tools are exposed after preflight. Three research questions were conservatively blocked (two language gates and one urgent gate); other failures include arithmetic, record linkage and UNKNOWN answers. This is a newly authored known benchmark, not a held-out or clinical validation set. Its 3/10 result must not be merged with or substituted for the seven-case paired score. Three questions are moderate difficulty, and some share cohorts.
