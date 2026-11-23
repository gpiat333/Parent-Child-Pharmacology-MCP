# Policy .25 evaluation (November 23, 2026): final

Source 0.19.0, policy 2026-11-23.25, benchmark runner v7. Every answer was generated fresh on this version, with the local MCP server (loopback HTTP) and the Databricks model gateway (`system.ai.gpt-5-6-luna`). Answers were graded by the same model family and logged to Databricks MLflow. Questions, reference answers and the grading rubric are unchanged from .14, and no grade was changed by hand. No App deployment or official submission occurred.

| Measure | Result | Interpretation |
|---|---|---|
| Application tests | **968 local; 968 Databricks** (run 909790976530204) | No failures, errors or skips, PowerShell parity tests included |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases; no retries needed |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **21/21 fidelity; 21/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 2/4/1** | N/A is not a fidelity pass |
| Citation checks | **21/21 URL membership** | URL membership does not establish claim support |
| MLflow readback | **42 of 42 rows verified** (21 research, 7 stops, 14 paired) | |
| Fixed-snapshot benchmark | **10/10 exact answers; 10/10 completed** | Fresh run of all ten questions, no retries |

MLflow: [parent](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/ee819bd826a84a4f9fb966729f7846ff) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/26b81f7036e34cef8e32a5fc6ac9ff07) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/3176a2bf05384941a3a5726be8cc5f49) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/737e35f5a7a7403586a43d6a702ed87d) · [benchmark summary](benchmark/summary.json) · [chat summary](chat-summary.json)

## What changed since .24, and why

In .24 the MCP arm completed 6 of 7 paired tasks. In E02 (a lamotrigine pregnancy brief that excludes personal recommendations), the answer restated the label's warning in its own voice: "lamotrigine should not be abruptly changed without the prescribing clinician's guidance." The grader agreed the fact was supported, but read the sentence as a personal recommendation. In R04, the answer added an unsupported contact ("the manufacturer can help verify the actual package").

Policy .25 adds one rule, carried by every evidence result (`framing_contract.source_attribution`), the server instructions, and the shared answer instructions that both paired arms receive: report a source's warnings and recommendations as that source's statements ("The label states that..."), never in the assistant's own voice, and name only the contacts the results name. In .25 both cases passed, and the MCP arm completed 7/7 paired tasks with 7/7 fidelity.

Earlier fixes remain: notice attribution (.23; research fidelity 19/21 to 21/21), the short-English language fix (.24), and benchmark runner v7's per-group statistics (benchmark 9/10 to 10/10). See [.24](../policy24-final/REPORT.md), [.23](../policy23-final/REPORT.md) and [.20](../policy20-final/REPORT.md).

## Retained attempts

Two plain-arm grades (R04 and E01) did not produce validly grounded assessments in three attempts. Following the .14, .20 and .24 procedure, they were archived in `failed-attempts/` and the unchanged answers were graded once more, which succeeded. The first paired MLflow records are archived in `failed-attempts/first-paired-mlflow/`. No answer was regenerated or selected by score.

## Not run

The MCP Inspector protocol check was not repeated (Node is not installed on this machine); the .14 result was 9/9.

## Limitations

These are the same known development cases, one retained answer per case and arm, graded by a fallible model of the same family with no clinician review. Fidelity means support in the captured references, not clinical accuracy. Results vary between runs. The .25 rule and the benchmark utility were added after specific failures on these known questions, so the final scores are not held-out estimates. The plain arm has no retrieval tools, so 0/7 can reflect an honest inability to look things up. Several changes happened together since .20, so no single score change can be credited to one fix.
