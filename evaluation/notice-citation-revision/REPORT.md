# Required caveats and citation-checker correction

Local November 21, 2026 GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim. Nothing deployed, pushed, uploaded or submitted. NIHRePORTERAgent was not modified.

## What changed

The preceding 473-test run omitted two required caveats in generated answers: P01 did not state that activity codes alone do not establish research success; S6-pregnancy did not state that human clinical framing review remains required. Both limits already existed in the payload, but the model dropped them.

The server now exposes applicable `required_display_notices`. The companion and MCP comparison arm render the fixed notices after generation, selecting only trusted local policy text by tool identity. Funding tools require the activity-code interpretation notice. Clinical evidence tools require the clinical-framing-review notice. Repeated rendering does not duplicate exact notice lines. Stop responses do not receive these additions. Before-notice text and applied notice IDs are saved in evaluation traces. Third-party clients must enforce the display contract.

The URL checker now separates adjacent Markdown links and preserves balanced or escaped parentheses. It retains missing/unknown-URL failures and exact query distinctions. This is a bounded HTTP(S) scanner, not a complete Markdown renderer or claim-support grader. On the same historical saved outputs, the old check was 20/21 and the corrected parser is 21/21. Historical raw scores remain unchanged; that parser-only comparison is stored separately.

## Current verified results

| Measure | Current result | Meaning |
|---|---:|---|
| Unit tests | 508 passed | Zero failures, errors or skips; 35 added regressions |
| Source freeze | 112 files | Frozen before evaluation |
| Inventory | 30 tools, 4 prompts, 4 resources | No new MCP tools |
| Chat completion | 28/28 | Current saved answers |
| Expected routes | 28/28 | Known-case routing, not clinical sensitivity |
| Required/allowed tools | 28/28 | Separate from answer quality |
| Fixed stops | 7/7 | Zero downstream evidence/model calls |
| URL provenance | 21/21 | Corrected extraction; membership only |
| Diagnostic fidelity | 20 pass, 1 fail, 0 not assessable | Fallible model labels |
| Diagnostic task fulfillment | 17/21 | Separate from seven fixed stops |
| Applicable chat notices | 13/13 preserved | Deterministic final-output check |
| Direct protocol probes | 20 | Source/contract and workflow captures |

P01 and S6-pregnancy contain the previously omitted notices. The earlier E01 composite-first workflow remains enforced; all 4 explicit brief requests honored it. The same 28 questions, allowed/required tools, criteria, grader v2 prompt and paired answer prompt were retained. Only URL extraction changed in the execution checker. Synthetic grader controls matched 4/4 fidelity and 4/4 task expectations; this does not validate clinical grading.

## Seven paired questions

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task labels | 5/7 | 0/7 |
| Fidelity pass / fail / N/A | 6 / 1 / 0 | 2 / 4 / 1 |
| Median successful-attempt seconds | 17.43 | 6.43 |

The same model and shared answer instructions are used. Only MCP has retrieval tools, required workflow enforcement and fixed application notices. The paired runner uses a shorter prompt than the companion and omits its separate source-review stage. This compares two workflows; it does not isolate raw-model ability. Timings include service/retrieval effects under parallel load and exclude incomplete attempts and retry delays. No accuracy or speed superiority claim is made.

## Grading limitations and retained evidence

Known development cases, one retained completed sample, changing live sources, same-family judging, bounded/truncated references and no independent clinician adjudication limit interpretation. Honest abstention can leave a lookup incomplete without making a false claim. URL membership does not establish support for a claim. A mandatory caveat cannot by itself prevent false reassurance or alarm-inducing framing. S2 and S6 still require human clinical review of real outputs. Conservative English routing can overblock short technical questions; Spanish safety text remains held for human review.

Technical inspection identifies limitations in the current raw judgments. D05's grader alleges doses while quoting participant counts; the final answer contains study sizes, exposure percentages and gestational age, but no medication-dose values were found. This appears to be a grader error, not a corrected score. Its other study-design comments remain reviewable. P01 now includes the original caveat; its current task failure concerns a missing FY2024 grouped count in a capped retrieval, which must not be read as zero funded research. The grader also treats fixed application-policy notices as uncited source claims. E01's omission of returned FAERS signals requires review while preserving the distinction between spontaneous reports and confirmed pregnancy outcomes. The paired E01 output retains dose-bearing animal details and reaction-count alignment concerns.

All current failures and raw rationales remain in `grading-review.json`, `chat-judgments/` and `paired-final/`, with separate technical observations and no manual score adjustments or clinician adjudication. Completed answers were not regenerated to improve scores. Incomplete infrastructure attempts, if any, were retained before retry. The 473-test run and earlier 445, 443 and 395-test runs retain matching source snapshots and original results. Existing managed model access was used without renewing credentials or changing provider settings.
