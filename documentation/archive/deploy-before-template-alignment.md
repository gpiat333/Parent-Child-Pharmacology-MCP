> Current status: local policy .10, deployed .9 unchanged. Fresh chats and paired answers, unchanged grader v3. 592 server and 30 grader tests pass. No deployment or GitHub upload. See [current validation](DATABRICKS_VALIDATION.md). Earlier numbers and deployment statements below are historical.

> Historical record. Current local code has 508 tests, 30 tools, four prompts and four resources; see [current implementation](CURRENT_IMPLEMENTATION.md). Historical names and counts remain below.

> Historical notes retained for traceability. The current local revision is documented in CURRENT_IMPLEMENTATION.md, the evaluation DOCX and ../evaluation/results.json. No deployment was performed.

# mcp-mc deployment

## Extended evaluation fixes — latest November 17, 2026 deployment

Sanitized exception envelopes, application logging and audit error categories;
disabled request logging and filtered library exception details. Added empty-name
validation, atomic-only combination ingredients, LactMed record-boundary parsing
and no whole-page fallback. Added trial relevance metadata, grant abstracts and
explicit FAERS cohort limits. Follow-up probes prompted strict PMID validation
and recognition of the valid legacy Nursing Mothers SPL code.

Validation: 30 local tests passed; 17 deployed edge/regression checks plus an
offline synthetic privacy probe passed; final five-tool deployed smoke passed.
The privacy tests include mocked audit writes; production/platform logs and a
live Delta audit table were not inspected, and historical logs were not purged.
Twenty-one chat turns completed (48 tool calls, median 7.34 seconds) before the
last PMID/legacy-code patch. Those two final changes were checked with three
targeted deployed calls and the final smoke suite, not another full chat batch.
Search relevance and clinical grounding remain limited; no clinical validation
or perfect answer-quality score is claimed.

Executed the same bundle validate/deploy/run commands documented below. Final
deployment source ID: 01f1e29e3efa1510be442b34e0332a1b. App remains live-only at
https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp.
No input signatures/tool names changed; no additional compute resources created.

Companion workspace commands:

```powershell
.\test-mcp-edge-cases.ps1 -OutputPrefix fixed-direct
.\run-extended-evaluation.ps1 -RunPrefix fixed
& 'C:\Users\piatkowskigs\Documents\mcp-mother-child\.venv\Scripts\python.exe' .\test-error-privacy.py fixed-privacy-results.json
.\test-mcp-edge-cases.ps1 -OutputPrefix final-targeted -OnlyIds 15-upstream-error,16-legacy-label,17-valid-abstract
python .\verify-fixed-results.py
.\test-deployed-mcp.ps1
python .\build-fixed-report.py
```

Before/after evidence and remaining limitations are in the companion project's
presentation-evidence/fixed-evaluation-report.html. The local client also received
stricter refusal/source-directive instructions; those do not automatically apply
to other chat clients.

## Evaluation fixes deployed — November 17, 2026

Updated mc/sources.py and server.py: classify explicit DailyMed section titles and
flag source code/title mismatches; verify RxNorm identity and require confirmation
of approximate matches; stop composite briefs for unconfirmed identities; validate
LactMed numeric IDs; improve retrieval instructions; include FAERS query URLs and
timestamps. Tool names and input signatures are unchanged. Source fields were added.
The fluoxetine SPL itself contained incorrect section codes; the fix does not
silently treat the original machine-readable code as reliable when titles disagree.

