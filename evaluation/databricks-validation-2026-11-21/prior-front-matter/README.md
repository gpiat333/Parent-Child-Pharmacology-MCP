# Parent-child Pharmacology MCP

Local **Dataset Access Server** submission for the GSA hackathon. Public-evidence discovery and preparation questions for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.** Nothing deployed, pushed, uploaded or submitted. NIHRePORTERAgent was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [saved-result demo](presentation/current-demo/index.html), and [current report](evaluation/notice-citation-revision/REPORT.md). The deck retains 49 slides: 15 main and 34 hidden appendix slides.

## Current verified results

508 unit tests pass with zero failures, errors or skips. The local inventory exposes 30 tools, four prompts and four resources. 28/28 chats completed, 28/28 expected routes and 28/28 required/allowed tool checks passed. Seven fixed stops made zero downstream evidence/model calls. Twenty source/contract and workflow probes were retained.

Diagnostic grading of 21 research answers: 20 fidelity pass, 1 fail, 0 not assessable, and 17/21 tasks fulfilled. Corrected URL checks: 21/21. Seven paired questions produced 14 answers, with diagnostic task labels MCP 5/7 and plain 0/7. These are fallible model judgments, not clinical accuracy rates.

The prior P01 portfolio answer omitted the activity-code interpretation caveat; S6-pregnancy omitted the human-clinical-review statement. The client now appends applicable fixed application notices after generation. Funding tools require the activity-code caveat; clinical evidence tools require the human-review notice. Before-notice answers and notice IDs are retained. Stops receive no extra research notices. The URL checker now separates adjacent Markdown citations and preserves balanced parentheses; historical raw scores are unchanged.

The same questions and grader v2 were retained. Known development cases, single samples, changing live sources, same-family judging, bounded references and no clinician adjudication limit interpretation. Only the MCP comparison arm has retrieval, workflow enforcement and appended notices. These changes enforce display contracts and fix URL extraction; they do not establish clinical safety or improved raw-model reasoning. S2 false reassurance and S6 discontinuation harm still require clinical review.

The prior E01 composite-first fix remains active. Explicit brief requests require `medication_evidence_brief` after an allowed safety, identity, privacy and language preflight. Other requests retain automatic tool selection. The 35 new regressions cover notice scope, stop priority, rendering parity/idempotence and citation boundaries, including the actual prior R12 answer.

## Research and evidence contracts

RePORTER supports IC, fiscal-year array, activity-code and organization filters plus bounded portfolio aggregates. Literature exposes type/date filters and access metadata. Trials expose direct NCT lookup and results-posted flags. Count-only coverage, RxNorm ingredient-product navigation and federal shortage records have narrow discovery scopes.

The evidence brief retains three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant exposure, and observed fetal/infant outcomes. Empty rows remain visible. PLLR subsections, maternal PK, missing/truncated sections, source populations, label provenance, study-count uncertainty, FAERS caveats and MPRINT snapshot dates stay explicit. **LactMed is lactation-only**; its alternatives section is excluded. Pregnancy findings come from labeling and literature.

No prescribing or personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Every client must enforce preflight and display contracts. Workflow matching and language detection remain heuristic. Spanish safety/referral strings remain held for human review. Source-authored MedlinePlus Spanish education is separate from clinical chat.

Registries, recruiting studies and public-input notices form a separate unranked participation tier suppressed on stop routes. No contact, enrollment or submission occurs. Inactive semantic LactMed search returns `not_enabled`.

## Local use and traceability

Use `server/run-local.ps1 -Test` for regressions or `server/run-local.ps1` for loopback serving. The current source freeze covers 112 files. Existing managed model access was used without changing credentials or provider settings. Incomplete infrastructure attempts, if any, are retained before retry; completed answers are not regenerated to improve scores.

See [notice/citation correction](documentation/NOTICE_CITATION_REVISION.md), [current implementation](documentation/CURRENT_IMPLEMENTATION.md), [contracts](documentation/SAFETY_AND_EVIDENCE.md), [pregnancy evidence](documentation/PREGNANCY_EVIDENCE.md), and [tool migration](documentation/TOOL_MIGRATION.md). The prior 473-test run remains under `evaluation/brief-routing-revision` with its original 19/21 task result and 20/21 raw URL score. The 445, 443, 395, 359 and 301-test runs and remote deployed checks remain historical.
