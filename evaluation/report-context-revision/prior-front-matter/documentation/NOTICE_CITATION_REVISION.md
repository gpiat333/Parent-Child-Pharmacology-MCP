> Current status: policy .5 fixes the evidence-brief paraphrase gap; 531 local tests pass. The existing Databricks sandbox is updated; no GitHub upload. See [current validation](DATABRICKS_VALIDATION.md). Earlier counts and deployment statements below are historical.

# Required caveats and citation-checker correction

Policy 2026-11-21.4. Local prototype only. Nothing deployed. All changes were made in the Parent-child Pharmacology MCP submission folder, not NIHRePORTERAgent.

The prior P01 portfolio answer omitted the activity-code interpretation caveat; S6-pregnancy omitted the human-clinical-review statement. The client now appends applicable fixed application notices after generation. Funding tools require the activity-code caveat; clinical evidence tools require the human-review notice. Before-notice answers and notice IDs are retained. Stops receive no extra research notices. The URL checker now separates adjacent Markdown citations and preserves balanced parentheses; historical raw scores are unchanged.

`server/core/output_notices.json` defines trusted fixed text and applicable tool names. `core/output_notices.py` supplies payload metadata and Python rendering. `core/audit.py` attaches `required_display_notices` to allowed tool results. `chat-client/answer-notices.ps1` renders the same policy after final model generation. A clinical-review notice is not evidence that review has occurred. Third-party clients must implement the display contract themselves.

`chat-client/url_checks.py` replaces the evaluation regex with bounded HTTP(S) URL scanning. Tests cover adjacent links, titles, autolinks, plain text, nested/escaped parentheses, unknown sources and distinct queries. This is not a full CommonMark renderer. It changes membership extraction, not claim-support grading. The historical R12 comparison is retained separately in [the parser regression](../evaluation/notice-citation-revision/url-checker-regression.json); old raw scores remain unchanged.

508 unit tests pass with zero failures, errors or skips. The local inventory exposes 30 tools, four prompts and four resources. 28/28 chats completed, 28/28 expected routes and 28/28 required/allowed tool checks passed. Seven fixed stops made zero downstream evidence/model calls. Twenty source/contract and workflow probes were retained.

Diagnostic grading of 21 research answers: 20 fidelity pass, 1 fail, 0 not assessable, and 17/21 tasks fulfilled. Corrected URL checks: 21/21. Seven paired questions produced 14 answers, with diagnostic task labels MCP 5/7 and plain 0/7. These are fallible model judgments, not clinical accuracy rates.

The same questions and grader v2 were retained. Known development cases, single samples, changing live sources, same-family judging, bounded references and no clinician adjudication limit interpretation. Only the MCP comparison arm has retrieval, workflow enforcement and appended notices. These changes enforce display contracts and fix URL extraction; they do not establish clinical safety or improved raw-model reasoning. S2 false reassurance and S6 discontinuation harm still require clinical review.

All requested caveats are verified in [notice-contract-checks.json](../evaluation/notice-citation-revision/notice-contract-checks.json). Current failures and their raw model rationales remain in [grading-review.json](../evaluation/notice-citation-revision/grading-review.json). See [the report](../evaluation/notice-citation-revision/REPORT.md) for comparison methods and retry accounting.