Executed from this project directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle validate --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle deploy --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle run mcp_mc --profile gsa-mcp-hackathon
```

Validation passed (only absent .env exclusion warnings). Deployment updated two
files and created no compute resources. App start succeeded at
https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp.
Final unit suite: 13 passed, including 8 new regression tests. Five deployed smoke
checks passed. From the companion project directory, executed:

```powershell
.\test-deployed-mcp.ps1
.\run-chat-evaluation.ps1 -RunPrefix retest
python .\build-retest-report.py
```

Ten chat retests completed, 25 tool calls, median 11.33 seconds. Qualitative review:
6 pass, 4 partial, 0 fail (not a clinical accuracy metric). Retrieval relevance and
unsupported general statements in safety refusals remain open. Original evidence
is preserved under the companion project's presentation-evidence folder; see
chat-retest-report.html. The local chat-client prompt and deterministic disclaimer
formatter do not automatically apply to other MCP clients or Playground.
RxNorm exact-match semantics were checked against
https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.findRxcuiByString.html (search=0).

## Current status — November 17, 2026

Follow-up verification: a Windows PowerShell MCP client completed initialization,
listed all 13 tools / 3 prompts / 1 resource, and successfully called normalize_drug,
search_lactmed, get_lactmed_record, get_label_sections, and medication_safety_brief.
It used the CLI OAuth token in memory and Windows default HTTPS certificate
verification. No TLS bypass was used. Python's separate certificate-store problem
remains, but it no longer blocks this Windows-based smoke-test route.
Script and full results are saved in the companion local workspace:
C:\Users\piatkowskigs\Documents\ChatGPT\Mother-Child-MCP\test-deployed-mcp.ps1
and deployed-mcp-test-results.json. These are smoke checks, not clinical validation
or full agent evaluation. The selected DailyMed label returned no lactation field;
the composite brief returned no general education topics but two drug-info entries.

The credit restriction no longer blocked deployment. Re-ran bundle deploy and
bundle run mcp_mc with profile gsa-mcp-hackathon. Both succeeded. The app is running
in live-only mode on the approved MEDIUM app compute.

App URL: https://mcp-mc-7474654188777746.aws.databricksapps.com

MCP endpoint: https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp

Startup logs confirmed HTTP responses from all nine requested public-source hosts.
Root-path responses included 200, 301, 302, and 404; these establish reachability,
not successful API queries or redirect-destination access.

The authenticated local smoke test was attempted but failed before MCP initialization:
Python/httpx reported CERTIFICATE_VERIFY_FAILED (self-signed certificate in chain).
Certificate verification was not disabled. End-to-end tool results remain unverified.
Resolve local certificate trust or test from approved Databricks compute next.

Additional commands used:

```powershell
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' auth profiles
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle deploy --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle run mcp_mc --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' apps logs mcp-mc --profile gsa-mcp-hackathon --search EGRESS_CHECK --tail-lines 30
```

For the smoke test, an OAuth token from auth token was passed only through the
child process environment and removed afterward; no token was printed or saved.
The command was:

```powershell
.\.venv\Scripts\python.exe smoke_test.py 'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp' sertraline
```

The November 16 notes below are historical, superseded by the current status.

## Status — November 16, 2026

Deployment blocked: workspace credits exhausted. Databricks rejected app creation
with HTTP 400 BAD_REQUEST: "Sorry, cannot run Databricks App because you've
exhausted your available credits. Please add a payment method to upgrade your
account."

No final app URL is available. Do not treat an inferred URL as a deployed app.
The workspace administrator must restore credits or provide an enabled workspace.
No payment method was added and no warehouse, cluster, or vector endpoint was created.

## Configuration

- Workspace: https://dbc-aae0ba16-8727.cloud.databricks.com
- CLI profile: gsa-mcp-hackathon
- CLI version: 1.26.0
- App name: mcp-mc; description: MCP service
- Mode: live APIs only, USE_LAKEHOUSE=false
- Requested app compute: MEDIUM (user approved app compute)
- No warehouse binding or scheduled job in this initial bundle.
- Original YAML files preserved locally under .deployment-backup (excluded from upload).
- Startup checks nine public-source hosts and logs only host, status, or error type.
  These checks have NOT run on Databricks because compute could not be created.
- App files uploaded to /Workspace/Users/gabriela.piatkowski@nih.gov/.bundle/mcp-mc/dev/files.
  Neutral app naming does not hide source contents from authorized workspace readers.

## Commands used

Run from C:\Users\piatkowskigs\Documents\mcp-mother-child in PowerShell.

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle validate --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle deploy --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' apps get mcp-mc --profile gsa-mcp-hackathon --output json
```

Validation passed with warnings about exclusion patterns matching absent files
(.env, .env.*, deploy.md before this document existed). All five unit tests passed.
Deployment uploaded 11 files, deleted zero files, then failed creating the app.

## Resume after credits are restored

Repeat validation and deployment, then run (not yet executed):

```powershell
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle run mcp_mc --profile gsa-mcp-hackathon
```

Inspect deployment/compute status and startup egress logs; resolve any blocked hosts.
Read the actual app URL from Databricks and smoke test its /mcp endpoint using OAuth
without printing or saving tokens in project files. Live smoke tests, ingestion,
vector indexes, permissions and lakehouse verification remain pending.

## November 17 follow-up: OTC label and refusal fixes

