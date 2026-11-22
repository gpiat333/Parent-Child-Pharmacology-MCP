> Current status (November 21, 2026): the existing Databricks sandbox was updated; no GitHub push. See [current validation](DATABRICKS_VALIDATION.md). Prior counts and “no deployment” statements below describe earlier runs.

> Historical record. Current local code has 508 tests, 30 tools, four prompts and four resources; see [current implementation](CURRENT_IMPLEMENTATION.md). Historical names and counts remain below.

> Historical notes retained for traceability. The current local revision is documented in CURRENT_IMPLEMENTATION.md, the evaluation DOCX and ../evaluation/results.json. No deployment was performed.

# Parent-child Pharmacology MCP: methodology and evaluation

Updated November 19, 2026. Hackathon research prototype; not a clinically certified decision-support service.

## Scope and architecture

The deployed Databricks App exposes 27 FastMCP tools over streamable HTTP at `/mcp`. Databricks OAuth and app permissions control access. The deployed configuration is live-only; Delta/Vector Search paths and persistent lakehouse audit storage are inactive. No new compute was provisioned for this evaluation.

Public evidence is retrieved through source-specific adapters, not a single combined clinical database. RxNorm resolves names; LactMed public pages supply breastfeeding evidence; PubMed supplies publications; DailyMed supplies label text; ClinicalTrials.gov supplies registry metadata; MedlinePlus supplies patient information; RePORTER supplies grants; FDA supplies labeling, FAERS, recalls, safety communications and pregnancy-registry discovery. BPCA supplies summary discovery and links. DASH supplies public study metadata, not restricted underlying data. MPRINT uses versioned published Gold/Silver subsets and inferred literature/grant discovery, not a claimed official MPRINT API. Federal Register supports public-input discovery.

The client calls `route_parent_question` before requesting a model answer. Recognized urgent, privacy, unidentified-drug and personal-treatment requests return fixed guidance without evidence retrieval/model generation. Normal research proceeds through typed tools, structured evidence, a source-review model pass, exact link rendering and narrow output checks. This enforcement exists in the companion client; metadata alone cannot enforce another client's behavior.

## Code map and design decisions

| Component | Implementation and purpose |
|---|---|
| Tool registration | `server.py`: stable existing public signatures, eight additional parent-facing tools, prompts and source resource. |
| Shared response contract | `mc/audit.py`: disclaimer, safety fields and bounded error metadata; identifier screening before external retrieval. |
| Parent routing | `mc/parent_safety.py`: conservative English patterns, explicit allow/refer decision and fixed source-backed emergency/poison guidance. Not clinical triage. |
| Parent resources | `mc/parent_resources.py`: bounded queries/results; recalls, registries, recruiting studies, public notices and reporting links. |
| Source retrieval | `mc/sources.py`, `mc/nichd.py`, `mc/pediatric_labels.py`, `mc/mprint_data.py`: source-specific parsing and published snapshots. |
| HTTP reliability | `mc/http.py`: cache, retry, timeout and per-host throttling. These do not establish completeness or currentness. |
| Companion enforcement | `test-mcp-chat.ps1`, `parent-chat-policy.ps1`, `citation-output.ps1`: preflight, fail-closed policy, source review and citation provenance. |

Recall results are candidates: a literal lot match is not verification of the bottle, and a missing lot is not clearance. Trial recruitment and contact details are as listed, not live enrollment confirmation. Unknown public-comment deadlines remain unknown. A pregnancy-registry listing does not establish eligibility. No reporting/comment/enrollment submission is performed.

## November 19 expanded evaluation

Test materials are in the companion project `evaluation/parent-expanded/`. All questions are synthetic; no patient records were used.

| Layer | Initial result | Follow-up / interpretation |
|---|---|---|
| Existing Python regression suite | 170/170 | After adding three regression cases: 173/173. |
| New routing challenge set | 46/48 | Two wording fixes; unchanged challenge set 48/48 locally. |
| Deployed acceptance checks | 18/18 | Repeated after deployment: 18/18. Tool inventory, policy envelope, identity, privacy, sources and participation fields. |
| Companion checks | 12 policy + 7 citation checks passed | Four new trace-capture checks also passed. |
| Eight new chat cases | 7/8 harness checks passed | Privacy case had no saved trace by design; fresh follow-up verified refusal and absence of trace. Initial failure retained. |

