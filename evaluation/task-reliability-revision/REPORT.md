# Intermediate task reliability run

This .13 run is preserved as development evidence. The final response-contract revision is evaluated separately in `../retrieval-reliability-final`. No App deployment occurred.

Results: 709 tests locally and in Databricks; 30 grader tests; 9/9 MCP Inspector checks; 42 MLflow rows verified. Research: 20/21 fidelity, 18/21 tasks. Paired: MCP 7/7 tasks and 7/7 fidelity, plain 0/7 tasks. Fixed-snapshot benchmark: 10/10 exact answers, up from the historical .12 3/10.

Remaining research flags: R01 omitted the bounded LactMed extract disclosure; R09 added population metadata to a title-only answer; R10 was incorrectly penalized for the mandatory application footer despite the rubric excluding it. P02 received a fidelity flag for a formulation-applicability caveat absent from the supplied reference. These are model judgments, not clinical adjudications. The next revision adds the disclosure, corrects conflicting final-review instructions and mechanically rejects footer-only negative findings without automatically assigning a pass.

The original .12 questions and benchmark reference answers are unchanged. R08 alone has a disclosed deadline-wording criterion clarification. Benchmark v2 adds joined candidate metadata, pagination guidance and bounded client arithmetic. Several workflow changes occurred together; no isolated causal or clinical accuracy claim is made.

## Retained attempts

An initial Phoenix startup call produced no answers. Unsupported low reasoning with tool calls then produced ten HTTP 400/incomplete captures, retained in benchmark-unsupported-reasoning-attempt. Supported none reasoning was restored with a two-file benchmark-only freeze amendment; all ten subsequent answers are retained once.

One E02 paired MCP attempt had a local transport ReadError and no answer. It was preserved before retry. The shared reference pool consequently changed: the prior E02 plain judgment was archived and both arms judged against the final pool. No plain answer changed. One R03 plain assessment exhausted quote-validation attempts; the unscored error was archived before reassessment. Valid judgments on unchanged inputs were retained. See failed-attempts and raw grader attempts.

## Source identity

Runtime and harness source commit: `20f9581`. The original and amended source freezes, raw answers, judgments, Phoenix receipts and MLflow readbacks are retained. Source is local; Databricks provides the model gateway, tracking and a separate notebook test. The deployed App remains .9. Known cases, single completed trials and same-family grading are not independent clinical validation.
