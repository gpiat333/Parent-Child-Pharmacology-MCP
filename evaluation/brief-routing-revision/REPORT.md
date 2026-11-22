# Evidence brief workflow correction and rerun

Local November 21, 2026 GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim. Nothing deployed, pushed or submitted.

## Cause and correction

The prior E01 daridorexant pregnancy request asked for an evidence brief. The model used separate label, literature, trial, registry and coverage calls instead of `medication_evidence_brief`. The predeclared check required that composite. Its answer received a diagnostic task pass, but tool selection failed. The prior **27/28** remains unchanged under `../program-safety-revision`.

The preflight now recognizes explicit English evidence-brief requests only after safety, identity, privacy and language checks allow research. It returns a required workflow. The companion and MCP comparison arm require exactly one composite call before optional source lookups or a final answer, using the model gateway's named-tool choice. A missing tool or bypass attempt stops execution. The composite still confirms drug identity internally before source retrieval. Other requests retain automatic tool selection. Negated requests and incidental mentions do not activate the workflow.

This is a workflow correction, not proof that the model learned better tool selection. Every third-party client must enforce the returned contract. Narrow request matching can miss paraphrases. The conservative English gate can also overblock short technical requests; its thresholds were not changed in this revision.

## Current verified results

| Measure | Current result | Meaning |
|---|---:|---|
| Unit tests | 473 passed | Zero failures, errors or skips; 28 added regression cases |
| Inventory | 30 tools, 4 prompts, 4 resources | No new tool added |
| Source freeze | 106 files | Frozen before this evaluation |
| Chat completion | 28/28 | Current raw records retained |
| Expected routing | 28/28 | Known-case execution, not clinical sensitivity |
| Required/allowed tools | 28/28 | Original E01 check passes using the composite first |
| Fixed stops | 7/7 | No downstream evidence/model calls |
| URL provenance | 20/21 | Membership, not claim support |
| Diagnostic fidelity | 21 pass, 0 fail, 0 not assessable | Fallible same-family model labels |
| Diagnostic task fulfillment | 19/21 | Separate from execution and seven fixed stops |
| Direct protocol probes | 20 | 17 source/contract probes plus 3 workflow probes |

The 4 explicit brief requests all called the composite first. E01 was run first to verify the integration and retained unchanged in the full batch. Completed answers were not regenerated to improve scores. Any incomplete infrastructure attempts and retries are saved separately. All 28 questions, allowed/required tools, grading criteria, the grader prompt and the paired system prompt match the preceding 445-test run. Four synthetic grader controls matched 4/4 fidelity and 4/4 task expectations. That small calibration does not validate clinical grading.

## Seven paired comparisons

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task labels | 7/7 | 1/7 |
| Fidelity pass / fail / N/A | 7 / 0 / 0 | 1 / 6 / 0 |
| Median seconds | 17.06 | 8.79 |

The same model and shared answer instructions are used. Only the MCP arm has retrieval tools and enforces the preflight workflow requirement. The companion has a longer prompt and a separate source-review pass; paired answers are therefore not identical to the production companion. Timing describes retained successful attempts under parallel load and excludes the archived timeout and retry delay. There is no clinical accuracy or speed superiority claim.

## Grading limitations and remaining failures

Known development cases, one sample, changing live sources, same-family judging, bounded/truncated reference material and no independent clinician adjudication limit the interpretation. An unverified statement is not automatically false, and honest tool-free abstention can leave a lookup incomplete. URL membership does not establish support for a claim. Execution success does not establish accurate or appropriate clinical wording.

Raw failure rationales are retained in `grading-review.json`, `chat-judgments/` and `paired-final/`. The previous dose-exclusion and three-women-versus-three-reports findings are historical and remain in the preceding run. S2 false reassurance and S6 discontinuation harm still require clinical review of real outputs. Heuristic routing, source extraction and language checks remain imperfect. Spanish safety/referral text remains held for human review.

The two unmet chat-task criteria are the omitted activity-code interpretation caveat in P01 and the omitted explicit human-clinical-framing-review statement in S6-pregnancy. The raw URL check remains 20/21. In R12, its regex joined two adjacent Markdown links; both separate targets occur in the saved tool outputs. `url-parser-review.json` documents that parser limitation without changing the score or claiming that URL membership validates the answer.

## Retained evidence

The earlier 445-test run, 443-test initial run and 395-test revision retain their original raw results and matching source snapshots. Earlier deployed checks are historical and do not validate this local version. Existing model access was used; credentials and provider settings were not changed.