The routing set covers urgent symptoms, possible exposure, personal medication requests, vague identity, identifiers, ordinary research and non-US number handling. Expected routes were declared before execution. This is an engineering challenge set, not an independent clinical reference set or population-level safety estimate.

Chat questions cover urgent/identity/dose/privacy boundaries, acetaminophen recalls, lamotrigine registries, FDA reporting and recruiting pediatric diabetes studies. Acceptance checks measure completion and expected blocking; they do not measure medical correctness. Three captured blocked chats show zero model calls and zero evidence calls (mandatory MCP preflight is separate). Privacy capture is intentionally omitted. Four research answers were manually reviewed against retrieved evidence. They include official links and applicability limits; a recall answer still used loose attribution for lookup-generated caveats, so fully source-faithful phrasing remains an improvement area.

### Failures and corrections

1. `I took the wrong medicine` initially bypassed the poison-help pattern. Optional article handling was expanded.
2. `my blood pressure medicine` initially bypassed vague-identity screening. That description now requires confirmation.
3. The chat harness incorrectly expected a transcript for a privacy-blocked question. The initial failure is preserved rather than replaced with a pass.
4. A privacy follow-up was attempted during app restart and received HTTP 502. This exposed a client failure path: opt-in trace saving could run before a screening decision existed. `Test-TraceCaptureAllowed` now rejects absent, empty and privacy decisions. A fresh-prefix privacy follow-up confirmed no transcript. Only synthetic identifiers were involved in the test; the original failed artifact remains as evaluation evidence.

Server deployment after wording fixes: `01f1e45bcdda1930a6a30df11b35e321`. Client trace fix is local companion code, not server code. Public tool names/signatures were unchanged in this pass.

Separate post-deployment wording probe: both repaired questions returned the expected blocking route; the 27-tool inventory check also passed (3/3 assertions, including one repeated inventory assertion). Evidence: `wording-deployed-results.json`.

## Historical MLflow methodology and results

### New paired selection/explanation pilot (later November 19)

The companion `evaluation/selection-explanation/` now contains a completed new
MLflow comparison: 10 newly worded development questions, each run once with the
full 27-tool inventory and a 12-tool parent subset. Mandatory preflight, model and
production prompts were held constant; order alternated by case. The client adds
an optional `ToolProfile` parameter; its default remains `full`. No deployed
server behavior or public MCP signature changed during this experiment.

Two guideline judges assessed evidence fidelity and task fulfillment; three
deterministic checks assessed task-relevant tool selection, expected response/
blocking behavior and citation provenance. There were 100 completed assessments.
Raw results (full / parent): selection 9/10 / 9/10; expected behavior 9/10 / 8/10;
citation provenance 9/10 / 8/10; evidence fidelity 7/10 / 6/10; task fulfillment
5/10 / 4/10. Completed responses, including refusals: 10/10 / 9/10. No calls
outside the predefined task-relevant sets occurred. Scores are retained unchanged.

Confirmed failures: both inventories falsely refused an evidence question because
it said “Do not give a dose”; the smaller inventory selected the registry tool but
failed final URL validation. Some public-input results needed clearer relevance
labels. Several judge rationales falsely claimed that links, truncation notices,
site status or eligibility caveats were missing; refusal scoring also contradicted
the rubric. These disputes are documented in `review-notes.json`, not silently
converted into passes. This is not a clinically validated correctness benchmark.

Completed runs: full `9252221980374ebf9627988f3709fbef`; parent
`4e041d0d12b4431482fc32fca2ad6bdc`, in experiment `1096079759942705`.
Initial attempts were interrupted after SDK metadata-discovery timeouts; their IDs
are retained. Completed attempts reused the same captured answers and rubric,
skipping optional host metadata inference only inside the evaluation process while
retaining explicit host/token authentication. No answers were regenerated to
improve scores. One trial per condition cannot establish inventory superiority;
token totals are not a controlled price comparison. The immediate priorities are
negation-aware routing, robust citation delivery, relevance disclosure and judge
calibration against independent review, rather than adding sources.

### Earlier 32-question benchmark

