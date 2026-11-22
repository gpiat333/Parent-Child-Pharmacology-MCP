from pathlib import Path
from datetime import datetime,timezone
import json,statistics,hashlib,sys,html,xml.etree.ElementTree as ET
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/databricks-validation-2026-11-21';W=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sys.path.insert(0,str(P/'server'))
from core.output_notices import required_notices
cases=read(R/'cases.json');C=read(R/'chat-summary.json');checks=read(R/'chat-checks.json');freeze=read(R/'local-source-freeze.json')
assert C['diagnostic_grading']['judged']==21
unitroot=ET.parse(R/'local-unit-tests.xml').getroot().find('testsuite');unit={k:int(unitroot.get(k)) for k in ['tests','failures','errors','skipped']}
assert unit==dict(tests=508,failures=0,errors=0,skipped=0)
notices=[];workflow=[]
for case in cases:
    d=read(R/'chats'/(case['id']+'-results.json'));assert d['completed']
    expected=required_notices([x['tool'] for x in d['tool_calls']],d.get('policy_blocked',False))
    notices.append({'case':case['id'],'expected_ids':[x['id'] for x in expected],'recorded_ids':d.get('required_notice_ids',[]),'all_required_text_present':all(x['text'] in d['answer'] for x in expected)})
    if d.get('requested_workflow'):workflow.append({'case':case['id'],'required_tool':d['requested_workflow']['required_tool'],'first_tool':d['tool_calls'][0]['tool']})
assert all(n['expected_ids']==n['recorded_ids'] and n['all_required_text_present'] for n in notices)
save(R/'notice-contract-checks.json',notices)
ids=['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk'];paired={};rows=[]
for arm in ['mcp','plain']:
    answers=[read(R/'paired-final'/(i+'-'+arm+'.json')) for i in ids];grades=[read(R/'paired-final'/(i+'-'+arm+'-judge.json'))['judgment'] for i in ids]
    assert all(a['completed'] for a in answers)
    paired[arm]={'completed':7,'total':7,'task_fulfilled':sum(g['task_fulfilled'] for g in grades),'fidelity_pass':sum(g['fidelity_status']=='pass' for g in grades),'fidelity_fail':sum(g['fidelity_status']=='fail' for g in grades),'fidelity_not_assessable':sum(g['fidelity_status']=='not_assessable' for g in grades),'median_seconds':round(statistics.median(a['elapsed_ms'] for a in answers)/1000,2)}
    for i,a,g in zip(ids,answers,grades):rows.append({'case':i,'arm':arm,'completed':a['completed'],'fidelity':g['fidelity_status'],'task_fulfilled':g['task_fulfilled'],'elapsed_ms':a['elapsed_ms']})
verified=[read(R/'mlflow'/(p+'-verification.json')) for p in ['research','stops','paired']]
assert sum(v['rows_verified'] for v in verified)==42 and all(v['all_applicable_scores_present'] and v['assessment_errors']==0 for v in verified)
source=read(R/'deployed-source-verification.json');inv=read(R/'deployment-probes.json')['inventory'];app=read(R/'app-after.json');parent=read(R/'mlflow/parent-run.json')
assert source['runtime_files']==93 and source['local_frozen_files_unchanged']==112 and not source['missing'] and not source['changed'] and not source['extra']
S={'revision':'databricks-mlflow-validation','policy_version':'2026-11-21.4','generated_at_utc':datetime.now(timezone.utc).isoformat(),'local_tests':unit,'source_files':112,'deployed_runtime_files_verified':93,'inventory':inv,'chat':C,'paired':paired,'paired_rows':rows,'protocol_probes':20,'valid_tool_schemas':30,'invalid_input_rejections':8,'workflow_requirements':workflow,'required_notice_records':sum(bool(n['expected_ids']) for n in notices),'required_notices_preserved':True,'deployment_id':source['deployment_id'],'app_url':app['url'],'model':'system.ai.gpt-5-6-luna','deployed':True,'deployment_scope':'Updated existing Databricks sandbox app only; no new compute or infrastructure resources','github_push':False,'clinical_review':'Not performed','evaluation_driver':'Local Python/PowerShell driver; deployed MCP app, model gateway and MLflow tracking in Databricks','mlflow':{'parent':parent,'runs':{p:read(R/'mlflow'/(p+'-run.json')) for p in ['research','stops','paired']},'final_rows_verified':42,'assessment_errors':0,'capture_mode':'Precomputed evaluation of fresh deployed captures, with one root span per row and full tool traces in artifacts; not full per-tool MLflow instrumentation'},'first_attempt_chat_completion':24,'http429_chat_retries':4,'cases_unchanged':True,'grader_prompt_unchanged':True,'additional_routing_observation':read(R/'additional-routing-observation.json'),'interpretation':'Same known cases, one completed sample, same-family diagnostic judge and bounded reference pool. No clinician adjudication. Compares workflows; no clinical-accuracy or speed-superiority claim.'}
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':paired,'rows':rows,'limits':S['interpretation']})
findings=[]
for c in checks:
    for key in ['boundary_behavior','tool_selection','citation_provenance']:
        if c.get(key) is False:findings.append({'case':c['id'],'type':key,'tools':c['tools'],'unmatched_urls':c.get('unmatched_urls',[])})
    g=c.get('judgment')
    if g and (g['fidelity_status']=='fail' or not g['task_fulfilled']):findings.append({'case':c['id'],'type':'diagnostic_model_finding',**g})
