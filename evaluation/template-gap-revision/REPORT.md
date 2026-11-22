# Template gap revision evaluation

Current source **0.12.0**, policy **2026-11-21.12**. The existing Databricks App remains on .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. MCP/chat/paired drivers and Phoenix ran locally; models and MLflow used Databricks. A separate Databricks serverless notebook ran the frozen source tests. Code is pushed only to the existing private GitHub repository. No App deployment, access-policy change, public release or official GSA submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **686/686 locally; 686/686 in Databricks**, no failures or skips | Contract/regression tests, not clinical correctness |
| Grader tests and controls | **30/30 unit tests; 10/10 synthetic fidelity controls** | Development checks, not independent adjudication |
| MCP Inspector | **9/9 checks** | 30 tools, four prompts, four resources; bounded protocol checks |
| Fresh chat routes and tools | **28/28 expected routes; 28/28 tool checks** | Known development questions |
| Fixed stops | **7/7**, zero downstream calls | Heuristic boundaries, not triage validation |
| Research answers | **21/21 fidelity passes; 18/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain model 0/7** | Seven known questions; unequal workflow capabilities |
| Paired fidelity pass/fail/N/A | **MCP 6/1/0; plain 1/5/1** | N/A is excluded from fidelity rates |
| Citation and trace checks | **21/21 URL membership; 42 unique MLflow rows verified** | Membership is not support for a claim |
| New fixed-snapshot benchmark | **3/10 exact answers; 7/10 generated final answers** | Separate Phoenix benchmark; three conservative routing stops and other retrieval/reasoning gaps |

[Raw metrics](summary.json) · [All negative grades](TECHNICAL_REVIEW.md) · [MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/591268c202e94d44bfadb2178a33bc8d) · [Databricks notebook](https://dbc-aae0ba16-8727.cloud.databricks.com/?o=7474654188777746#job/365762992429541/run/722956547264765) · [Windows/Linux CI](https://github.com/gpiat333/Parent-Child-Pharmacology-MCP/actions/runs/44984535771)

## Changes

The .12 revision adds connection-time public-IP validation and pinned HTTPS connections with original TLS verification; fail-closed remote RS256 authorization with individual tool scopes; initialize-level guidance; JSON/Markdown outputs that preserve structured safety fields; explicit continuation metadata and PubMed offsets; staged src imports; and public SDK Tool construction without private manager mutation. Sixty-four added tests exercise these boundaries. The GSA template's 65-file audit is retained with current dispositions.

Remote hosting still requires an operator-managed issuer/public key/audience, gateway access controls and network egress policy. No firewall or identity infrastructure was provisioned. The official pinned mcp SDK and stable tool names remain documented adaptations. Sources without continuation support explicitly report unknown completeness rather than inventing cursors. A .12 deployed-App evaluation remains outstanding because this revision does not deploy the App.

## Grading limitations

Fidelity asks whether claims are supported by the captured, bounded evidence pool. Task fulfillment asks whether the requested requirements were met. They are separate, fallible same-family model judgments. Quote checks and URL membership do not establish relevance, medical truth or safety. All negative grades and raw rationales are retained; there were no manual score overrides or clinician adjudication.

The 28 development questions and seven paired questions retain grader v3 and the prior case definitions. There is one retained completed answer per case/arm; live sources, source caches, snapshots and generation variability affect results. Only MCP has retrieval, preflight and required notices. The companion also has a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer did not receive. No clinical-accuracy, speed or general-superiority claim follows.

The separate ten-question Phoenix benchmark uses a fixed MPRINT snapshot, independently explored read-only questions, an XML/CSV registry and exact string comparison. Only the two MPRINT evidence tools are exposed after preflight. Three research questions were conservatively blocked (two language gates and one urgent gate); other failures include arithmetic, record linkage and UNKNOWN answers. This is a newly authored known benchmark, not a held-out or clinical validation set. Its 3/10 result must not be merged with or substituted for the seven-case paired score. Three questions are moderate difficulty, and some share cohorts.

## Attempts and retention

One E01 chat attempt failed with HTTP 429 before a final answer. Its complete failure trace was retained and only the incomplete case was retried; the 28 retained completed answers were not selected by score. Both paired arms completed all seven cases. One plain R04 grader assessment exhausted quote-validation retries and received no score; its failure was archived, then that unscored assessment was retried with the unchanged rubric. Other valid grades were reused. Legacy version labels in frozen harness metadata are disclosed in metadata-corrections.json; source hashes and policy payloads establish the .12 runtime.

Phoenix setup first used the wrong client dataset argument shape; that attempt produced no answers. A subsequent launcher interruption left the first completed answer saved. The resumed generation retained it, causing a bookkeeping error for that task while the other nine cases ran. The final Phoenix experiment replays all ten unchanged saved outcomes, including UNKNOWN and fixed stops, for exact scoring and readback. No benchmark answer was regenerated to improve a score. The generation summary, original method, failed Phoenix task and final scoring receipt are all retained.

## Source identity

153 source/client/harness/data files are SHA256-frozen in run-design.json. Databricks test archive: `b4bf39ad67d4000f4bac14bc26c67136dc044cc54f803fd3d66b729c5815ee71`. The source-freeze check and notebook counts agree. All 42 MLflow rows have applicable persisted scores with no scorer execution errors. Phoenix replay has ten task rows and no task errors.

## Post-evaluation metadata correction

After all evaluations and readbacks, four canonical harness files received descriptive version-label corrections only. No grader prompt, case, scoring logic, capture or grade changed. The evaluated copies remain frozen in this evidence directory; `harness-metadata-amendment.json` records before/after hashes. `metadata-corrections.json` explains legacy labels in the raw metadata and registered scorer rationales.