Deployment 01f1e2a0103b1f928496a02d103ea1f7 is RUNNING, live-only.
DailyMed parser now retains combined OTC pregnancy/lactation warnings (LOINC 53414-9), rejects empty headings, and reports missing standalone sections plus product scope. Cetirizine lookup now returns its OTC product and source URL; standalone pediatric coverage remains unavailable for that selected label. No formulation substitution was made.
Companion test-mcp-chat.ps1 now uses explicit concise refusal instructions. This client-side prompt does not automatically configure third-party chat clients.
Validation: 35 local tests, five deployed label checks, five deployed smoke checks passed; 12 targeted chat executions completed and reviewed. Original 100-test records preserved.
Commands used after edits, from project root:
.\.venv\Scripts\python.exe -m pytest tests -q
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle validate --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle deploy --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle run mcp_mc --profile gsa-mcp-hackathon
Evidence: companion presentation-evidence/otc-fix-report.html. No additional compute created.

## November 17 source-fidelity follow-up

Deployment 01f1e2a1744d161f9026ccf268b16957 succeeded. Updated get_lactmed_record and search_trials tool descriptions to separate monitoring recommendations from observed outcomes and require study-specific links plus distinct status groups. Companion test-mcp-chat.ps1 system instructions enforce the same requested behavior through prompting. No public signatures or infrastructure changed.
Commands used: .\.venv\Scripts\python.exe -m pytest tests -q; Databricks CLI bundle validate, bundle deploy, and bundle run mcp_mc, each with --profile gsa-mcp-hackathon (same executable path documented above).
Validation: 35 existing local tests passed; five deployed smoke checks passed; four questions repeated three times (12 chat runs) met targeted source-fidelity checks. 28 listed-study link occurrences matched captured source records. Six LactMed responses used untruncated record text. These results are not clinical certification or independent clinical review.
Evidence: companion presentation-evidence/fidelity-report.html, fidelity-summary.json, and fidelity-*-results.json. Historical trial selection remains variable and can include background-treatment studies; clinically representative external review remains outstanding.

## November 17 gold-evaluation follow-up
Deployment 01f1e2a92d61191d8390bc90b79153de succeeded. Added partial-chronology guidance to get_lactmed_record. No signatures, source parser, resources or permissions changed. Used documented CLI bundle validate/deploy/run mcp_mc commands with gsa-mcp-hackathon profile. 35 tests and five final deployed smoke checks passed. Companion chat client handles one disclaimer and source review. Timeline uncertainty wording remains imperfect in targeted repetitions; do not claim fully resolved clinical fidelity. See companion evaluation/v2/fix-status.html for all results and limitations.

## November 17 FDA pediatric labeling tool
Deployment 01f1e2c6535f19f0b45332da44ba1c58 succeeded. Added search_pediatric_labeling_changes via mc/pediatric_labels.py and openpyxl read-only parsing. MCP now 14 tools. Validation: 49 unit tests, nine deployed checks and one source-checked chat passed. Commands: .venv\Scripts\python.exe -m pytest tests -q; documented Databricks CLI bundle validate, bundle deploy, bundle run mcp_mc with gsa-mcp-hackathon profile. No resource changes. FDA workbook cached up to one hour; schema failures fail closed. Source/data-scope notes and MPRINT API investigation: companion evaluation/fda-mprint/report.html. MPRINT remains inferred search; published dataset integration is not implemented.

## November 17 direct MPRINT data integration
Deployment 01f1e2c8874210f2991be5ee073445ed succeeded. Added search_mprint_gold and get_mprint_silver_classifications with read-only SQLite snapshot of published Gold study metadata and Silver PMID study-type labels, revision 4bdee90dff3610816e86d0eed29b4c4d0fe76e89. 16 tools total. 63 unit tests and 13 deployed checks passed, plus final two-tool chat. Initial oversized snapshot fixed using WITHOUT ROWID compaction; original-case fields nested to avoid case-insensitive JSON client collisions. No paid compute or permissions created. Commands: .venv\Scripts\python.exe -m pytest tests -q; documented Databricks CLI bundle validate/deploy/run mcp_mc --profile gsa-mcp-hackathon. Snapshot refresh builder and provenance: companion build-mprint-snapshot.py and evaluation/mprint-integration/. Limits: no Gold outcomes or Silver drug/population mapping tables; no live portal API claim.

## November 17 MPRINT labels, identity, filters and outcomes
Deployment 01f1e2ceb2f91e24aa0d730f195b8f4b succeeded; 17 tools. search_mprint_gold gains optional population/study_type/resolve_names; new get_mprint_gold_outcomes exposes paginated PE_CT and PK_summary rows. Read-only outcome shards retain provenance and null/value/unit semantics; strict source-context joins flagged when missing. 87 tests and 18 deployed checks passed; two chat runs completed with one extra unreturned RxCUI identifier flagged in brand answer. Commands: project .venv\Scripts\python.exe -m pytest tests -q; documented CLI bundle validate/deploy/run mcp_mc --profile gsa-mcp-hackathon. No new compute/grants. Details and reproduction scripts: companion evaluation/mprint-expanded/report.html and extend-mprint-outcomes.py, split-mprint-outcomes.py.

