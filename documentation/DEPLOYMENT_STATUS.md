# What is running, what was tested, and what deployment means

**A GitHub push updates files. An application deployment changes the service users connect to.** Those are separate actions in this project. The current work updates source, tests, documentation and submission materials; it does not replace the running Databricks App.

| Component | Current state | What changes when released |
|---|---|---|
| Private GitHub repository | Holds the revised source and submission artifacts; Windows/Linux CI tests the committed package | A push changes repository contents, not the live MCP service |
| Local MCP service | Started on loopback for fresh evaluation, then stopped | A local test process is not a shared hosted service |
| Databricks test notebook | Runs the revised application tests in an isolated job environment | Uploading a test bundle and running a notebook does not install it into the App |
| Databricks model gateway | Supplies model calls for evaluations using the existing model configuration | This work does not create or redeploy a model endpoint |
| Databricks MLflow | Stores runs, scores, traces and reviewed artifacts | Logging an experiment does not serve the MCP or change its App deployment |
| Databricks App `mcp-mc` | **Version 0.22.1, policy .29**, deployment `01f1e79f035f1322ab77836385f218a6` (November 23, 2026), from `/Workspace/Users/<owner>/apps/mcp-mc-v0221` | Redeploy from a new staged folder; the 0.22.0 (`mcp-mc-v0220`) and .27 (`mcp-mc-policy27`) folders stay available for rollback |
| Companion chat client | Revised local client scripts and output contracts | Any hosted client must be updated too; the server cannot force an arbitrary client to enforce its safety/display contracts |

## What a future hosted release would involve

1. Choose the evaluated source commit and package its dependencies, policy, bundled MPRINT snapshots and required configuration together. Confirm the intended transport and compute/runtime support.
2. Configure the host's access and network controls. The revised server defaults to local stdio; remote HTTP requires the documented operator-managed RS256 issuer, public key, audience and tool scopes. Existing Databricks gateway access alone is not proof that the new server's bearer-token contract is configured. Confirm how the gateway/client obtains and supplies the appropriate server token without broadening access.
3. Configure secrets through the hosting environment, permitted outbound source access, logging/trace retention and the intended user audience. Do not put credentials into source, demo traces or the submission package.
4. Deploy the selected package to the hosted App and update the intended companion/client configuration. Keep the old release available for rollback.
5. Run hosted protocol, authentication/authorization, source-connectivity, fixed-stop, display-contract and fresh chat checks against that exact deployment. Local tests, Databricks notebook tests and CI do not replace hosted integration checks.

No new model training, new model endpoint, new database, or public GitHub release is inherently required for these code changes. Spanish chat also does not become supported merely by deploying the package: its review prerequisites remain separate in [Language support](LANGUAGE_SUPPORT.md).

 This work makes no production-readiness, penetration-test or clinical-certification claim. [Security requirements](../SECURITY.md) and the [latest evaluation index](../evaluation/README.md) record remaining boundaries.

## November 23, 2026 deployment (policy .26)

**Access control.** The app runs with `MCP_AUTH_MODE=databricks_apps` (set in `deploy/databricks/app.yaml`). This mode takes effect only inside Databricks Apps: workspace sign-in is the access control, which is Databricks' own pattern for MCP servers hosted on Databricks Apps. Every `/mcp` request must carry the identity header the Databricks front door adds after sign-in; `/health` and `/version` stay open for platform probes. Per-tool scopes are not checked in this mode. Outside Databricks, remote HTTP still requires the RS256 token issuer described in the kit. Only people with permission on the app can reach it.

**What was staged.** `src/` (including the bundled LactMed, MotherToBaby and MPRINT snapshots), `main.py`, `requirements.txt`, `server/requirements.lock` and `app.yaml`. No `.env`, tests, evaluation captures or credentials.

**Checks on the deployed app** (November 23, 2026, signed in through the Databricks CLI):

| Check | Result |
|---|---|
| `/version` | 0.19.0, policy 2026-11-23.26 |
| `/health` | healthy |
| Request without workspace sign-in | Redirected to Databricks login (HTTP 302) |
| MCP `initialize`, `tools/list` | OK; 31 tools |
| `route_parent_question`, "I'm breastfeeding. Can I take ibuprofen?" | evidence route with the clinician message |
| `route_parent_question`, Spanish question | Stops with the Spanish message (`message_es`) |
| `normalize_drug` Zoloft (live RxNorm) | sertraline |
| `search_lactmed` sertraline (live NCBI) | Sertraline record found |
| `find_mprint_records` update check (live GitHub) | up_to_date |

