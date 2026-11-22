# Credential recovery and fresh evaluation addendum

Evaluations completed locally on November 20, 2026 (America/New_York; some stored UTC timestamps are November 21). **No deployment, GitHub push, or remote configuration change was made.**

## What was fixed

The Databricks login works (identity request HTTP 200). The original model route, `models.ai.gpt-5-6-luna`, returns HTTP 401 with `expired_secret_key` from its external provider, `models.ai.openai`. This account receives HTTP 403 when accessing that provider's settings. Refreshing the local login would not renew that shared provider key.

The local evaluation client now selects the existing managed route **`system.ai.gpt-5-6-luna`**, which returned HTTP 200 and completed the runs below. No new model was provisioned. The original shared credential was **not renewed**. Its authorized owner would need to replace it only to restore the old connection; this does not block the working managed route or these results. Matching model names do not establish identical underlying model revisions.

The localhost MCP server also needed explicit loopback host/origin allowlists: DNS-rebinding protection was enabled but rejected legitimate local requests. That is fixed, protection remains enabled, and a regression test verifies both accepted loopback requests and rejected hostile hosts/origins. **301 local tests passed**, with zero failures, errors, or skips in the pinned environment.

## Fresh chat evaluation

The current local server and production chat harness ran the existing 16-case set: 12 research questions and four fixed policy refusals.

| Measure | Result | Meaning |
|---|---:|---|
| Completed responses | 16/16 | All cases finished |
| Tool selection | 16/16 | Required/allowed tool names matched the saved case rules |
| Boundary behavior | 16/16 | Expected research/refusal routing; refusal cases made no downstream calls |
| Citation provenance | 16/16 | Answer URLs came from tool evidence, or no citation was needed for a fixed refusal |
| Evidence fidelity | 15/16 | Diagnostic model judgments plus fixed refusal contracts |
| Task fulfillment | 15/16 | Diagnostic model judgments plus fixed refusal contracts |

Citation provenance verifies URL origin, **not whether every associated claim is supported**. These are results on previously seen cases, not clinical accuracy estimates. The same-family judge matched four of four saved controls for each rubric; this does not establish validity on all real answers.

- R05 failed fidelity because the answer attributed MCP-generated registry coverage caveats to FDA itself. This is a real source-attribution concern.
- R01 failed the automated task score because the judge demanded quantitative milk measurements beyond the user's request. The raw failure is retained and flagged for review, not silently changed into a pass.
- R08 was initially judged against the UTC date. The evaluator was corrected to use the run's Eastern date, consistent with the returned deadline `as_of`. The original judgment is retained in `R08-initial-judge-utc-date.json`; only the date-affected case was reassessed.

## Plain-model comparison

Five questions were run once in each arm with the same managed model route, shared instructions and identical user questions. The MCP arm had the 27 local retrieval tools; the plain arm had no retrieval tools. This minimal matched harness is separate from the production chat harness above. The same reference pool was supplied to the judge for both arms, with arm labels hidden.

| Measure | With MCP | Plain model |
|---|---:|---:|
| Completed responses | 5/5 | 5/5 |
| Retrieval tool use observed | 5/5 | 0/5 (by design) |
| Automated task-fulfillment score | 5/5 | 0/5 |
| Median elapsed time, descriptive only | 17.17 s | 6.11 s |
| Validated factual-accuracy comparison | Not established | Not established |

**The automated task scores are diagnostic, not validated comparative success rates.** The plain model honestly declined live recall, recruitment, and safety-notice lookups. That is a useful limitation statement rather than a false fact. The MCP responses supplied retrieved records, but retrieval did not eliminate unsupported source attribution.

The first rubric incorrectly treated the plain model's inability to retrieve as contradicted by evidence available only to the evaluator. All ten unchanged answers were rescored under the same corrected rubric; both judgment versions are retained. Despite four of four synthetic calibration controls passing, real-case grading errors remain:

- R09 plain: “No FDA notice content was retrieved” accurately describes that arm, but the judge still labeled it a contradiction.
- R04 MCP: the judge flagged an unverified citation, while its claim-only normalization produced a pass. The answer also attributes MCP limitations to FDA records.
- R03 plain: comparison with one product's label cannot establish that claims about unspecified other labels are medically false; the directory link leaves them unverified.
- R01 plain: the judge demanded a statement about non-truncation even though this arm had no retrieved record.

For those reasons, **no aggregate factual-accuracy advantage is claimed**. Raw labels remain in `paired-summary.json` for audit, with the quality gate explicitly marked not passed. The useful result is a completed paired execution with visible differences in lookup capability and answer support. Independent review and a larger repeated sample are still needed before any accuracy or speed claim. No clinician review or new MLflow run is represented as complete.

## Reproducibility and evidence

- `diagnosis.json`: sanitized authentication/provider diagnosis; no credential values.
- `unit-tests.xml`: 301-test result for the local server revision.
- `source-manifest.json`: source and case hashes from the run.
- `chats/`: all 16 full chat traces and final answers.
- `chat-checks.json`, `chat-summary.json`, `chat-judgments/`: deterministic checks and saved diagnostic judgments.
- `paired-final/`: all ten final responses, shared references, frozen prompts, both judgment versions and calibration controls.
- `paired/`: initial transport-attempt records. An unreliable console JSON capture was replaced by a temporary UTF-8 response file; all ten answers were then generated afresh into `paired-final/`, not just selected failed cases.
- `judge-review.json`: explicit assistant audit of scoring limitations, not clinician review.

To rerun, start the pinned local server on `127.0.0.1:18080` with `USE_LAKEHOUSE=false`, then run `run-chats.ps1` in PowerShell 7 and `paired_evaluation.py --phase generate` in the pinned Python environment. `score_chats.py` reuses saved judgments by default; `--rescore R01` explicitly reassesses a chosen case. `rescore_pair.py` reproduces the V2 comparison scoring, including its disclosed limitations. `build_report.py` and `../generate-results.py` only assemble saved evidence and do not call a model. Preserve the existing evidence folder before new runs because the runners use fixed output names.

The CLI profile is `gsa-mcp-hackathon`. `model-call.ps1` accepts `DATABRICKS_CLI_PATH` for a different CLI installation. Credentials are acquired in memory and are absent from saved traces. The gateway bridge uses the Windows HTTPS trust store; TLS verification was not disabled. The temporary MCP server listens on loopback only and is stopped after evaluation.

## Submission artifact scope

The updated PowerPoint has 44 slides (15 main and 29 hidden appendix), and the official-template evaluation DOCX has 7 pages. Both now include the 301-test count, 16-case chat rerun, five paired comparisons and grading limitations reported here and in `../results.json`. Older checks are explicitly historical. The archive video and demo screenshots still replay earlier saved responses and retain their historical labels. Historical deployed checks (36 contracts and 21 source/safety checks) remain separate and do not validate this local revision.

## Restoring the old provider connection

No old-key renewal is required to use the working managed route or these results. If the old connection is needed again, an authorized provider owner/administrator can renew the credential for `models.ai.openai` in the hackathon workspace. The original model-route owner is recorded in `diagnosis.json`; the provider owner itself was not visible to this account. No message was sent to anyone. Suggested request:

> Please renew the external-provider credential for `models.ai.openai` in the hackathon Databricks workspace. `models.ai.gpt-5-6-luna` returns HTTP 401 `expired_secret_key` while workspace authentication succeeds. We completed local evaluations using the existing managed route `system.ai.gpt-5-6-luna`. No app deployment or provider configuration change has been made.
