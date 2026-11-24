# Version 0.22.2 evaluation (November 23, 2026)

Source 0.22.2, policy 2026-11-23.29, 21 tools, summary evidence brief by default. Every answer was generated fresh on this version with the local MCP server (loopback HTTP) and the Databricks model gateway (`system.ai.gpt-5-6-luna`). Answers were graded by the same model family and logged to Databricks MLflow. No grade was changed by hand, no answer was regenerated or selected by score, and no grading attempt failed in this run.

| Measure | .25 (31 tools) | 0.22.0 | 0.22.1 | 0.22.2 | Interpretation |
|---|---|---|---|---|---|
| Application tests, local and Databricks | 968 | 1,048 | 1,050 | **1,051** | No failures, errors or skips; Databricks run 253478292719663 |
| Fresh chats completed | 28/28 | 27/27 | 27/27 | **27/27** | 20 research and seven stop cases |
| Expected routes | 28/28 | 25/27 | 27/27 | **27/27** | Trace contract checks |
| Expected tools | 28/28 | 26/27 | 27/27 | **27/27** | Trace contract checks |
| Fixed stops | 7/7 | 5/7 | 7/7 | **7/7** | No downstream evidence or model calls |
| Research fidelity | 21/21 | 20/20 | 20/20 | **20/20** | Separate fallible model judgment |
| Research tasks fulfilled | 21/21 | 19/20 | 18/20 | **19/20** | See "Task misses" |
| Paired tasks, MCP and plain | 7/7; 0/7 | 7/7; 0/7 | 7/7; 0/7 | **7/7; 0/7** | Same model and shared instructions |
| Paired fidelity pass/fail/N/A, MCP | 7/0/0 | 5/2/0 | 7/0/0 | **7/0/0** | |
| Paired fidelity pass/fail/N/A, plain | 2/4/1 | 2/4/1 | 2/3/2 | **1/4/2** | N/A is not a fidelity pass |
| Citation checks | 21/21 | 20/20 | 20/20 | **20/20** | URL membership, not claim support |
| MLflow readback | 42 rows | 41 rows | 41 rows | **41 of 41 rows verified** | 20 research, 7 stops, 14 paired |
| Fixed-snapshot benchmark | 10/10 | 10/10 | 10/10 | **10/10 exact; 10/10 completed** | Fresh run, no retries |
| Judge calibration controls | 10/10 | 10/10 | 10/10 | **10/10** | Synthetic development controls |

MLflow: [parent](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/48a333c4d6b04d40b8e463468c166fc5) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/f50460c849a1476688bb21a524de93c8) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a5c48e7f12b34ce2b70229632fc7ef46) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/64b19e3374af4e1bac10b5ae453b8f41) · [benchmark summary](benchmark/summary.json) · [chat summary](chat-summary.json). Earlier runs on this tool set are kept: [0.22.1](../v0221-final/REPORT.md) and [0.22.0](../v0220-final/).

## What changed since 0.22.1

On 0.22.1 two research answers were judged accurate but incomplete, and both had used the summary evidence brief. D01 was asked to summarize the LactMed evidence and the product label, but the summary left out the label's section text, so the answer could not say what the label's lactation section states. R03 was required to name the retrieved product and did not. Version 0.22.2 keeps the opening of each label section in the summary (up to 1,200 characters, with longer sections flagged) and has every label result name its exact product with an instruction to state it. On 0.22.2 both cases were fulfilled. These changes were made after seeing failures on known questions, and each case is a single trial.

## Task misses on 0.22.2

One research answer was judged faithful to its sources but incomplete: **R04** (recall lot lookup) listed the candidate recalls without the recall reasons the question asked for. R04 was fulfilled on 0.22.0 and 0.22.1, and nothing in its code path changed between 0.22.1 and 0.22.2. Across the three runs on this tool set the single-case misses were E02, then D01 and R03, then R04, which is consistent with run-to-run variation on one-trial cases as well as with the fixes described above.

## Changes since .25

The catalog went from 31 tools to 21, the evidence brief returns a summary by default, tool descriptions are short with the full answer rules returned in each result, seven tools have typed result schemas, and routing and attribution rules were corrected (see [tool migration](../../documentation/TOOL_MIGRATION.md) and the [0.22.1 report](../v0221-final/REPORT.md)). Case R08 was retired with the public-input tool, so there are 27 chat cases. The fixed-stop check reads the policy file's current messages, a grader change disclosed in the 0.22.1 report.

## Deployment

Version 0.22.2 was deployed to the Databricks App `mcp-mc` as `01f1e7a50b1c1872be5159c39a70aff2` after this run and passed the hosted smoke checks ([deployment status](../../documentation/DEPLOYMENT_STATUS.md)). The scored evaluation ran against a local server, not the hosted App.

## Not run

The MCP Inspector protocol check was not repeated (Node is not installed on this machine); the .14 result was 9/9.

## Limitations

These are known development cases, one retained answer per case and arm, graded by a fallible model of the same family with no clinician review. Fidelity means support in the captured references, not clinical accuracy. Results vary between runs. The fixes in 0.22.1 and 0.22.2 were written in response to failures on these same questions, so the scores are not held-out estimates. The plain arm has no retrieval tools, so 0/7 can reflect an honest inability to look things up.
