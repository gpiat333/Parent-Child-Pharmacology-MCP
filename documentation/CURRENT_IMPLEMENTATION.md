# Current implementation

Current source 0.14.0, policy 2026-11-22.16. Policy .15 fixes safety-routing false positives found after evaluation (condition names such as seizures or postpartum depression were treated as emergencies); evaluation results describe .14. Policy .16 adds the HRSA National Maternal Mental Health Hotline (1-833-TLC-MAMA) to perinatal crisis replies and recognizes more postpartum wording. Evaluated locally with Databricks model calls and MLflow tracking; the same frozen source passed in a Databricks serverless notebook. The existing App remains .9. No App deployment, public release or official submission occurred.

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


The research fixes add mandatory study-team eligibility/availability and bounded LactMed extract notices, constrain both draft and final-review instructions to the requested title/excerpt-only scope, and distinguish an unreported outcome from an explicit negative finding. R08 had a grading conflict: the application requires “Past listed deadlines,” while the old criterion demanded “Closed deadlines.” The criterion now accepts elapsed dates without falsely asserting that a submission portal is closed. This is a disclosed rubric clarification, not a clinical improvement or a retroactive score change.

The previous 3/10 benchmark had seven failures: B06/B09 were blocked by English-language false positives; B10 confused an aggregate seizure-control outcome with an active symptom; B01 miscalculated proportions; B04 miscounted matching Silver annotations; B07/B08 inspected the wrong or incomplete candidate set. The revised runtime adds narrowly bounded English task recognition, distinguishes named aggregate outcomes while preserving personal/acute routing, and returns optional joined Silver classifications and exported-row counts with explicit pagination. Counts retain snapshot and unmatched-row limitations. The revised benchmark client inspects the requested cohort and uses a bounded decimal arithmetic helper. The helper is client-side, not a 31st MCP tool. All ten questions and reference answers are unchanged; no expected answer is supplied to the model.

The final .14 benchmark scored 9/10; the intermediate .13 run scored 10/10. Both are retained. The remaining final B09 error returned the DOI of a different retrieved candidate despite selecting the correct PMID for an additional lookup. This is an answer-attribution failure, not missing source data. No answer was replaced or manually corrected to raise the score.

[Current evidence](../evaluation/retrieval-reliability-final/REPORT.md)