for row in rows:
    if row['fidelity']=='fail' or not row['task_fulfilled']:
        g=read(R/'paired-final'/(row['case']+'-'+row['arm']+'-judge.json'))['judgment'];findings.append({'case':row['case'],'arm':row['arm'],'type':'diagnostic_model_finding',**g})
save(R/'grading-review.json',{'raw_scores_changed':False,'clinical_adjudication':False,'findings':findings,'technical_review_file':'TECHNICAL_REVIEW.md','important_distinction':'Unsupported by the bounded reference pool is not necessarily false in the wider literature. URL membership is not claim support.'})
c=C['counts'];g=C['diagnostic_grading'];b=paired
report=f'''# Databricks deployment and MLflow evaluation — November 21, 2026

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

The existing **mcp-mc Databricks sandbox app was updated** at the user's request. Deployment `{S['deployment_id']}` is running policy `{S['policy_version']}`. No GitHub push, official submission, new cluster, warehouse, model endpoint, permission change or provider change occurred. NIHRePORTERAgent source was not modified.

## Where this ran

The MCP server runs in [Databricks Apps]({S['app_url']}). Model calls use the existing Databricks managed gateway. MLflow scores, traces and artifacts are stored in the [evaluation experiment]({parent['url']}). The evaluation driver ran locally; no remote cluster job or Databricks notebook execution is claimed. The 508 unit tests were the prior verified **local** run on this unchanged source, not a fresh Linux unit run.

All 93 deployed runtime files were downloaded from the active immutable snapshot and matched byte for byte. All 112 frozen server/client files remain unchanged. Deployment/configuration and evaluation tooling changed; no application behavior was changed for this rerun.

## Verified results

| Measure | Result | Interpretation |
|---|---:|---|
| Local unit baseline | 508 passed | Zero failures/errors/skips; same source |
| Deployed inventory | 30 tools / 4 prompts / 4 resources | Observed on active app |
| Tool schemas / invalid inputs | 30 valid / 8 rejected | Runtime contract probes |
| Source/workflow captures | 20 | Captures, not 20 clinical passes; partial and empty statuses retained |
| Initial chat completion | 24/28 | Four HTTP 429 failures retained |
| Final chat completion | {c['completed']['passed']}/28 | Retry only incomplete cases, sequentially |
| Expected routes | {c['boundary_behavior']['passed']}/28 | Known-case behavior |
| Required/allowed tool checks | {c['tool_selection']['passed']}/28 | Separate from answer quality |
| Fixed stops | {c['fixed_stops']['passed']}/7 | Zero downstream evidence/model calls |
| URL membership | {c['citation_provenance']['passed']}/21 | Does not establish claim support |
| Diagnostic research fidelity | {g['fidelity_pass']} pass / {g['fidelity_fail']} fail / {g['fidelity_not_assessable']} N/A | Fallible model labels |
| Diagnostic research tasks | {g['task_fulfilled']}/21 | Seven stops excluded |
| Applicable notices | {S['required_notice_records']}/{S['required_notice_records']} | Required text preserved |
| MLflow final rows verified | 42/42 | 21 research + 7 stops + 14 paired; zero assessment errors |

The three pilot answers are reused in the full research set; they are not three additional independent samples. The corrected pilot was read back successfully. Four synthetic grader controls matched {C['calibration']['fidelity_matches']}/4 fidelity and {C['calibration']['task_matches']}/4 task expectations; this does not validate clinical grading.

## Seven paired questions

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task fulfillment | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| Median successful-attempt seconds | {b['mcp']['median_seconds']} | {b['plain']['median_seconds']} |

Both arms use the same model and shared instructions. Only MCP has retrieval, workflow enforcement and fixed notices. The paired runner uses a shorter prompt and no separate source-review stage. A shared bounded pool is judged without arm labels. This compares workflows, not isolated model ability. Abstention can be honest while leaving a lookup incomplete. N/A is not a fidelity failure; the combined MLflow fidelity mean excludes it. Report arm-specific counts above instead of treating the combined mean as an MCP result. Timings are uncontrolled and exclude retries; no speed advantage is established.

## Remaining limitations and recording fixes

The cases are known development cases with one retained completed sample, changing live sources, a same-family model judge, bounded references and no independent clinical adjudication. Raw negative grades were retained. The judge can misread evidence or penalize a valid statement because it lies outside its reference pool. Review `grading-review.json` and `TECHNICAL_REVIEW.md`; these are diagnostic observations, not clinical certification.

An extra smoke question, “Give me a pregnancy evidence brief for lamotrigine,” was allowed but did not select the mandatory brief workflow. “Compile an evidence brief…” matched correctly. This paraphrase limitation is outside the unchanged 28-case benchmark and remains unresolved; it must not be hidden behind the 28-case route score. Safety and language matching remain heuristic. Required notices cannot by themselves prevent false reassurance or harmful framing.

The first MLflow pilot exceeded Databricks' 65,535-byte assessment-value limit because full reference evidence was placed in expectations. Full evidence now lives in artifacts and expectations hold compact references. The earlier telemetry failure is preserved; answers and grades were reused. All final applicable scores, including False values and N/A handling, were read back from Databricks. MLflow uses precomputed captures with one root span per row; full MCP/tool traces are JSON artifacts, not separately instrumented spans.

A one-time OAuth token expired during the paired run's final status update after all results were saved. The harness now uses the existing CLI sign-in through a refreshable SDK credential provider. The status update was recovered without regenerating answers or grades. No administrator credential renewal was needed. Four incomplete chat attempts returned HTTP 429 and were archived before sequential retry; first-attempt reliability remains 24/28.

Early MLflow processes inherited this chat's NIHRePORTERAgent working directory, causing unrelated automatic Git metadata. Run tags were corrected and traces annotated; evaluated source is identified by the submission freeze and deployed snapshot hashes. No GitHub repository has been assigned or uploaded. Later evaluation processes run outside the unrelated checkout.

## Evidence and history

Current raw captures, scorers, model judgments, retry records, source hashes and MLflow readbacks are in this directory. The prior local 508-test evaluation remains under `../notice-citation-revision` with 20/21 fidelity and 17/21 tasks. The 473-test and older runs retain their original evidence. The existing demo images/video are labeled as predeployment local replays of the same source; this deployed evaluation is separate.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8')
links=''.join(f'<li><a href="{p}-verification.json">{p} readback</a></li>' for p in [])
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Databricks MLflow evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Databricks deployment and MLflow evaluation</h1><p><a href="summary.json">Metrics</a> · <a href="grading-review.json">Raw diagnostic findings</a> · <a href="TECHNICAL_REVIEW.md">Technical review</a> · <a href="'+html.escape(parent['url'])+'">MLflow run</a></p><pre>'+html.escape(report)+'</pre>',encoding='utf-8')
print(json.dumps({'chat':c,'diagnostic':g,'paired':paired,'verified_mlflow_rows':42},indent=2))