Before the earlier benchmark details below, note the separate follow-up to the
paired pilot: `evaluation/selection-fixes/report.html` documents deployment
`01f1e460818a1da1b370b6a4e47f76ca`, 186 unit tests, 18 deployed checks and ten
completed chat follow-ups. Required tool selection, expected boundary behavior
and URL provenance each passed 10/10. Explicit negated dose exclusions were fixed
without suppressing separate risky requests. A single bounded citation repair
still uses the original source allowlist. Relevance fields identify literal
keyword support and missing words, not clinical suitability.

The revised evaluator uses deterministic approved-refusal contracts for the two
boundary cases and model judges for eight research answers. Raw results were
10/10 evidence fidelity v2 and 9/10 task fulfillment v2 (run
`c26935e4279f42baa32cbde33da7d327`). Four synthetic calibration fixtures produced
4/4 correct evidence judgments but only 3/4 correct task judgments. The latter is
marked diagnostic-only and cannot serve as an acceptance gate. Five tests verify
that failed/missing calibration cannot pass the gate. The remaining E06 task flag
is retained even though its rationale conflicts with the explicit relevance
disclosure. Scores are not directly comparable to the earlier evaluator and are
not clinical certification. Three extra tool calls outside the original allowed
sets were observed; efficiency remains a limitation. Original results were not
overwritten. A separate live corrupted-citation repair test and parent-inventory
registry follow-up both passed.

The latest completed full batch is `evaluation/broad-source-citations/`: 32 reused development questions, eight each for PubMed, trials, cross-source and safety. Expected facts/reference evidence were frozen before chat generation. `mlflow.genai.evaluate` scored captured answers and tool evidence; it was not an exported-agent prediction workflow. Five model judges assessed correctness, source fidelity, clinical boundaries, safety and relevance. Two deterministic checks assessed response contract and citation URL provenance. Underlying judge model version was not pinned.

Raw passes: correctness 29/32; source fidelity 27/32; clinical boundaries 32/32; safety 32/32; relevance 30/32; response contract 32/32; citation grounding 32/32. All 224 assessments are retained. Disputed judge flags remain counted. Later targeted scorer timeouts are not reported as passes. This November 19 extension did not run a new MLflow benchmark.

MLflow experiment: https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705

URL provenance means a link came from tool evidence; it does not prove every clinical sentence is supported. Judge agreement is diagnostic feedback, not clinical certification. Scores from different test layers should not be summed into a medical-accuracy percentage.

## Security and remaining limitations

- No dosing, tapering, missed-dose schedules or personal start/stop decisions are in scope.
- Routing/identifier patterns are incomplete, English-focused and not validated for clinical sensitivity or specificity. Negation, historical symptoms, multilingual input and adversarial wording need further work.
- Source outages, stale trial status, bounded candidate searches and incomplete snapshots can omit relevant evidence. Missing evidence never establishes safety.
- Ordinary chat transcript capture is off. Synthetic opt-in capture is gated; this does not establish provider retention behavior or eliminate shell history/caches.
- Prompt instructions are not proof of prompt-injection resistance. DNS-rebinding protection remains disabled for Databricks Apps compatibility.
- Independent clinician review, externally held-out questions, cross-client enforcement testing and a new parent-focused MLflow batch remain outstanding. No HIPAA authorization, penetration-test result, clinical certification or production-readiness claim is made.

## Reproduction

Latest additional test batch: companion `evaluation/parent-generalization/`.
Sixteen new-wording cases (12 research, four fixed boundaries) completed using the
unchanged deployed server/client. Run `4075650d4a3c4e1ebd4e253719fc009f` has 80
assessments; calibration run `722b7dda3da740f8938f3e3fb9e420e6` has 20. Selection,
expected boundary behavior and citation provenance each passed 16/16. Raw v2
evidence fidelity was 14/16 (10/12 research plus four fixed contracts); task
fulfillment was 10/16 (6/12 research plus four fixed contracts). No scorer errors.
Task calibration again matched only 3/4 controls; its scores remain diagnostic-only.
Evidence calibration matched 4/4, but manual review still identified a false
omission flag, so calibration is not proof of judge reliability. No raw flags were
replaced. Real remaining weaknesses: pediatric searches can foreground broader
studies with unverified age eligibility; a public-input answer confused a known
future deadline with unverified status and inferred closure from past meeting dates.
These newly observed weaknesses were documented, not fixed during the test batch.
See the report and review-notes.json for disputed judge rationales and exact evidence.

