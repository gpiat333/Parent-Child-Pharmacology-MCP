# Version 0.22.1 evaluation (November 23, 2026)

Source 0.22.1, policy 2026-11-23.29, 21 tools, summary evidence brief by default. Every answer was generated fresh on this version with the local MCP server (loopback HTTP) and the Databricks model gateway (`system.ai.gpt-5-6-luna`). Answers were graded by the same model family and logged to Databricks MLflow. No grade was changed by hand and no answer was regenerated or selected by score.

| Measure | .25 (31 tools) | 0.22.0 | 0.22.1 | Interpretation |
|---|---|---|---|---|
| Application tests, local and Databricks | 968 | 1,048 | **1,050** | No failures, errors or skips; Databricks run 1020002982130560 |
| Fresh chats completed | 28/28 | 27/27 | **27/27** | 20 research and seven stop cases |
| Expected routes | 28/28 | 25/27 | **27/27** | See "Stop wording check" |
| Expected tools | 28/28 | 26/27 | **27/27** | Trace contract checks |
| Fixed stops | 7/7 | 5/7 | **7/7** | No downstream evidence or model calls |
| Research fidelity | 21/21 | 20/20 | **20/20** | Separate fallible model judgment |
| Research tasks fulfilled | 21/21 | 19/20 | **18/20** | See "Task misses" |
| Paired tasks, MCP and plain | 7/7; 0/7 | 7/7; 0/7 | **7/7; 0/7** | Same model and shared instructions |
| Paired fidelity pass/fail/N/A, MCP | 7/0/0 | 5/2/0 | **7/0/0** | See "Fidelity fix" |
| Paired fidelity pass/fail/N/A, plain | 2/4/1 | 2/4/1 | **2/3/2** | N/A is not a fidelity pass |
| Citation checks | 21/21 | 20/20 | **20/20** | URL membership, not claim support |
| MLflow readback | 42 rows | 41 rows | **41 of 41 rows verified** | 20 research, 7 stops, 14 paired |
| Fixed-snapshot benchmark | 10/10 | 10/10 | **10/10 exact; 10/10 completed** | Fresh run, no retries |
| Judge calibration controls | 10/10 | 10/10 | **10/10** | Synthetic development controls |

MLflow: [parent](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/ff3bd73e1fbe4576b0c344b5e5fbb3d6) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/06ef4cb3cde84a05a26401815af5e1c7) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/2a47186bc05f4d57a51aa262ad199b7d) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/5fde38adc4d245b8890b89aee8d29303) · [benchmark summary](benchmark/summary.json) · [chat summary](chat-summary.json). The 0.22.0 run is kept in [`../v0220-final`](../v0220-final/).

## What changed since .25

The catalog went from 31 tools to 21 by merging overlapping tools, the evidence brief returns a summary by default, tool descriptions are short with the full answer rules returned in each result, seven tools have typed result schemas, and the routing rules were corrected (see [tool migration](../../documentation/TOOL_MIGRATION.md)). Case R08 was retired with the public-input tool, so there are 27 chat cases instead of 28. Cases D01, R03, R06 and R07 now expect the current tools; questions and grading criteria are otherwise unchanged.

## Fidelity fix (0.22.0 to 0.22.1)

On 0.22.0 the MCP arm completed 7 of 7 paired tasks but passed fidelity on only 5. In R03 the answer credited this server's continuity-of-care notice to the product label ("The label itself states that..."). In R04 it added the manufacturer as someone to contact, which no result named. Version 0.22.1 states the author beside the continuity notice, extends the attribution rule so a server notice is never introduced with "the label states" or "LactMed says", and has recall results list exactly whom they name for verification. On 0.22.1 both cases passed. These changes were made in response to failures on known questions and each case is a single trial, so this is not a held-out estimate. The .24 run failed R04 the same way.

## Stop wording check

On 0.22.0, D03 (crisis) and D04 (Spanish) stopped on the correct route with no tool calls but failed the deterministic check, which looked for the literal words "callback" and "cannot confidently". Policy .26 had reworded those messages after the .25 evaluation. The check now requires the policy file's current fixed messages (`crisis_us` and `perinatal_support` for D03, `language_support` for D04), so it follows the wording. This is a disclosed grader change, not a routing change; the 0.22.0 answers also pass the new check.

## Task misses on 0.22.1

Both were judged faithful to their sources but incomplete:

- **D01-cross-source:** the answer did not give a substantive summary of the product label's lactation evidence. The summary brief leaves out label section text and says so, so the model had only the LactMed findings in detail. This is a consequence of the summary default; `detail="full"` or `get_label_sections` returns the text.
- **R03:** the answer did not name the retrieved DailyMed product.

On 0.22.0 the single task miss was E02 (a study-design description was omitted); it passed on 0.22.1. P01 used `search_funded_research` instead of `summarize_research_portfolio` on 0.22.0 and the expected tool on 0.22.1, with no change to either tool between the runs.

## Retained attempts

On 0.22.1 the judge did not produce a validly grounded assessment for S6-lactation in three attempts. Following the .14, .20, .24 and .25 procedure, the failed record and the first research MLflow record are archived in `failed-attempts/`, and the unchanged answer (SHA-256 prefix `fe02022e7a5103d7` before and after) was graded once more, which succeeded. No answer was regenerated.

## Deployment

Version 0.22.0 was deployed to the Databricks App `mcp-mc` before this run and smoke-checked ([deployment status](../../documentation/DEPLOYMENT_STATUS.md)). The scored evaluation ran against a local server, not the hosted App. At the time of this report the App had not been redeployed with 0.22.1.

## Not run

The MCP Inspector protocol check was not repeated (Node is not installed on this machine); the .14 result was 9/9.

## Limitations

These are known development cases, one retained answer per case and arm, graded by a fallible model of the same family with no clinician review. Fidelity means support in the captured references, not clinical accuracy. Results vary between runs: three outcomes changed between 0.22.0 and 0.22.1 on cases whose code path did not change. The plain arm has no retrieval tools, so 0/7 can reflect an honest inability to look things up. Several changes were made together since .25, so no single score change can be credited to one change.
