# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

The local MCP is now policy .10. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Unit tests, MCP Inspector and evaluation drivers ran locally; model calls, grading and MLflow used existing Databricks services. NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report](evaluation/abstract-disclosure-revision/REPORT.md) and [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a05a172e30e8447ab5dd6adaea0236f5).

## Changes and verified results

PubMed retrieval now returns PMID-level abstract coverage, separating missing text, unreturned records and request failures. The composite brief preserves the coverage. Both companion clients append a validated disclosure when needed, and a later successful refetch updates it. Titles alone are not outcome evidence. General instructions also preserve recall candidates and statuses, distinguish study comparators and unspecified specimens, and avoid unsupported methodological additions.

**592 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched both grade dimensions. These are not held-out or clinical validation. The 116 final application files are frozen. **MCP Inspector: 9/9 checks**, including the inventory of 30 tools, four prompts and four resources.

All **42 fresh capture rows** were graded and read back in MLflow, with zero scorer execution errors. Chats: **28/28 completed**, 28/28 expected routes and 28/28 tool-selection checks. Seven fixed stops made zero downstream evidence/model calls. URL membership: 21/21 research answers.

Current research results: **21/21 fidelity passes** (0 fail, 0 N/A); **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 5/7; plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 6/1/0; plain 1/6/0.

Fresh paired E01: fidelity pass; task fulfilled. The answer contains the required missing-abstract disclosure. All negative grades and rationales remain in the technical review.

## What the grades mean

Fidelity measures support in the captured reference pool. Task fulfillment measures completion of requested requirements. They are separate, fallible model judgments: a supported answer can omit an item; an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote checks and URL membership do not prove clinical truth or safety.

The evaluation cases and grader v3 core are unchanged; answers and tool-retrieved references are fresh, with normal source caches and snapshots. One answer per known development case, changing sources, model variability, a bounded shared pool and same-family grading limit interpretation. Only MCP has retrieval, workflow enforcement and notices. The main companion adds source review; the paired runner does not. R01 and R06 paired task flags concern completeness; R06’s rationale misdescribes which contact was shown. R03 has a label-wording fidelity flag. Scores remain unchanged for transparent review. No clinician adjudication or manual overrides occurred. This is a workflow comparison, not a clinical accuracy or speed claim.

The previous .9 answers, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The fresh .10 run changes application code and instructions as well as answers and live sources, so differences are not a controlled causal estimate. Older .5 figures (531 tests, research tasks 18/21 and paired MCP 5/7) remain historical. Prior raw evidence is preserved. Saved demo images and video illustrate .4. The deck has 49 slides: 15 main and 34 hidden appendix slides.

## Research and evidence contracts

RePORTER supports IC, fiscal-year array, activity-code and organization filters plus bounded portfolio aggregates. Literature exposes type/date filters and access metadata. Trials expose direct NCT lookup and results-posted flags. Count-only coverage, RxNorm ingredient-product navigation and federal shortage records have narrow discovery scopes.

The evidence brief retains three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant exposure, and observed fetal/infant outcomes. Empty rows remain visible. PLLR subsections, maternal PK, missing/truncated sections, source populations, label provenance, study-count uncertainty, FAERS caveats and MPRINT snapshot dates stay explicit. **LactMed is lactation-only**; its alternatives section is excluded. Pregnancy findings come from labeling and literature.

No prescribing or personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Every client must enforce preflight and display contracts. Workflow matching and language detection remain heuristic. Spanish safety/referral strings remain held for human review. Source-authored MedlinePlus Spanish education is separate from clinical chat.

Registries, recruiting studies and public-input notices form a separate unranked participation tier suppressed on stop routes. No contact, enrollment or submission occurs. Inactive semantic LactMed search returns `not_enabled`.

Abstract disclosures are application metadata, not source-authored medical findings. Every client must preserve them. The bundled Python and PowerShell clients enforce them; an arbitrary third-party client may not.

## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Existing app: [mcp-mc](https://mcp-mc-7474654188777746.aws.databricksapps.com). Unchanged deployed policy .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. Local source policy: `2026-11-21.10`; grader: `3.0`.

Application changes are in this submission folder’s `server` and `chat-client`; fresh evaluation evidence is in `evaluation/abstract-disclosure-revision`. See [source changes](evaluation/abstract-disclosure-revision/source-changes.diff), [capture lineage](evaluation/abstract-disclosure-revision/capture-lineage.json), [implementation](documentation/CURRENT_IMPLEMENTATION.md), [Databricks validation](documentation/DATABRICKS_VALIDATION.md) and [technical review](evaluation/abstract-disclosure-revision/TECHNICAL_REVIEW.md). This version is not deployed. No GitHub destination has been selected.