From the server root: `.venv\Scripts\python.exe -m pytest tests -q`.
From the companion root, using the server Python: run `evaluation/parent-expanded/boundaries.py` and `evaluation/parent-expanded/test_deployed.py`.
Run PowerShell `evaluation/test-parent-chat-policy.ps1`, `evaluation/test-citation-output.ps1`, and `evaluation/parent-expanded/test_trace_capture.ps1`.
`evaluation/parent-expanded/run_chat_initial.ps1` preserves the initial harness behavior for reproducibility; its privacy row expects a file and fails because privacy traces are suppressed. The corrected `run_chat.ps1` uses fresh capture prefixes and checks the privacy response plus absence of a trace. The corrected full batch has not been rerun; the separate privacy follow-up is the evidence for that row. Do not overwrite archived results when repeating a run. Databricks authentication is obtained through the CLI; credentials are never included in the report.



## 2026-11-19 pediatric population and public-input deadline correction
Pediatric discovery now requires explicit numeric registry age support below 18, retaining conflict checks and excluding adult-only and unverified records. CHILD category alone is insufficient for the main list. This conservative screen may omit eligible studies and does not establish individual eligibility. Applied to both trial tools, without signature changes. Returned age fields, exclusion counts, study type, relevance and bounded-search limitations remain available.
Public-input results separate the listed comment date and past/today/future/unknown relation from unverified submission acceptance. Meeting dates never establish comment closure; same-day dates do not establish a cutoff time.
Client instructions require population filtering and separate date/relevance/submission status. 215 local tests passed; 21 deployed checks passed. Final deployment: 01f1e4656e0c107e949cdadb1f6d24a8. Original generalization results and the first follow-up (which still admitted CHILD-only broad records) remain retained. See companion evaluation/population-deadline-final for captured answers, MLflow results and limitations. These are engineering evaluations, not clinical certification.

Final targeted MLflow run `20bb013dde97463d9fc63d3def41678a`: all five metrics 5/5 (25 assessments across three research and two exact-contract boundary cases). Evidence calibration 4/4; task calibration 3/4, task score diagnostic-only. Five-case follow-up is not a held-out benchmark or clinical validation. Manual review found minor heading ambiguity: “Closed deadlines” would be clearer as “Past listed deadlines”; the subsequent client wording follow-up is archived separately.

## 2026-11-20 MCP contract hardening

`mc/contracts.py` declares bounded, nonempty inputs, identifier patterns, list sizes,
and the typed `EvidenceResponse`/`SafetyMetadata` envelope. The 27 FastMCP-generated
argument models now forbid unexpected fields and require strict primitive types.
The shared registration helper rebuilds both the model and the advertised schema.
The FastMCP 1.x internal argument-model hook is isolated and covered by tests.

Tool names, parameter names and defaults remain unchanged; accepted inputs are
intentionally narrower. Numeric strings, blank required inputs, excessive limits,
invalid identifiers and unknown arguments now return MCP validation errors before
retrieval. Intentional empty discovery searches remain supported. Internal adapter
checks remain as defense in depth. No clinical meaning is inferred from valid syntax.

All tools advertise an output schema requiring a typed safety envelope and nonempty
disclaimer. Source-specific fields are allowed and preserved, but are not individually
modeled. This is a common response contract, not complete validation of every source
record or an assurance of clinical accuracy. Client enforcement remains necessary.

Descriptions distinguish focused parent information from broad research briefs and
enrollment discovery from the research landscape across trial statuses. The composite
description explicitly limits combination-product coverage to the first ingredient
and pediatric FAERS coverage to infants.

Validation: **250 unit tests passed**, including 35 new protocol-contract tests;
**36/36 deployed contract checks** (27 schemas, 8 invalid calls, 1 structured response);
**21/21 deployed source/safety checks**. Test results and pre/post audit JSON are in
the companion `evaluation/tool-design-audit/` directory. Historical MLflow results
were not overwritten; these checks do not constitute a new MLflow benchmark.

Two new chat-selection probes (focused parent evidence and recruiting-study
participation) could not complete: the Databricks model route returned HTTP 401
`expired_secret_key` before model output. Therefore actual chat-selection behavior
with the clarified descriptions remains unverified. Endpoint authentication and
all MCP contract/source checks succeeded; provider credential renewal is separate.
