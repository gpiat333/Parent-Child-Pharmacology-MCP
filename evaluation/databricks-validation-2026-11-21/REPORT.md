# Databricks deployment and MLflow evaluation — November 21, 2026

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

The existing **mcp-mc Databricks sandbox app was updated** at the user's request. Deployment `01f1e5d04532167f8b244e9ca79d5fe1` is running policy `2026-11-21.4`. No GitHub push, official submission, new cluster, warehouse, model endpoint, permission change or provider change occurred. NIHRePORTERAgent source was not modified.

## Where this ran

The MCP server runs in [Databricks Apps](https://mcp-mc-7474654188777746.aws.databricksapps.com). Model calls use the existing Databricks managed gateway. MLflow scores, traces and artifacts are stored in the [evaluation experiment](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/cfad8c43ac3d4124922713c4c8124cae). The evaluation driver ran locally; no remote cluster job or Databricks notebook execution is claimed. The 508 unit tests were the prior verified **local** run on this unchanged source, not a fresh Linux unit run.

All 93 deployed runtime files were downloaded from the active immutable snapshot and matched byte for byte. All 112 frozen server/client files remain unchanged. Deployment/configuration and evaluation tooling changed; no application behavior was changed for this rerun.

## Verified results

| Measure | Result | Interpretation |
|---|---:|---|
| Local unit baseline | 508 passed | Zero failures/errors/skips; same source |
| Deployed inventory | 30 tools / 4 prompts / 4 resources | Observed on active app |
| Tool schemas / invalid inputs | 30 valid / 8 rejected | Runtime contract probes |
| Source/workflow captures | 20 | Captures, not 20 clinical passes; partial and empty statuses retained |
| Initial chat completion | 24/28 | Four HTTP 429 failures retained |
| Final chat completion | 28/28 | Retry only incomplete cases, sequentially |
| Expected routes | 28/28 | Known-case behavior |
| Required/allowed tool checks | 28/28 | Separate from answer quality |
| Fixed stops | 7/7 | Zero downstream evidence/model calls |
| URL membership | 21/21 | Does not establish claim support |
| Diagnostic research fidelity | 19 pass / 2 fail / 0 N/A | Fallible model labels |
| Diagnostic research tasks | 19/21 | Seven stops excluded |
| Applicable notices | 13/13 | Required text preserved |
| MLflow final rows verified | 42/42 | 21 research + 7 stops + 14 paired; zero assessment errors |

The three pilot answers are reused in the full research set; they are not three additional independent samples. The corrected pilot was read back successfully. Four synthetic grader controls matched 4/4 fidelity and 4/4 task expectations; this does not validate clinical grading.

## Seven paired questions

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task fulfillment | 7/7 | 0/7 |
| Fidelity pass / fail / N/A | 5 / 2 / 0 | 1 / 5 / 1 |
| Median successful-attempt seconds | 18.12 | 5.56 |

Both arms use the same model and shared instructions. Only MCP has retrieval, workflow enforcement and fixed notices. The paired runner uses a shorter prompt and no separate source-review stage. A shared bounded pool is judged without arm labels. This compares workflows, not isolated model ability. Abstention can be honest while leaving a lookup incomplete. N/A is not a fidelity failure; the combined MLflow fidelity mean excludes it. Report arm-specific counts above instead of treating the combined mean as an MCP result. Timings are uncontrolled and exclude retries; no speed advantage is established.

## Remaining limitations and recording fixes

The cases are known development cases with one retained completed sample, changing live sources, a same-family model judge, bounded references and no independent clinical adjudication. Raw negative grades were retained. The judge can misread evidence or penalize a valid statement because it lies outside its reference pool. Review `grading-review.json` and `TECHNICAL_REVIEW.md`; these are diagnostic observations, not clinical certification.

An extra smoke question, “Give me a pregnancy evidence brief for lamotrigine,” was allowed but did not select the mandatory brief workflow. “Compile an evidence brief…” matched correctly. This paraphrase limitation is outside the unchanged 28-case benchmark and remains unresolved; it must not be hidden behind the 28-case route score. Safety and language matching remain heuristic. Required notices cannot by themselves prevent false reassurance or harmful framing.

The first MLflow pilot exceeded Databricks' 65,535-byte assessment-value limit because full reference evidence was placed in expectations. Full evidence now lives in artifacts and expectations hold compact references. The earlier telemetry failure is preserved; answers and grades were reused. All final applicable scores, including False values and N/A handling, were read back from Databricks. MLflow uses precomputed captures with one root span per row; full MCP/tool traces are JSON artifacts, not separately instrumented spans.

A one-time OAuth token expired during the paired run's final status update after all results were saved. The harness now uses the existing CLI sign-in through a refreshable SDK credential provider. The status update was recovered without regenerating answers or grades. No administrator credential renewal was needed. Four incomplete chat attempts returned HTTP 429 and were archived before sequential retry; first-attempt reliability remains 24/28.

Early MLflow processes inherited this chat's NIHRePORTERAgent working directory, causing unrelated automatic Git metadata. Run tags were corrected and traces annotated; evaluated source is identified by the submission freeze and deployed snapshot hashes. No GitHub repository has been assigned or uploaded. Later evaluation processes run outside the unrelated checkout.

## Evidence and history

Current raw captures, scorers, model judgments, retry records, source hashes and MLflow readbacks are in this directory. The prior local 508-test evaluation remains under `../notice-citation-revision` with 20/21 fidelity and 17/21 tasks. The 473-test and older runs retain their original evidence. The existing demo images/video are labeled as predeployment local replays of the same source; this deployed evaluation is separate.
