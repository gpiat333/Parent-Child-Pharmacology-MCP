"""Assemble the recovery addendum from retained results; no network/model calls."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IDS = ['R01', 'R03', 'R04', 'R06', 'R09']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

arms = {}
rows = []
for arm in ['mcp', 'plain']:
    answers = [read(HERE/'paired-final'/f'{cid}-{arm}.json') for cid in IDS]
    judgments = [read(HERE/'paired-final'/f'{cid}-{arm}-judge-v2.json')['judgment'] for cid in IDS]
    arms[arm] = {
        'completed': sum(a['completed'] for a in answers), 'total': len(answers),
        'tool_retrieval_observed': sum(bool(a['calls']) for a in answers),
        'automated_task_fulfillment': sum(j['task_fulfilled'] for j in judgments),
        'raw_source_fidelity_labels_not_validated': dict(Counter(j['fidelity_status'] for j in judgments)),
        'median_elapsed_seconds': round(statistics.median(a['elapsed_ms'] for a in answers)/1000, 2),
    }
    for cid, answer, judgment in zip(IDS, answers, judgments):
        rows.append({'id': cid, 'arm': arm, 'completed': answer['completed'],
                     'task_fulfilled_model_judged': judgment['task_fulfilled'],
                     'raw_fidelity_label': judgment['fidelity_status'],
                     'tool_names': [c['tool'] for c in answer['calls']],
                     'source': f'paired-final/{cid}-{arm}.json',
                     'judge_source': f'paired-final/{cid}-{arm}-judge-v2.json'})

review = [
    {'id': 'R09', 'arm': 'plain', 'issue': 'False contradiction despite the corrected rubric',
     'finding': 'The answer says no FDA notice content was retrieved in its session. Its saved trace has zero calls. The evaluator-only reference does not contradict this statement. This is honest abstention with no assessable source claims, not evidence of a false FDA fact.',
     'effect': 'Do not use the raw fail label or contradicted-claim count as accuracy evidence. The requested lookup was not completed.'},
    {'id': 'R04', 'arm': 'mcp', 'issue': 'Claim-only normalization ignores an unverified citation',
     'finding': 'The raw judge says fail because the FDA guidance-page content was not retrieved, but the normalization produces pass from its zero unverified-claim count. The answer also attributes MCP recall limitations to FDA records.',
     'effect': 'This is a source-attribution/citation concern. Do not treat the normalized pass as verified citation accuracy.'},
    {'id': 'R03', 'arm': 'plain', 'issue': 'Specific product evidence versus unspecified generic labeling',
     'finding': 'The answer links a metformin search directory and does not identify a product. The judge compares it with one retrieved product label. Differences are not sufficient to prove that every other label is false. The directory also cannot verify the specific claims. The answer omits the requested adult warning discussion.',
     'effect': 'Label claims are unverified against this pool; the raw contradicted-claim count is not a definitive medical error count. Task fulfillment remains a diagnostic judgment.'},
    {'id': 'R01', 'arm': 'plain', 'issue': 'Overly strict completeness rationale',
     'finding': 'The judge demands an explicit statement that evidence was not truncated, although no source was retrieved in this arm. It also identifies an unsupported source-attributed monitoring recommendation, which is a distinct support concern.',
     'effect': 'The 0/5 plain-model task score is a raw automated result, not an independently validated task-success rate.'},
]
calibration = read(HERE/'paired-final/calibration-v2.json')
summary = {
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'model': 'system.ai.gpt-5-6-luna', 'case_ids': IDS, 'arms': arms, 'cases': rows,
    'method': 'Same model route, shared prompt and user questions; one response per arm per question. Only the MCP arm receives local retrieval tools. Both graders receive the same reference pool per question. Production chat review/safety passes are not part of this minimal paired harness.',
    'calibration_v2': {'matched_controls': sum(c['expected']==c['judgment']['fidelity_status'] for c in calibration), 'total_controls': len(calibration)},
    'grading_quality_gate': 'NOT PASSED for a validated source-fidelity comparison: real-case rubric violations remain despite 4/4 synthetic controls. Raw judgments retained; no further resampling.',
    'source_accuracy_comparison': None,
    'review_findings': review,
    'limits': ['Five selected, previously seen questions; one trial per arm.',
               'Same-family model judge, not independent clinical review.',
               'Reference pool comes from this MCP implementation and may be incomplete.',
               'Honest abstention does not complete a lookup and is not itself a false claim.',
               'Parallel local timing samples are descriptive only; no speed or general superiority claim.',
               'Managed route name matches the older model suffix; equivalence of underlying model revisions was not established.',
               'No new MLflow run, deployment, or GitHub push.'],
}
save(HERE/'paired-summary.json', summary)
save(HERE/'judge-review.json', {'review_type': 'Assistant evidence/rubric audit; not human or clinician review', 'findings': review})

diagnosis = read(HERE/'diagnosis.json')
save(ROOT/'evaluation/provider-access-check.json', {
    'checked_at_utc': diagnosis['recorded_at_utc'],
    'status': 'Evaluations unblocked through existing managed model route; original provider credential remains expired',
    'original_model': diagnosis['original_route']['model'], 'original_http_status': 401,
    'original_error_code': 'expired_secret_key', 'working_model': diagnosis['working_route']['model'],
    'working_http_status': 200, 'credential_renewed': False, 'remote_configuration_changed': False,
    'diagnosis_source': 'credential-recovery/diagnosis.json',
    'historical_check_source': 'credential-recovery/original-provider-access-check.json',
})
chat = read(HERE/'chat-summary.json')
suite = ET.parse(HERE/'unit-tests.xml').getroot().find('testsuite')
assert int(suite.get('tests')) == 301 and int(suite.get('failures')) == 0 and int(suite.get('errors')) == 0
assert all(a['completed'] == 5 for a in arms.values())
assert chat['counts']['completed'] == {'passed': 16, 'total': 16}

report = f'''# Credential recovery and fresh evaluation addendum

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
| Automated task-fulfillment score | {arms['mcp']['automated_task_fulfillment']}/5 | {arms['plain']['automated_task_fulfillment']}/5 |
| Median elapsed time, descriptive only | {arms['mcp']['median_elapsed_seconds']} s | {arms['plain']['median_elapsed_seconds']} s |
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
'''
(HERE/'REPORT.md').write_text(report, encoding='utf-8')

# A self-contained readable answer browser, with evidence links and no external assets.
sections = []
for cid in IDS:
    cards = []
    for arm in ['mcp', 'plain']:
        a = read(HERE/'paired-final'/f'{cid}-{arm}.json')
        cards.append(f'<article><h3>{"With MCP" if arm=="mcp" else "Plain model"}</h3><p>{a["elapsed_ms"]/1000:.2f} seconds; {len(a["calls"])} tool calls</p><pre>{html.escape(a["answer"])}</pre><a href="paired-final/{cid}-{arm}.json">Full saved trace</a></article>')
    sections.append(f'<details><summary>{cid}: {html.escape(a["question"])}</summary><div class="pair">'+''.join(cards)+'</div></details>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fresh evaluation addendum</title><style>body{font:17px/1.6 system-ui,sans-serif;margin:40px auto;max-width:1250px;padding:0 24px;color:#182a42}a{color:#155b97}.note{background:#fff2d8;padding:20px;border-left:5px solid #ca780a}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.6 system-ui,sans-serif}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{background:#f4f7fa;padding:20px;min-width:0}summary{cursor:pointer;font-weight:650;padding:18px}details{border:1px solid #ccd5df;margin:18px 0}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>Fresh local evaluation results</h1><p>November 20, 2026 · Parent-child Pharmacology MCP · No deployment or GitHub push</p><div class="note"><strong>Evaluations unblocked; original shared key not renewed.</strong><br>The existing managed model route completed 16 chat cases and 10 comparison responses. 301 local tests passed. Automated grading still has known errors; these results do not establish clinical accuracy or general superiority.</div><p><a href="REPORT.md">Full report and limitations</a> · <a href="chat-summary.json">16-case chat scores</a> · <a href="paired-summary.json">Paired comparison summary</a> · <a href="diagnosis.json">Credential diagnosis</a></p><h2>Compare the five paired answers</h2><p>These are unchanged saved responses. Source URLs are shown as response text, not independently validated medical guidance. Open each question to compare both arms.</p>'''+''.join(sections)+'</html>'
(HERE/'index.html').write_text(page, encoding='utf-8')
print(json.dumps({'chat': chat['counts'], 'paired': arms, 'source_accuracy_comparison': None, 'report': str(HERE/'REPORT.md')}))