These are smoke checks, not a hosted re-run of the model-graded evaluation; the scored results describe policy .25 run on a local server. No load or penetration testing was done.

**Rollback.** `databricks apps deploy mcp-mc --source-code-path <previous folder>` redeploys an earlier version; the .9 source remains at its original bundle path.

## November 23, 2026 redeployment (policy .27)

Hands-on testing in Claude found that “What does LactMed say about sertraline and breastfeeding? Link the studies.” was blocked as non-English. Policy .27 fixes the language check and adds a landing page at `/`. Redeployed as `01f1e77b7f631005b51803936dbda628` from `/Workspace/Users/<owner>/apps/mcp-mc-policy27`; the .26 folder remains for rollback. Checks on the hosted app: `/version` 2026-11-23.27; `/` shows the landing page; the LactMed question, “List FDA recalls for naproxen.” and “Thanks! Now do the same for escitalopram.” route to evidence; a Spanish question still stops with the Spanish message.

## November 23, 2026 redeployment (0.22.0, policy .28)

The 21-tool version was deployed after its tests passed in a Databricks serverless notebook: 1,048 tests, no failures, errors or skips (run 836082121861576; [receipt](../evaluation/databricks-validation-2026-11-23-v0220/databricks-job-output.json)). Source commit `e7e7dff` was staged to `/Workspace/Users/<owner>/apps/mcp-mc-v0220` (`src/`, `main.py`, `requirements.txt`, `server/requirements.lock`, `app.yaml`) and deployed as `01f1e79696a9180baea31889672e81f2`. Access control is unchanged (`MCP_AUTH_MODE=databricks_apps`).

| Check on the hosted app | Result |
|---|---|
| `/version` | 0.22.0, policy 2026-11-23.28 |
| `/health`, landing page | healthy; 200 |
| Request without workspace sign-in | Redirected to Databricks login (HTTP 302) |
| MCP `initialize`, `tools/list`, resources | OK; 21 tools; 5 resources |
| `route_parent_question`, "I'm breastfeeding. Can I take ibuprofen?" | evidence route with the clinician message |
| `route_parent_question`, Spanish question | Stops with the Spanish message (`message_es`) |
| `route_parent_question`, "I keep thinking about hurting my baby" | mental_health_support |
| `route_parent_question`, "sertraline" | evidence (no longer language-blocked) |
| `normalize_drug` Zoloft (live RxNorm) | sertraline |
| `get_lactmed_record` by drug name, sertraline (live NCBI) | Sertraline record with cited-study links |
| `search_fda_drug_notices` recalls, naproxen (live openFDA) | 2 results |
| `search_trials` recruiting_only, pediatric ADHD (live ClinicalTrials.gov) | participation listing, 2 studies |
| `medication_evidence_brief` sertraline, lactation (live) | summary, about 68,000 characters; axis totals 19, 31 and 24 |
| `find_mprint_records` update check (live GitHub) | up_to_date |

These are smoke checks, not a hosted run of the model-graded evaluation. **Rollback:** `databricks apps deploy mcp-mc --source-code-path /Workspace/Users/<owner>/apps/mcp-mc-policy27`.

## November 23, 2026 redeployment (0.22.1, policy .29)

After the 0.22.0 evaluation, version 0.22.1 corrected how answers attribute server notices and recall contacts. It was evaluated in full ([report](../evaluation/v0221-final/REPORT.md)), passed 1,050 tests in a Databricks serverless notebook with no failures, errors or skips (run 1020002982130560), and was deployed from commit `8ff5926` as `01f1e79f035f1322ab77836385f218a6` from `/Workspace/Users/<owner>/apps/mcp-mc-v0221`. The hosted App now runs the same version the evaluation scored; the scored run itself used a local server.

The same smoke checks as the 0.22.0 deployment were repeated on the hosted App and all passed: `/version` reports 0.22.1 and policy 2026-11-23.29; an unauthenticated request is redirected to Databricks login; 21 tools and 5 resources are listed; crisis, Spanish, personal-question and short-English routing behave as expected; and live calls to RxNorm, LactMed, openFDA recalls, ClinicalTrials.gov, the evidence brief and the MPRINT update check returned results. **Rollback:** `databricks apps deploy mcp-mc --source-code-path /Workspace/Users/<owner>/apps/mcp-mc-v0220`.
