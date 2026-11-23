# Policy .24 evaluation (November 23, 2026): final

Source 0.19.0, policy 2026-11-23.24, benchmark runner v7. Every answer was generated fresh on this version, with the local MCP server (loopback HTTP) and the Databricks model gateway (`system.ai.gpt-5-6-luna`). Answers were graded by the same model family and logged to Databricks MLflow. Questions, reference answers and the grading rubric are unchanged from .14. No App deployment, public release or official submission occurred.

| Measure | Result | Interpretation |
|---|---|---|
| Application tests | **965 local; 965 Databricks** (run 335241140191974) | No failures, errors or skips, PowerShell parity tests included |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases; no retries needed |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **21/21 fidelity; 21/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 6/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 6/1/0; plain 1/4/2** | N/A is not a fidelity pass |
| Citation checks | **21/21 URL membership** | URL membership does not establish claim support |
| MLflow readback | **42 of 42 rows verified** (21 research, 7 stops, 14 paired) | |
| Fixed-snapshot benchmark | **10/10 exact answers; 10/10 completed** | Fresh run of all ten questions, no retries |

MLflow: [parent](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/99fdf5d3637e42dbb6392fb3b7d3b6e9) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/827cfeba25ed4dc18207b2569d516e5a) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/8f31c271268842d0a9a98fbf6ed02564) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/404276ca8e884f9db841d7512789e95e) · [benchmark summary](benchmark/summary.json) · [chat summary](chat-summary.json)

## What changed since .20, and why

**Research fidelity, 19/21 to 21/21.** In .20, D05 and R08 each credited a server notice to "MCP guidance" or "the MCP implementation". The chat client tells the model to attribute interpretation guidance to the MCP, but tool results never said that the MCP wrote those notices, so the grader could not verify the attribution. Policy .23 adds a `notice_attribution` field to every tool result, and the server and client instructions point to it. In the .23 run both cases passed. One new .23 failure (R04, "caplets" versus "tablets") did not recur in .24.

**Benchmark, 9/10 to 10/10.** In .20 and .23, B06 required comparing three exposures' spreads. The model computed one exposure by hand, skipped the others and copied the label from the wrong row. Runner v7 adds `aggregate_outcome_rows`, a client utility that computes a statistic for every group of captured rows and returns each group's exact label. It also lets the calculator accept max(), min() and abs(). In .24, B06 used the utility and matched. The questions and references are unchanged. These are client utilities, not MCP tools.

**Policy .24 language fix.** "I'm breastfeeding. Can I take ibuprofen?" was blocked as non-English, because the short-English check required a question word first and medicine names fooled the detector. Sentences may now open with common English statement words, and medicine names are masked before the foreign-language check. Spanish, French and mixed-language questions still stop. No scored case used this phrasing.

## The paired misses (MCP arm)

- **R04, fidelity:** the answer added that "the manufacturer can help verify the actual package". The evidence supports asking a pharmacist, not the manufacturer.
- **E02, task:** the answer restated the label's warning as direct advice ("lamotrigine should not be abruptly changed without the prescribing clinician's guidance"). The request excluded personal recommendations.

Both are model wording slips, retained as generated. The paired runner omits the chat client's source-review pass, which the 21 research chats use.

## Retained attempts

The first grading of the plain-arm E02 answer did not produce a validly grounded assessment in three attempts. Following the .14 and .20 procedure, it was archived in `failed-attempts/` and the unchanged answer was graded once more, which succeeded (task not fulfilled; fidelity not assessable). The first paired MLflow records are archived in `failed-attempts/first-paired-mlflow/`. No answer was regenerated or selected by score.

The intermediate .23 run is retained in [../policy23-final](../policy23-final/REPORT.md).

## Not run

The MCP Inspector protocol check was not repeated (Node is not installed on this machine); the .14 result was 9/9.

## Limitations

These are the same known development cases, one retained answer per case and arm, graded by a fallible model of the same family with no clinician review. Fidelity means support in the captured references, not clinical accuracy. Results vary between runs: .13 scored 10/10 on the benchmark, .14 scored 9/10, and .24 scored 10/10. The benchmark utility was added after B06 failed on these known questions, so 10/10 is not a held-out estimate. The plain arm has no retrieval tools, so 0/7 can reflect an honest inability to look things up. Several changes happened together since .20, so no single score change can be credited to one fix.
