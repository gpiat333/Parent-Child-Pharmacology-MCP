# Evaluation methodology

Current source 0.14.0, policy 2026-11-22.14. Evaluated locally with Databricks model calls and MLflow tracking; the same frozen source passed in a Databricks serverless notebook. The existing App remains .9. No App deployment, public release or official submission occurred.

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


Fidelity asks whether claims are supported by the captured references. Task fulfillment asks whether all requested requirements were met. Neither is clinical accuracy. These are known development cases, one retained completed answer per case/arm, bounded references and a fallible same-family model judge. There was no clinician adjudication, manual score override or selection of a better completed answer. Live sources and model outputs vary. Other clients must enforce preflight and display contracts themselves.

The seven-case comparison measures the MCP workflow, including tools, preflight and required notices. The plain arm has no retrieval tools; 0/7 can reflect honest inability to verify a current lookup, not seven fabricated or medically wrong answers. Both arms receive the same updated instructions. The paired runner omits the companion’s additional source-review pass.

The ten-question benchmark is an exact-answer test of joins, filters, candidate selection and arithmetic against a fixed MPRINT snapshot. It is separate from the chat and paired scores. It is small, known, partly cohort-sharing and not held out. Runtime and client instructions changed together, so any gain is not a controlled estimate of one fix. Exact agreement with snapshot fields does not establish clinical truth, safety, source completeness or performance across all 30 tools.

The judge prompt is unchanged. Grader v3.1 now rejects a negative finding based only on the exact mandatory application footer, enforcing an existing rubric rule. It requests a new bounded model judgment and never sets a failed score to pass in code. Semantic grading errors remain possible. R08 alone has the disclosed criterion clarification above; other criteria and every question are unchanged. Heuristic routing and independent review of framing, omissions and evidence gaps remain limitations.

In the intermediate .13 run, the first Phoenix launch reached the service before startup completed and produced no answers. The next attempt received HTTP 400 because this gateway does not support function tools with low reasoning. All ten incomplete captures and receipts are retained under ../task-reliability-revision/benchmark-unsupported-reasoning-attempt. The final .14 run has fresh captures in its own directory. The runner was changed to supported none reasoning, matching the historical setting. The source-freeze amendment records the two benchmark-only files changed; runtime, chat captures, paired runner and grader were unaffected. No completed answer was replaced. Any gateway retry records remain alongside captures. In final .14, one E01 chat received HTTP 429 before producing an answer; its failed capture was preserved and only that incomplete request was retried. One plain R04 assessment exhausted reference-quotation validation and received no score; the invalid assessment was archived before reassessing the unchanged answer. All other valid grades were retained.

[Current evidence](../evaluation/retrieval-reliability-final/REPORT.md)
