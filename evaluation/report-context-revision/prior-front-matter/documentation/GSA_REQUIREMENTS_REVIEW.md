> Current status: policy .5 fixes the evidence-brief paraphrase gap; 531 local tests pass. The existing Databricks sandbox is updated; no GitHub upload. See [current validation](DATABRICKS_VALIDATION.md). Earlier counts and deployment statements below are historical.

# GSA event requirements review

Reviewed the full [official event page](https://www.gsa.gov/super-intelligence/si-community-of-practice/events-and-training/mcp-server-and-si-agent-government-hackathon), including its scope, judging criteria, deliverables, timeline and participation guidance. The page lists November 20, 2026 for submissions and limits work to sandbox prototypes using public government data, without public deployment.

The deliverables are a documented GitHub repository, presentation and evaluation. The evaluation sample is linked on the event page, not inside the GitHub starter repository. This package uses that exact [DOCX sample](https://www.gsa.gov/system/files/MCP-hackathon-sample-evaluation-document.docx), replacing its illustrative CDC/Phoenix content with this project's evidence. The sample's no-tool comparison results do not apply here.

| Judging area | Package evidence | Remaining limit |
|---|---|---|
| Readability and maintainability | Thin entry point; models/tools/clients/core; source parsers separated | Compatibility shims retained |
| Performance and reliability | 300 local tests; saved checks; failure injection; historical timings | Revised deployment and load testing not run |
| MCP design | Named strict inputs, structured output, annotations, selection guidance and tool tiers | Fresh model selection probes blocked |
| Innovation | Cross-source evidence with identity, provenance and missing-evidence handling | No measured superiority over other interfaces |
| Mission alignment | Dataset Access Server; parent, clinician, research and program-staff use cases | No operational adoption claim |
| Presentation | 15 main slides, appendix, archived response screenshots and video | Replay is historical, not live |

The revised source is local. GitHub upload and deployment are paused at the user's explicit request. Provider access remains expired; a plain-model comparison and clinician review are not completed. These gaps are disclosed in the evaluation and deck.
