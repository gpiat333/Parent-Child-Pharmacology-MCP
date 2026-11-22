# Current evaluation: three-axis evidence and language fix

Evidence date: November 20, 2026 Eastern. Source hashes were frozen before the final run. Nothing was deployed, pushed or provisioned. All final chat files postdate the freeze. Earlier diagnostic attempts remain under initial-language-run and selector-language-run, separate from current results.

| Current measure | Result | Meaning |
|---|---:|---|
| Unit tests | 395/395 | Zero failures, errors or skips |
| Protocol | 26 tools, 4 prompts, 4 resources | Observed through local MCP discovery |
| Chat completion | 24/24 | All saved responses completed |
| Expected routing | 24/24 | Original English false positive fixed; seven intended stops |
| Tool selection | 24/24 | Required/allowed tool checks |
| Research-answer URL provenance | 17/17 | Returned URLs, not proof of claim support |
| Fixed-stop contracts | 7/7 | Zero downstream model and evidence calls |
| Diagnostic research fidelity | 15 pass, 2 fail, 0 not assessable | Model labels, not clinical validation |
| Diagnostic research task fulfillment | 16/17 | Seven fixed stops are assessed separately |
| Direct protocol probes | 7 | Two brief pre-tests plus five contract/source calls |

The 24 chats comprise 16 previous cases, six safety/demo cases and two pregnancy cases. They are development/regression cases, not an unseen or representative clinical dataset. The companion applies a mandatory preflight, source review and output checks. The paired runner uses a shared, shorter prompt for both arms and a local preflight for the MCP arm; its results are distinct from the production-client chat evaluation.

## Seven paired questions

Same existing model route, shared instructions, one answer per question per arm. Only the MCP arm has retrieval tools. Five earlier questions are retained, with daridorexant and lamotrigine pregnancy questions added. The judge receives the same reference pool for both answers without arm labels. All 14 answers and judgments are saved unchanged.

| Measure | MCP | Plain model |
|---|---:|---:|
| Completed answers | 7/7 | 7/7 |
| Raw diagnostic task labels | 6/7 | 0/7 |
| Raw fidelity labels (pass / fail / N/A) | 6 / 1 / 0 | 0 / 6 / 1 |
| Median elapsed seconds | 17.48 | 6.81 |

Timing comes from single trials under parallel load and is descriptive only. The comparison measures retrieval-assisted task completion on these questions, not general model quality or clinical accuracy. An honest abstention may leave a lookup incomplete without making a false factual claim. No accuracy or speed advantage is established.

## Grading limitations observed in this run

Four synthetic controls matched all expected fidelity and task labels. Real-answer problems remained:

- **chat R03:** The compact judge pool omitted content_flags, including the removed-PLLR-category instruction. The original tool trace retains it. The fidelity failure is therefore partly sensitive to reference preparation, not proof that the answer is factually wrong.
- **chat E02-maternal-pk:** The judge rejects a statement that the MCP classified passages as candidates even though the pool contains heuristic candidate passages and an instruction to inspect study design. Retain the raw failure pending independent review.
- **chat R10:** Task failure is attributed to the mandatory application disclaimer/footer, despite the requested MedWatch link and causation caveat being supplied. No score was manually changed.
- **paired R04 and R09 plain:** The judge treats truthful no-live-lookup statements as contradicted by evidence available to the evaluator. Tool-free inability is not factual contradiction. The raw failures remain diagnostic.
- **paired R03 MCP:** The response emphasizes the lactation warning rather than adequately comparing warnings for the adult taking the medicine. The raw task failure is retained.
- **paired E01-gap MCP:** The answer says no human outcomes were identified, while the supplied FAERS results contain spontaneous pregnancy-related reaction reports. These are unverified signals rather than established clinical outcomes, but a broad absence claim needs tighter scope. The demo labels empty rows as label/abstract extraction gaps and keeps FAERS context separate.

The scores above are the original unadjusted labels. No failures were turned into passes. The grader shares the answer-model family, reference coverage is bounded, and no clinician independently reviewed or certified the answers. Evidence fields can be incomplete or truncated, and three-axis extraction is heuristic. See grading-review.json and the raw judgments for the exact rationales.

## Gap demonstration and source scope

Daridorexant was pre-tested: the selected DailyMed label has Risk Summary and Data but no parsed Clinical Considerations; it reports a human pregnancy-data limitation. Three broad PubMed records were returned without abstracts, and the targeted maternal-PK search returned zero records. The FDA directory returned one registry with public contacts. Animal findings and spontaneous FAERS signals remain separate context. Empty rows refer to this bounded label/abstract extraction, not to proof that no human reports or evidence exist anywhere.

Lamotrigine provides a contrasting pre-test with parsed Clinical Considerations, dose-adjustment source text and retrieved maternal-PK candidates. No personal dose is calculated. Participation listings are unranked and not recommended; they are suppressed on stop routes.

LactMed is lactation-only. TOXNET/DART history and PRGLAC, BPCA and PREA statements are verified against primary sources in documentation/PREGNANCY_EVIDENCE.md. The tool surfaces gaps rather than closing them.
