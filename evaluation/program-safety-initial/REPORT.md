> Historical initial November 21 run (443 tests), before the final selector and Spanish-string correction. Current results: ../program-safety-revision/REPORT.md.

# Current evaluation

November 21, 2026. GSA hackathon prototype, not an official NIH MCP tool. No production-readiness claim. Nothing deployed or pushed.

| Measure | Current result | Interpretation |
|---|---:|---|
| Unit tests | 443 passed | Zero failures, errors or skips |
| Inventory | 30 tools, 4 prompts, 4 resources | Local protocol discovery |
| Chat completion | 28/28 | Six initial rate-limited cases retried; original attempts retained |
| Expected routing | 28/28 | Known cases, not clinical sensitivity |
| Required/allowed tools | 28/28 | Execution check |
| Fixed stops | 7/7 | Zero downstream model/evidence calls |
| URL provenance | 20/21 | URL membership, not claim support |
| Diagnostic fidelity | 20 pass, 1 fail, 0 not assessable | Same-family model labels |
| Diagnostic task fulfillment | 19/21 | Research cases, separate from fixed stops |
| Direct protocol calls | 15 | Current source responses and contract checks |

The final source freeze contains 104 source files. All final chat records postdate it. The original English-query regression passed: True. The 28 cases comprise 24 retained regression cases plus portfolio, coverage and two S6 framing cases. Six initial HTTP-429 failures are retained under infrastructure-attempts; sequential retries kept the same source and prompts. Grading rate-limit retries are logged separately.

## Paired comparison

Seven questions, same model and shared instructions, one answer per arm. Only MCP receives retrieval tools. The paired prompt is shorter than the production companion's instructions/source review. Both arms receive diagnostic judgments against a shared bounded reference pool with arm labels hidden.

| Measure | MCP | Plain |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task labels | 3/7 | 0/7 |
| Fidelity pass / fail / N/A | 6 / 1 / 0 | 3 / 4 / 0 |
| Median seconds | 18.19 | 5.6 |

Timing is descriptive from single trials under parallel load. Honest tool-free abstention can leave a lookup incomplete without being false. No clinical accuracy or speed superiority is established.

## Grading limitations

Grader v2 retains content_flags and clarifies mandatory footers and access-abstention treatment. These rules were fixed before this run. Four synthetic controls matched 4/4 fidelity and 4/4 task labels. This small calibration does not validate clinical grading. The changed rubric and expanded cases prevent a direct improvement claim versus the previous run.

No clinician reviewed or certified these answers. Known cases, one trial, same-family judging, bounded/truncated references and heuristic extraction limit interpretation. Raw labels are unchanged; the full rationales remain in grading-review.json and individual judge files. S2 and S6 require clinical review of real answers for false reassurance and alarm.

## Current demonstrations and source scope

The current viewer uses complete selected excerpts from D01, fixed identity/crisis responses, a deliberate empty retrieval, clinician questions and a pre-tested daridorexant gap example. Coverage counts are navigation metadata, not evidence-quality scores. Empty label/abstract axes do not prove no human reports exist; FAERS signals remain separate and noncausal. Registry contacts are separate, unranked and not recommended.

New Spanish safety/referral strings remain held pending human Spanish-language review. Non-English/uncertain questions fail closed. Confirmed drug-code Spanish MedlinePlus education does not enable Spanish clinical chat. No machine translation of medical evidence is used.

## Historical evidence

The previous 395-test/26-tool/24-chat version and its raw grades remain under ../evidence-revision, with matching source-snapshot files. Older 359-test and 301-test runs and remote deployed checks are historical. They do not validate the current source. No credentials, provider settings or deployments were changed.

## Concrete limitations found during review

The sole URL-provenance failure joined adjacent Markdown citations into one string. Post-run inspection found all 16 actual destinations in the source pool, but the original 20/21 score remains unchanged. S6-lactation also repeats an inconsistent count/percentage already in LactMed: 30 mothers, five affected infants and 13%. The source itself does not reconcile. Source fidelity alone cannot validate an answer. See citation-parser-review.json and grading-review.json.

