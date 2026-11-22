# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

The existing **mcp-mc Databricks sandbox app was updated** with the routing fix on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks. NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report](evaluation/brief-paraphrase-revision/REPORT.md) and [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/5b578ac30be1410380b9b144f0c54ed6).

## Routing fix and verified results

The missed “Give me a pregnancy evidence brief for lamotrigine” request now requires `medication_evidence_brief` first. Give/show/send variants share object grammar with their negations. All **12 separate deployed routing probes passed**, and the original missed question completed with the brief as the first evidence tool. Whole-question stops still take priority. These checks are separate from the unchanged 28-case benchmark; matching remains heuristic.

Fresh local suite: **531 tests passed**, including 23 new routing regressions, with zero failures, errors or skips. All **93 deployed runtime files** match the staged source; 112 server/client files were frozen. Active inventory: **30 tools, four prompts and four resources**. Runtime checks: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures, retaining partial/empty statuses.

Chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. First-attempt completion: 28/28. Completed answers were not regenerated.

Research grades across 21 answers: **21 fidelity passes**, 0 failures, 0 N/A; **18/21 tasks fulfilled**. URL membership: 21/21. Paired task fulfillment: **MCP 5/7, plain model 0/7**. Paired fidelity pass/fail/N/A: MCP 4/3/0; plain 2/4/1. All **42 final MLflow rows** were read back with applicable scores and zero assessment errors.

## What the grades mean

Fidelity means support in the captured reference pool; task fulfillment means meeting the requested lookup or output requirements. These are separate model judgments. The plain model has no retrieval tools, so honest abstention can leave a source-lookup task incomplete. Zero fulfilled tasks does not mean every statement was false. N/A is excluded from fidelity rates. URL membership is not claim support.

Known development questions, one retained completed sample each, changing sources, a same-family judge, bounded references and no clinician adjudication limit interpretation. Only MCP has retrieval, workflow enforcement and fixed notices. Raw negative grades remain visible. This compares workflows, not isolated model ability or clinical accuracy; no speed advantage is established. Required notices do not eliminate false reassurance or harmful framing.

The preceding Databricks .4 run remains under `evaluation/databricks-validation-2026-11-21` with 508 local tests, 19/21 fidelity and 19/21 tasks; its paired tasks were MCP 7/7 and plain 0/7. Earlier local runs also remain. These are historical totals. Saved demo images and video illustrate the prior .4 revision, not current .5 validation. The deck has 49 slides: 15 main and 34 hidden appendix slides.

## Research and evidence contracts

RePORTER supports IC, fiscal-year array, activity-code and organization filters plus bounded portfolio aggregates. Literature exposes type/date filters and access metadata. Trials expose direct NCT lookup and results-posted flags. Count-only coverage, RxNorm ingredient-product navigation and federal shortage records have narrow discovery scopes.

The evidence brief retains three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant exposure, and observed fetal/infant outcomes. Empty rows remain visible. PLLR subsections, maternal PK, missing/truncated sections, source populations, label provenance, study-count uncertainty, FAERS caveats and MPRINT snapshot dates stay explicit. **LactMed is lactation-only**; its alternatives section is excluded. Pregnancy findings come from labeling and literature.

No prescribing or personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Every client must enforce preflight and display contracts. Workflow matching and language detection remain heuristic. Spanish safety/referral strings remain held for human review. Source-authored MedlinePlus Spanish education is separate from clinical chat.

Registries, recruiting studies and public-input notices form a separate unranked participation tier suppressed on stop routes. No contact, enrollment or submission occurs. Inactive semantic LactMed search returns `not_enabled`.

## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Current app: [mcp-mc](https://mcp-mc-7474654188777746.aws.databricksapps.com). Deployment: `01f1e5db4fd3177ab9374d54fe273ff9`. Policy: `2026-11-21.5`.

The changed code is in `server/core/workflows.py`, `server/core/policy.json`, `server/core/output_notices.json` and `server/tests/test_brief_workflow.py`. Existing required notices and URL checking remain active. Full reference evidence and tool-call traces are MLflow artifacts; each precomputed evaluation row has one root span. Existing CLI sign-in supplies refreshable authentication.

See [current implementation](documentation/CURRENT_IMPLEMENTATION.md), [Databricks validation](documentation/DATABRICKS_VALIDATION.md), [contracts](documentation/SAFETY_AND_EVIDENCE.md) and [technical review](evaluation/brief-paraphrase-revision/TECHNICAL_REVIEW.md). Prior evidence and source snapshots remain preserved. No GitHub destination has been selected.