## November 17 MPRINT export interpretation fix
Deployment 01f1e2d75bf413ceafa897aa1154caaf succeeded. Outcome responses now label interpretation/linkage guidance as MCP implementation guidance and scope nulls to missing fields in the export, without implying absence in the original paper. No tool names or signatures changed. Companion chat generation and review prompts follow the same rules; they do not configure third-party chat clients.
Validation: 87 unit tests and 18 deployed checks passed, including new live guidance assertions. Commands: .venv\Scripts\python.exe -m pytest tests -q; documented Databricks CLI bundle validate, bundle deploy, bundle run mcp_mc --profile gsa-mcp-hackathon; companion test-mprint-v2.ps1. Bundle deployment changed no infrastructure. App URL: https://mcp-mc-7474654188777746.aws.databricksapps.com . Versioned chat/MLflow artifacts are in companion evaluation/mprint-mlflow-v2; see its report for final scoring rather than assuming all checks passed.

## November 17 empty-result abbreviation fix
Deployment 01f1e2d9355e155d8bc201fd19326671 succeeded. All MPRINT snapshot responses now include a classification legend, including empty outcome searches; PE is explicitly pharmacoepidemiology. Shared metadata also identifies implementation-authored guidance. Companion review instructions prohibit guessing abbreviation meanings from filenames or memory. Added regression test for empty-result labels. 88 unit tests and 18 deployed checks passed. Live PubMed search/abstract and ClinicalTrials.gov search checks also passed before this MPRINT-only update. No tool signature or infrastructure changes. Used the documented bundle validate/deploy/run commands and companion test-mprint-legend.ps1. Full unchanged-criteria chat/MLflow evidence: companion evaluation/mprint-full-retest (pre-fix) and evaluation/mprint-legend-retest (post-fix). Preserve both runs; consult saved scores and manual findings.

## November 17 broad-source quality fixes
Deployment 01f1e2dd4e4d1f4b94ff494401105df9 succeeded. search_mprint_gold now accepts an optional exact PMID and permits omission of drug for that lookup; old drug-name calls remain compatible. PubMed search responses include the public source request URL, including empty results, with the same filters used for retrieval; abstracts include canonical article URLs. Trial interventions retain original names and add name_without_strength for dose-free display. Companion chat routing/review instructions use these fields; evidence-free replies retain a disclaimer without claiming retrieved-source compilation. Third-party clients do not automatically inherit the companion prompt or footer.
Validation: 105 Python tests, disclaimer-format checks and 22 deployed checks passed. Commands: .venv\Scripts\python.exe -m pytest tests -q; documented Databricks CLI bundle validate, bundle deploy, bundle run mcp_mc --profile gsa-mcp-hackathon; companion test-chat-output.ps1 and test-broad-fixed.ps1. No infrastructure or permission changes. Same 32-case broad-source benchmark and grading rules retained in companion evaluation/broad-source-fixed; consult its final report for scores and remaining limitations. App: https://mcp-mc-7474654188777746.aws.databricksapps.com .

Follow-up: the 32-case capture exposed an overbroad companion routing instruction selecting Gold metadata for outcome rows (S04). Narrowed the client instruction without changing the server deployment. Repeated the unchanged C03 metadata and S04 outcome questions; both passed all seven checks in MLflow run 76c2e13731fe4321896ba57241e926a1. Original 32-case results are retained separately; this two-case follow-up is not a complete rerun of the final client. Artifacts: companion evaluation/broad-routing-followup. Python tests and footer checks remained passing.


## NICHD discovery update — 2026-11-17
Added search_bpca_evidence and search_nichd_studies in mc/nichd.py. BPCA returns summary links only; DASH returns public metadata and access notes. No controlled data or new compute.
Commands run from the server project using the existing Databricks CLI: `bundle validate --profile gsa-mcp-hackathon`, `bundle deploy --profile gsa-mcp-hackathon`, `bundle run mcp_mc --profile gsa-mcp-hackathon`.
Validation: `.venv\Scripts\python.exe -m pytest tests -q` — 120 passed. Companion `test-nichd-deployed.ps1` — 8 checks passed. Two chat probes completed; not a new MLflow evaluation.
Final URL: https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp

## Parent-facing features — 2026-11-19

