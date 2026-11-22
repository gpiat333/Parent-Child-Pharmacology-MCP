# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

The existing **mcp-mc Databricks sandbox app was updated** on November 21, 2026 at the user's request. No GitHub push or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. The evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks. The 508 unit tests are the prior verified local baseline on unchanged source, not a new remote unit run. NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report](evaluation/databricks-validation-2026-11-21/REPORT.md), and [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/cfad8c43ac3d4124922713c4c8124cae).

## Current verified results

Local unchanged-source baseline: **508 unit tests passed** with no failures, errors or skips. Active Databricks inventory: **30 tools, four prompts and four resources**. All **93 deployed runtime files** match the staged source; all 112 frozen server/client files remain unchanged. Runtime probes: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures (including partial/empty statuses).

Final chats: **28/28 completed**, 28/28 expected routes and 28/28 required/allowed tool checks. Seven fixed stops made zero downstream evidence/model calls. Initial completion was 24/28; four HTTP 429 attempts were archived before sequential retry. Completed answers were not regenerated.

Research grades: **19 fidelity pass, 2 fail, 0 not assessable; 19/21 tasks fulfilled**. URL membership: 21/21. Paired tasks: **MCP 7/7, plain 0/7**. Paired fidelity pass/fail/N/A: MCP 5/2/0; plain 1/5/1. N/A is excluded from fidelity rates. All **42 final MLflow rows** were read back with applicable scores and zero assessment errors.

These are known development cases, one completed sample each, with changing sources, a same-family diagnostic judge, bounded references and no independent clinician adjudication. Only MCP has retrieval, workflow enforcement and fixed notices. URL membership does not establish claim support. Neither clinical accuracy nor a speed advantage is established. An extra ‘Give me a pregnancy evidence brief…’ paraphrase failed to select the required workflow; this remains outside the unchanged 28-case benchmark. Required notices do not eliminate false reassurance or harmful framing.

The two required application notices and corrected URL parser remain active. Before-notice answers and notice IDs are retained. The earlier local evaluation remains under `evaluation/notice-citation-revision`; its 20/21 fidelity and 17/21 task results are historical. The deck has 49 slides: 15 main and 34 hidden appendix slides. Existing [demo images/video](presentation/current-demo/index.html) replay the predeployment local run of this same source and are labeled accordingly.

## Research and evidence contracts


RePORTER supports IC, fiscal-year array, activity-code and organization filters plus bounded portfolio aggregates. Literature exposes type/date filters and access metadata. Trials expose direct NCT lookup and results-posted flags. Count-only coverage, RxNorm ingredient-product navigation and federal shortage records have narrow discovery scopes.

The evidence brief retains three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant exposure, and observed fetal/infant outcomes. Empty rows remain visible. PLLR subsections, maternal PK, missing/truncated sections, source populations, label provenance, study-count uncertainty, FAERS caveats and MPRINT snapshot dates stay explicit. **LactMed is lactation-only**; its alternatives section is excluded. Pregnancy findings come from labeling and literature.

No prescribing or personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Every client must enforce preflight and display contracts. Workflow matching and language detection remain heuristic. Spanish safety/referral strings remain held for human review. Source-authored MedlinePlus Spanish education is separate from clinical chat.

Registries, recruiting studies and public-input notices form a separate unranked participation tier suppressed on stop routes. No contact, enrollment or submission occurs. Inactive semantic LactMed search returns `not_enabled`.


## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Current deployed app: [mcp-mc](https://mcp-mc-7474654188777746.aws.databricksapps.com). Deployment ID: `01f1e5d04532167f8b244e9ca79d5fe1`. Policy: `2026-11-21.4`.

Existing Databricks CLI sign-in now refreshes MLflow credentials automatically. A cached token expired during the paired run's final status update; saved results were recovered without regeneration. No administrator renewal was needed. Full reference evidence is stored as MLflow artifacts after the first pilot exceeded the assessment-value size limit. Precomputed MLflow rows have one root span; full MCP/tool traces remain JSON artifacts.

See [Databricks validation](documentation/DATABRICKS_VALIDATION.md), [current implementation](documentation/CURRENT_IMPLEMENTATION.md), [contracts](documentation/SAFETY_AND_EVIDENCE.md), and [pregnancy evidence](documentation/PREGNANCY_EVIDENCE.md). All earlier raw runs and source snapshots remain preserved. No GitHub destination has been selected.
