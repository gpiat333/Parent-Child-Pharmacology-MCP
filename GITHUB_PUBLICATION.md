# Private GitHub publication

Current source 0.14.0, policy 2026-11-22.15. Policy .15 fixes safety-routing false positives found after evaluation (condition names such as seizures or postpartum depression were treated as emergencies); evaluation results describe .14. Evaluated locally with Databricks model calls and MLflow tracking; the same frozen source passed in a Databricks serverless notebook. The existing App remains .9. No App deployment, public release or official submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **709 local; 709 Databricks** | No failures, errors or skips |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| MCP Inspector | **9/9** | Protocol, schemas and sampled contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **17/21 fidelity; 21/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 1/5/1** | N/A is not a fidelity pass |
| Citation and trace checks | **21/21 URL membership; 42 MLflow rows verified** | URL membership does not establish claim support |
| Fixed-snapshot benchmark | **9/10 exact answers; 10/10 final answers** | Separate Phoenix task, not the seven-case comparison |


The private repository receives reviewed source and submission materials. The final publication receipt identifies the pushed commit; no App deployment.

[Current evidence](evaluation/retrieval-reliability-final/REPORT.md)
