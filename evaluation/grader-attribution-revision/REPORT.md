# Grader attribution correction and replay evaluation

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

Grader v3 fixes the E01 reference-to-answer mix-up. The old grader requested exact quotations but never verified that they appeared in the candidate answer. It attributed animal-study doses and eligibility timing from the reference pool to two answers that did not contain them. The [historical exact-text audit](../report-context-revision/grader-attribution-audit.json) and original v2 grades remain unchanged.

The corrected grader separates the candidate and references, requires candidate quotations for negative content findings, anchors omissions to requested requirements, and validates cited URLs against the answer. A cache entry must match the grader implementation, model and exact grading inputs. It accepts the first structurally valid grade, whether pass or fail. Invalid JSON or attribution may trigger up to two correction attempts; all attempts are saved. Unresolved errors receive no score. No code converts a failure to a pass.

## Controlled rerun

All 28 chat captures and 14 paired answers, their evidence and case criteria are byte-identical to the completed .9 run. No answer was regenerated and no source lookup was repeated. This isolates the grading change and avoids mixing it with variation in new answers or live sources. It is not a new independent model-performance sample.

The runtime remains policy .9 on deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. No app deployment, infrastructure or permission change occurred in this revision. No GitHub upload or official submission occurred. Unit tests and the evaluation driver ran locally; grader calls and MLflow tracking used the existing Databricks services.

## Verified results

| Measure | Result | Scope |
|---|---:|---|
| Server unit tests | 562 passed | Fresh rerun of unchanged application code |
| Evaluator unit tests | 30 passed | Separate attribution, citation binding, cache and error-handling suite |
| Synthetic controls | 10/10 fidelity; 10/10 task | Includes a true dose violation, source-only dose, concentration, genuine omission and ranking behavior |
| Retained chats checked | 28/28 | Existing answers; no new generation |
| Routes / tool selections | 28/28 / 28/28 | Recomputed from retained traces |
| Fixed stops | 7/7 | Retained traces contain zero downstream evidence/model calls |
| URL membership | 21/21 | Membership is not claim support |
| Research fidelity | 20 pass / 1 fail / 0 N/A | New v3 model judgments |
| Research tasks fulfilled | 20/21 | Separate from fidelity |
| Grounded grading records | 35/35 | Literal attribution checks; not clinical validation |
| MLflow rows verified | 42/42 | 21 research + 7 fixed stops + 14 paired; zero scorer execution errors |

| Paired measure | MCP | Plain model |
|---|---:|---:|
| Retained completed answers | 7/7 | 7/7 |
| Tasks fulfilled | 6/7 | 0/7 |
| Fidelity pass / fail / N/A | 6 / 1 / 0 | 0 / 5 / 2 |
| New answers generated | 0 | 0 |

Only the MCP workflow originally had retrieval, workflow enforcement and fixed notices. Honest abstention can leave a lookup incomplete. The same-family judge uses a bounded shared reference pool that may include material a particular answer never received. N/A is excluded from fidelity rates. No new latency comparison or speed claim is made.

## E01 and historical comparison

E01 main answer: fidelity pass, task fulfilled True. E01 paired answer: fidelity pass, task fulfilled False. The false dose allegations are removed without changing either answer. Main rationale: The answer presents all three requested evidence axes with visible empty rows, preserves animal versus human evidence, reports the maternal PK retrieval gap within scope, separates FAERS report-only context and registry contacts, includes the FDA directory and label citations, avoids medication decisions and administered doses, and does not rank or recommend participation. Paired rationale: The answer accurately presents all three visible evidence axes, keeps empty rows visible, separates animal findings from human evidence, reports the retrieved maternal PK gap within scope, includes appropriately caveated FAERS context, and provides FDA registry information without recommending participation. It omits the required disclosure about absent PubMed abstracts. The retained pilot record reports each accepted attempt. Minor citation placement issues remain visible in the retained outputs and judge notes; no clinician adjudication is implied. Fixing a false allegation does not erase a different, supported omission.

| Grader on the same .9 answers | Research fidelity / tasks | Paired tasks MCP / plain |
|---|---|---|
| Historical v2 | 21/21 / 20/21 | 6/7 / 1/7 |
| Current v3 | 20/21 / 20/21 | 6/7 / 0/7 |

All 6 rows whose pass/fail scores changed are itemized in [grading-deltas.json](grading-deltas.json), alongside the old and new rationales for every answer. E01 paired remains task-fail, but for a different, supported omission rather than the old false dose allegation. Score differences can reflect the new rubric and model-judge variability; they are not new behavior by the answer model. The earlier .5 figures of research 18/21 tasks and paired MCP 5/7 belong to an older runtime and remain historical.

Current research negatives need separate interpretation. R04 is fidelity-pass but task-fail because the judge expects returned candidate recall records and their statuses, beyond the answer's total and no-matching-lot caveats. R12 meets the requested task, but its ancillary methodological statements are unverified in the bounded pool. The judge accepts R12's counts, coded age scope and causation/incidence caveats. Neither result establishes a clinically false answer. These technical observations do not override the model grades.

The paired MCP R01 answer meets the task but receives a fidelity failure for comparator-study wording and a more specific infant blood-level statement. Its quoted passages are present in the answer and sources; that mechanical check does not validate the judge's interpretation or the clinical importance of the wording. Independent clinical adjudication remains absent.

## Development checks and limitations

The initial v3 candidate matched 7/8 fidelity and 7/8 task control expectations. It incorrectly counted an epistemic caveat as a source claim and a reversed study direction as task-complete. Generic rubric definitions were clarified before the final freeze; the initial results remain in [development/initial-v3-candidate](development/initial-v3-candidate/STATUS.json). A subsequent candidate matched all eight controls but mistyped a long E01 citation URL on all three attempts, so no score was accepted for that answer. Those attempts remain in [development/url-copy-candidate](development/url-copy-candidate/STATUS.json). The implementation now assigns citation IDs to original answer URLs and binds those IDs in code, retaining the model's support judgments. The next candidate incorrectly demanded the word "unranked" even when an answer did not rank anything; its raw grades remain in [development/citation-id-candidate](development/citation-id-candidate/STATUS.json). The final rubric distinguishes behavioral compliance from required disclosures, and adds compliant-list and actual-ranking controls. Missing-abstract disclosures remain required when the task asks for them. All ten final controls match their expectations. These are development controls, not held-out validation.

The final benchmark needed 42 model assessment attempts for 35 accepted grades, including 7 structural corrections. Correction requests are triggered by attribution/schema checks, not by an undesirable score. The two E01 pilot assessments are reused once in the final benchmark. No completed benchmark answer was replaced. Full raw model attempts, failure-reason fields and input hashes are saved with each grade.

Literal quote validation cannot establish that a quotation is relevant, that an omission is clinically important, or that an answer is safe. The grader remains fallible. Known cases, one retained answer per case/arm, bounded references and no clinician review limit interpretation. Fidelity and task fulfillment are separate. A supported statement may leave a task incomplete; an unverified statement in the bounded pool is not automatically medically false.

Four MLflow workers per sequential research, stops and paired phase. Calibration and E01 pilot ran concurrently with at most two active model calls. No answers regenerated; prior answer latencies are historical, not a new timing comparison.

The [MLflow parent run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/28581b73dddf4472844828dc40bb9ca4) contains the new scores, raw captures, grader code and final documents. Precomputed replay produces one root span per row; full original tool traces are in artifacts. This was not a remote notebook unit-test run.

## Files

The grader changes are confined to `evaluation/grader-attribution-revision`; `server` and `chat-client` remain unchanged. See [grader-changes.diff](grader-changes.diff), [capture-lineage.json](capture-lineage.json), [TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md), and [summary.json](summary.json). The updated deck and evaluation DOCX use these metrics. Saved .4 demo images and video remain explicitly historical.
