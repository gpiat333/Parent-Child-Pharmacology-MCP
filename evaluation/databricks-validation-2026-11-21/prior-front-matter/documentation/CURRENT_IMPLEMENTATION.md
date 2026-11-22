# Current implementation

508 unit tests pass with zero failures, errors or skips. The local inventory exposes 30 tools, four prompts and four resources. 28/28 chats completed, 28/28 expected routes and 28/28 required/allowed tool checks passed. Seven fixed stops made zero downstream evidence/model calls. Twenty source/contract and workflow probes were retained.

Diagnostic grading of 21 research answers: 20 fidelity pass, 1 fail, 0 not assessable, and 17/21 tasks fulfilled. Corrected URL checks: 21/21. Seven paired questions produced 14 answers, with diagnostic task labels MCP 5/7 and plain 0/7. These are fallible model judgments, not clinical accuracy rates.

The prior P01 portfolio answer omitted the activity-code interpretation caveat; S6-pregnancy omitted the human-clinical-review statement. The client now appends applicable fixed application notices after generation. Funding tools require the activity-code caveat; clinical evidence tools require the human-review notice. Before-notice answers and notice IDs are retained. Stops receive no extra research notices. The URL checker now separates adjacent Markdown citations and preserves balanced parentheses; historical raw scores are unchanged.

The same questions and grader v2 were retained. Known development cases, single samples, changing live sources, same-family judging, bounded references and no clinician adjudication limit interpretation. Only the MCP comparison arm has retrieval, workflow enforcement and appended notices. These changes enforce display contracts and fix URL extraction; they do not establish clinical safety or improved raw-model reasoning. S2 false reassurance and S6 discontinuation harm still require clinical review.

The prior required-brief workflow remains active. No MCP tools were added. See [the correction](NOTICE_CITATION_REVISION.md), [contracts](SAFETY_AND_EVIDENCE.md), [architecture](ARCHITECTURE.md) and [current evaluation](../evaluation/notice-citation-revision/REPORT.md). Nothing deployed.
