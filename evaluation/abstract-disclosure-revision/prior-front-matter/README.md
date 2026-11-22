# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

This revision changes the grader and submission documents only. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Tests and the replay driver ran locally; grader calls and MLflow used the existing Databricks services. NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report](evaluation/grader-attribution-revision/REPORT.md) and [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/28581b73dddf4472844828dc40bb9ca4).

## Grader correction and verified results

Grader v3 fixes E01 source-to-answer misattribution. Negative content findings must quote the candidate answer; omissions must identify a requested requirement. Stable citation IDs bind to original answer URLs. Cached scores must match the grader code, model and exact inputs. The first structurally valid judgment is retained, including failures. Up to two correction attempts are allowed only for invalid schema or attribution; raw attempts remain available. No manual pass overrides were made.

Fresh local tests: **562 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched fidelity and task expectations. These controls are not held-out or clinical validation. All 114 frozen application files are unchanged; 93 runtime files were verified during the prior .9 deployment. The prior inventory of 30 tools, four prompts and four resources is unchanged and was not re-probed this revision.

All **42 retained rows** were reevaluated and read back in MLflow with zero scorer execution errors. No answer or source retrieval was regenerated. Retained chats: **28/28 completed**, 28/28 expected routes and 28/28 tool checks. Seven fixed stops contain zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current grader v3 research results: **20/21 fidelity passes**, 1 failure, 0 N/A; **20/21 tasks fulfilled**. Paired tasks: **MCP 6/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 0/5/2.

E01 main now passes. The paired E01 answer still omits the required disclosure of absent abstracts, so that genuine task failure remains. The false dose allegations have been removed without modifying either answer.

## What the grades mean

Fidelity means support in the captured reference pool; task fulfillment means meeting requested output requirements. These are separate, fallible model judgments. A supported answer can omit a required item, and an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote validation and URL membership do not prove claim support or clinical safety.

This is a controlled grader replay of the same answers and evidence, not a new sample or improvement in model behavior. Known development cases, one retained answer each, bounded shared references and a same-family judge limit interpretation. Only MCP originally had retrieval, workflow enforcement and fixed notices. No clinician adjudication or new latency comparison was performed. Initial grader candidates, raw attempts and all current negative grades are preserved.

Historical grader v2 on these same .9 answers reported research fidelity 21/21, tasks 20/21, and paired tasks MCP 6/7, plain 1/7. It contained the E01 attribution error. The older .5 runtime reported 531 tests, research tasks 18/21 and paired MCP 5/7, plain 0/7. Other intermediate runs remain archived. Saved demos illustrate .4; their scores and deployment statements describe that recording, not the present revision. The deck has 49 slides: 15 main and 34 hidden appendix slides.

## Research and evidence contracts

RePORTER supports IC, fiscal-year array, activity-code and organization filters plus bounded portfolio aggregates. Literature exposes type/date filters and access metadata. Trials expose direct NCT lookup and results-posted flags. Count-only coverage, RxNorm ingredient-product navigation and federal shortage records have narrow discovery scopes.

The evidence brief retains three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant exposure, and observed fetal/infant outcomes. Empty rows remain visible. PLLR subsections, maternal PK, missing/truncated sections, source populations, label provenance, study-count uncertainty, FAERS caveats and MPRINT snapshot dates stay explicit. **LactMed is lactation-only**; its alternatives section is excluded. Pregnancy findings come from labeling and literature.

No prescribing or personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Every client must enforce preflight and display contracts. Workflow matching and language detection remain heuristic. Spanish safety/referral strings remain held for human review. Source-authored MedlinePlus Spanish education is separate from clinical chat.

Registries, recruiting studies and public-input notices form a separate unranked participation tier suppressed on stop routes. No contact, enrollment or submission occurs. Inactive semantic LactMed search returns `not_enabled`.

## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Existing app: [mcp-mc](https://mcp-mc-7474654188777746.aws.databricksapps.com). Unchanged deployment: `01f1e5f7f6fc162fb8c3cc875e7f8546`. Policy: `2026-11-21.9`; grader: `3.0`.

Changes for this request are in `evaluation/grader-attribution-revision`; `server` and `chat-client` application code is unchanged. See [grader changes](evaluation/grader-attribution-revision/grader-changes.diff), [capture lineage](evaluation/grader-attribution-revision/capture-lineage.json), [current implementation](documentation/CURRENT_IMPLEMENTATION.md), [Databricks validation](documentation/DATABRICKS_VALIDATION.md) and [technical review](evaluation/grader-attribution-revision/TECHNICAL_REVIEW.md). Original tool traces are artifacts; each replay row has one root span. Historical evidence remains preserved. No GitHub destination has been selected.