Deployment `01f1e454a38712f8a49faa6f0b8a9654` started successfully on the existing
`mcp-mc` app. Eight new tools bring the total to 27; existing public signatures
remain unchanged. Added `mc/parent_safety.py`, `mc/parent_resources.py`, shared
safety metadata and identifying-input checks in `mc/audit.py`, participation
fields in trial results, and updated parent workflow prompts/source documentation.

Companion client changes: mandatory routing before model generation, identity/error
gates, narrow output-boundary checks, exact citation rendering and opt-in synthetic
trace capture (`-SaveTrace`). See `PARENT_FEATURES.md` for source limitations and
the distinction between companion enforcement and third-party clients.

Commands executed from the server root:

```powershell
.venv\Scripts\python.exe -m pytest tests -q
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle validate --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle deploy --profile gsa-mcp-hackathon
& 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe' bundle run mcp_mc --profile gsa-mcp-hackathon
```

Validation before deployment: 168 Python tests, 11 client-policy checks and 7
citation checks passed. Six live-source probes passed. Bundle deployment reported
zero resources created/changed/deleted. Deployed endpoint/chat acceptance results
are recorded separately in the companion `evaluation/parent-features/` directory;
consult its final report rather than assuming deployment implies all checks passed.
No new MLflow benchmark or independent clinical validation is claimed.

Follow-up deployment `01f1e459a1841bd884aad91383ed0819` succeeded using the same
bundle deploy/run commands. Parent wording such as "children's ibuprofen" now
uses separate escaped product terms. Federal Register uses plain subject search,
candidate filtering and per-notice details for deadlines/submission text. These
fix false-empty results found during manual chat review. Final server regression
run: 170 passed; final deployed checks: 18 passed. Client tests: 12 policy checks
and 7 citation checks passed. Ten initial synthetic chats completed; targeted
recall/public-input follow-ups are retained separately. A final client-only
attribution instruction distinguishes MCP limitations from FDA/NIH statements.
See companion `evaluation/parent-features/report.html` for exact final outcomes.

November 19 expanded-test follow-up: deployment `01f1e45bcdda1930a6a30df11b35e321`
succeeded after `bundle validate`, `bundle deploy` and `bundle run mcp_mc` with the
same CLI/profile above. No resources were created or changed. Two unmatched `.env`
exclusion warnings were reported by validation. Updated routing covers “the wrong
medicine” and “blood pressure medicine.” Local regression: 173 passed; routing
challenges: initial 46/48 then 48/48; deployed acceptance after restart: 18/18.
The companion client separately fixes trace saving before preflight completion.
See `METHODOLOGY.md` and companion `evaluation/parent-expanded/report.html`.

November 19 selection/explanation fixes: deployment
`01f1e460818a1da1b370b6a4e47f76ca` succeeded with the same bundle validate/deploy/run
commands and profile. No resources created or changed. Policy version is
`2026-11-19.2`; explicit exclusions such as “Do not give a dose” no longer suppress
research. Separate actual treatment/urgent/identity requests remain gated. Trial
and public-input responses add literal relevance metadata; trial responses also
return registry study type. Existing tool names/signatures remain unchanged.
186 unit tests and 18 deployed checks passed. Companion citation repair and
evaluation calibration changes are recorded in `evaluation/selection-fixes/` in
the companion project; see its report for raw results and remaining judge limits.


2026-11-19 correction deployment: `databricks bundle deploy --profile gsa-mcp-hackathon`, followed by `databricks bundle run mcp_mc --profile gsa-mcp-hackathon` (CLI 1.26.0). Active deployment `01f1e4656e0c107e949cdadb1f6d24a8`; live-only; no compute resources created. Endpoint https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp. Validation: 215 unit tests, 21 deployed checks.

## 2026-11-20 validation contract deployment

Deployment `01f1e53dd5881e4b8ed6111cd924fc14` started successfully on the existing
`mcp-mc` app. Added `mc/contracts.py`, stricter input schemas, typed common output
metadata and clearer tool-selection descriptions. Inputs are intentionally stricter;
names and parameter names/defaults are unchanged. See METHODOLOGY.md for migration details.

Commands: `bundle validate --profile gsa-mcp-hackathon`, then
`bundle deploy --profile gsa-mcp-hackathon`, then
`bundle run mcp_mc --profile gsa-mcp-hackathon`, using the same CLI path above.
Validation had only existing unmatched .env/.env.* exclusion warnings. Deployment
uploaded 4 files; 0 resources created, changed or deleted. Final local suite:
250 passed. Live checks: 36/36 contract checks and 21/21 source/safety checks.
Final endpoint: https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp
