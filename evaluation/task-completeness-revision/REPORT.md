> Preserved intermediate .6 run. The final revision is [exposure-measurements-revision](../exposure-measurements-revision/REPORT.md). No deck or DOCX was promoted for this intermediate run.

# Task completeness and Databricks evaluation

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

Policy `2026-11-21.6` addresses the missing-source and output-contract issues identified in the preceding evaluation. LactMed allocates its text limit across available sections, rather than letting a long exposure section crowd out infant outcomes or effects on lactation. Both label retrieval paths retain adult warnings and population-specific sections from the same selected label. Requested fiscal years have explicit retrieved-record counts, including zero in the extract while full-portfolio counts remain unknown when capped. A required FAERS notice prevents the population-generalizability caveat being dropped. Evidence-axis and companion review rules distinguish maternal endpoints, milk/infant measurements, protocol plans and source recommendations. Routing and stop rules retain their priority.

The existing Databricks sandbox app was updated to deployment `01f1e5e6dd53100d9329c4f5845f18f6`. No GitHub push or official submission occurred. No new cluster, warehouse, model endpoint, permission or provider configuration was created. NIHRePORTERAgent source was not modified.

## Where this ran and what changed

Source edits are in the submission folder's `server/clients`, `server/core`, `server/tools`, `server/tests` and `chat-client/test-mcp-chat.ps1`. The exact 13-file diff is retained in `source-changes.diff`. There are 17 additional test cases. All **548 tests passed locally**, with zero failures, errors or skips. All **93 runtime files** downloaded from the active Databricks snapshot match the staged source; 113 server/client files were frozen for this run.

The evaluation driver ran locally. The MCP app, model gateway and managed [MLflow experiment](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/b89043e64d7046ffbe87244ec9c4da46) ran in Databricks. This is not a remote notebook or cluster unit-test run. Fresh responses were captured for the same 28 questions and seven paired questions, with unchanged criteria, model, paired system prompt and grader v2 prompt. Companion completeness instructions changed as part of the product fix. Five pilot answers are included in the 28; they are not extra independent samples.

## Verified results

| Measure | Result | Meaning |
|---|---:|---|
| Fresh local unit tests | 548 passed | Includes 17 additional test cases |
| Deployed inventory | 30 tools / 4 prompts / 4 resources | Active app |
| Schemas / invalid inputs | 30 valid / 8 rejected | Runtime contract checks |
| Source/workflow captures | 20 | Partial/empty results retained; not clinical passes |
| Additional routing probes | 12/12 | Outside the unchanged benchmark |
| Original missed question | Completed; brief called first | Separate end-to-end client regression |
| First-attempt chat completion | 28/28 | Retry history retained |
| Final chat completion | 28/28 | Completed answers not regenerated |
| Expected routes | 28/28 | Known-case behavior |
| Required/allowed tools | 28/28 | Selection, not answer quality |
| Fixed stops | 7/7 | Zero downstream evidence/model calls |
| URL membership | 21/21 | Not claim support |
| Research fidelity | 20 pass / 1 fail / 0 N/A | Fallible diagnostic model labels |
| Research tasks fulfilled | 20/21 | Seven stops excluded |
| Applicable notices | 13/13 | Required text preserved |
| MLflow final rows verified | 42/42 | 21 research + 7 stops + 14 paired; zero assessment errors |

Four synthetic grader controls matched 4/4 fidelity and 4/4 task expectations. These controls do not validate clinical grading. Routing probes and the extra end-to-end question are separate artifacts, not added to the 42 benchmark rows.

## What the grades mean

**Fidelity** asks whether substantive answer claims are supported by the supplied, bounded evidence pool. A fail can mean unsupported detail, a mismatched citation, or a grader mistake; it does not by itself establish medical falsity. **Task fulfillment** asks whether the requested lookup or output requirements were met. The two criteria are independent: an honest abstention can avoid unsupported claims while leaving the task incomplete.

The preceding .5 run reported **21/21 fidelity passes and 18/21 tasks fulfilled**; its paired tasks were **MCP 5/7 and plain 0/7**. The earlier .4 run reported **19/21 fidelity and 19/21 tasks**, with paired tasks **MCP 7/7 and plain 0/7**. These are historical runs, not extra independent samples or the current totals. The seven paired questions are a separate comparison, not seven additional cases to add to the 21 research answers.

| Seven paired questions | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Task fulfillment | 5/7 | 1/7 |
| Fidelity pass / fail / N/A | 7 / 0 / 0 | 1 / 4 / 2 |
| Median successful-attempt seconds | 16.92 | 5.68 |

The drop from **7/7 to 5/7** in the preceding run came from two fresh answers: R01 omitted quantitative milk findings and inferred monitoring advice from observations; R03 retrieved only population label sections and left the adult warning comparison incomplete. The earlier routing-only change did not alter those tools or paired instructions, so the run-to-run drop does not establish that change caused the failures. Live sources, generated answers and model judgments can vary. The plain arm has no retrieval tools. An unfulfilled lookup does not mean every answer statement was false. Both paired arms use the same model and shared instructions; only MCP has tools, workflow enforcement and fixed notices. This compares workflows, not isolated model intelligence. N/A is excluded from fidelity rates. Timings are uncontrolled and exclude retries; no speed advantage is established.

## Grading limitations

Known development cases, one retained completed sample per case, changing sources, a same-family model judge, bounded references and no clinician adjudication limit the conclusions. The same grader is retained for comparability, including its limitations: in the prior .5 run it alleged dose values absent from D05's final answer, and treated separate evaluator reference evidence as though R03 had retrieved it. The requested adult comparison was nevertheless incomplete. The three prior research-task failures were R12's omitted generalizability wording, P01's absent numeric empty-year count and D05's disputed dose allegation plus a maternal-axis concern. Raw negative scores remain unchanged. See [technical review](TECHNICAL_REVIEW.md) and [raw findings](grading-review.json) for this run's exact findings. Required notices and passing route checks are not clinical validation and do not eliminate false reassurance or harmful framing.

In this run, R09 retained task fulfillment but received a fidelity failure for saying only a notice title and link were returned even though its answer also displayed the date. That is a metadata wording inconsistency, not a demonstrated false pharmacology claim. The E01 task failure cites dose values present in the reference material but absent from the answer, and overlooks a continuity-of-care caution that is present in the supplied payload. The exact quotation and payload field are checked in [the attribution audit](grader-attribution-audit.json). A passing D05 rationale also refers to historical dose values absent from its final answer. These examples show why raw model labels need interpretation; no score was overridden. This text audit is not clinical adjudication.

MLflow evaluates precomputed fresh captures with one root span per row. Full tool-call traces and reference evidence are artifacts, not separate tool spans. Existing CLI sign-in supplies refreshable authentication. All applicable scores, including False and N/A handling, were read back from Databricks.

## Preserved history

The preceding .5 run remains in `../brief-paraphrase-revision`, the .4 Databricks run in `../databricks-validation-2026-11-21`, and the earlier local run in `../notice-citation-revision`. Their raw outputs and source snapshots are preserved. Existing screenshots and video illustrate the prior `.4` revision; they are historical demos, not fresh `.6` validation. This intermediate run did not update the deck or DOCX; the final artifacts use the subsequent exposure-measurements revision.
