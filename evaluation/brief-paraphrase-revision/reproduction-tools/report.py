from pathlib import Path
from datetime import datetime, timezone
import json, statistics, html, sys, xml.etree.ElementTree as ET
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-paraphrase-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sys.path.insert(0,str(P/'server'))
from core.output_notices import required_notices
cases=read(R/'cases.json');C=read(R/'chat-summary.json');checks=read(R/'chat-checks.json')
u=ET.parse(R/'local-unit-tests.xml').getroot().find('testsuite')
unit={k:int(u.get(k)) for k in ['tests','failures','errors','skipped']}
assert unit==dict(tests=531,failures=0,errors=0,skipped=0)
assert C['diagnostic_grading']['judged']==21
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
 answers=[read(R/'paired-final'/(i+'-'+arm+'.json')) for i in ids]
 grades=[read(R/'paired-final'/(i+'-'+arm+'-judge.json'))['judgment'] for i in ids]
 assert all(a['completed'] for a in answers)
 paired[arm]={'completed':7,'total':7,'task_fulfilled':sum(g['task_fulfilled'] for g in grades),'fidelity_pass':sum(g['fidelity_status']=='pass' for g in grades),'fidelity_fail':sum(g['fidelity_status']=='fail' for g in grades),'fidelity_not_assessable':sum(g['fidelity_status']=='not_assessable' for g in grades),'median_seconds':round(statistics.median(a['elapsed_ms'] for a in answers)/1000,2)}
 for i,a,g in zip(ids,answers,grades):rows.append({'case':i,'arm':arm,'completed':a['completed'],'fidelity':g['fidelity_status'],'task_fulfilled':g['task_fulfilled'],'elapsed_ms':a['elapsed_ms']})
verified=[read(R/'mlflow'/(p+'-verification.json')) for p in ['research','stops','paired']]
assert sum(v['rows_verified'] for v in verified)==42 and all(v['all_applicable_scores_present'] and v['assessment_errors']==0 for v in verified)
source=read(R/'deployed-source-verification.json');parent=read(R/'mlflow/parent-run.json');app=read(R/'app-after.json')
assert source['runtime_files']==93 and not source['missing'] and not source['changed'] and not source['extra']
retry=read(R/'retry-chats.json') if (R/'retry-chats.json').exists() else {'initial_completion':28,'retried_cases':[]}
regression=read(R/'routing-regression/verification.json');extra=read(R/'additional-routing-observation.json')
assert regression['completed'] and regression['first_evidence_tool']=='medication_evidence_brief' and extra['passed']==extra['expected']==12
S={'revision':'brief-paraphrase-revision','policy_version':'2026-11-21.5','generated_at_utc':datetime.now(timezone.utc).isoformat(),'local_tests':unit,'source_files':112,'deployed_runtime_files_verified':93,'inventory':read(R/'deployment-probes.json')['inventory'],'chat':C,'paired':paired,'paired_rows':rows,'protocol_probes':20,'valid_tool_schemas':30,'invalid_input_rejections':8,'workflow_requirements':workflow,'required_notice_records':sum(bool(n['expected_ids']) for n in notices),'required_notices_preserved':True,'deployment_id':source['deployment_id'],'app_url':app['url'],'model':'system.ai.gpt-5-6-luna','deployed':True,'deployment_scope':'Updated existing Databricks sandbox app; no new compute or infrastructure','github_push':False,'clinical_review':'Not performed','evaluation_driver':'Local driver and local unit tests; MCP app, model gateway and MLflow tracking in Databricks','mlflow':{'parent':parent,'runs':{p:read(R/'mlflow'/(p+'-run.json')) for p in ['research','stops','paired']},'final_rows_verified':42,'assessment_errors':0,'capture_mode':'Precomputed fresh deployed captures; one root span per row; full tool traces in artifacts'},'first_attempt_chat_completion':retry['initial_completion'],'retried_chat_cases':retry['retried_cases'],'cases_unchanged':True,'grader_prompt_unchanged':True,'routing_regression':regression,'additional_routing_observation':extra,'interpretation':'Known development cases; one completed sample each; changing live sources; same-family diagnostic judge; bounded reference pool; no clinician adjudication. Workflow comparison, not clinical accuracy or isolated model ability.'}
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':paired,'rows':rows,'limits':S['interpretation']})
findings=[]
for c in checks:
 for key in ['boundary_behavior','tool_selection','citation_provenance']:
  if c.get(key) is False:findings.append({'case':c['id'],'type':key,'tools':c['tools'],'unmatched_urls':c.get('unmatched_urls',[])})
 g=c.get('judgment')
 if g and (g['fidelity_status']=='fail' or not g['task_fulfilled']):findings.append({'case':c['id'],'arm':'chat','type':'diagnostic_model_finding',**g})
for row in rows:
 if row['fidelity']=='fail' or not row['task_fulfilled']:
  g=read(R/'paired-final'/(row['case']+'-'+row['arm']+'-judge.json'))['judgment'];findings.append({'case':row['case'],'arm':row['arm'],'type':'diagnostic_model_finding',**g})
save(R/'grading-review.json',{'raw_scores_changed':False,'clinical_adjudication':False,'findings':findings,'technical_review_file':'TECHNICAL_REVIEW.md','important_distinction':'Unsupported in the supplied reference pool does not necessarily mean false. URL membership does not establish claim support.'})
c=C['counts'];g=C['diagnostic_grading'];b=paired
report=f'''# Routing fix and Databricks evaluation

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

The missed request “Give me a pregnancy evidence brief for lamotrigine” is fixed in policy `{S['policy_version']}`. The shared matcher now handles give, show and send, with or without “me”; the same object grammar handles negations. Whole-question safety, identity, privacy and language stops still take priority. This is a bounded English pattern fix, not exhaustive intent recognition.

The existing Databricks sandbox app was updated to deployment `{S['deployment_id']}`. No GitHub push or official submission occurred. No new cluster, warehouse, model endpoint, permission or provider configuration was created. NIHRePORTERAgent source was not modified.

## Where this ran and what changed

Source edits are in the submission folder's `server/core/workflows.py`, `server/core/policy.json`, `server/core/output_notices.json` and `server/tests/test_brief_workflow.py`. There are 23 new regression tests. All **531 tests passed locally**, with zero failures, errors or skips. All **93 runtime files** downloaded from the active Databricks snapshot match the staged source; 112 server/client files were frozen for this run.

The evaluation driver ran locally. The MCP app, model gateway and managed [MLflow experiment]({parent['url']}) ran in Databricks. This is not a remote notebook or cluster unit-test run. Fresh responses were captured for the same 28 questions and seven paired questions, with unchanged criteria, model and grader v2 prompt. Three pilot answers are included in the 28; they are not extra independent samples.

## Verified results

| Measure | Result | Meaning |
|---|---:|---|
| Fresh local unit tests | 531 passed | Includes 23 new routing regressions |
| Deployed inventory | 30 tools / 4 prompts / 4 resources | Active app |
| Schemas / invalid inputs | 30 valid / 8 rejected | Runtime contract checks |
| Source/workflow captures | 20 | Partial/empty results retained; not clinical passes |
| Additional routing probes | 12/12 | Outside the unchanged benchmark |
| Original missed question | Completed; brief called first | Separate end-to-end client regression |
| First-attempt chat completion | {S['first_attempt_chat_completion']}/28 | Retry history retained |
| Final chat completion | {c['completed']['passed']}/28 | Completed answers not regenerated |
| Expected routes | {c['boundary_behavior']['passed']}/28 | Known-case behavior |
| Required/allowed tools | {c['tool_selection']['passed']}/28 | Selection, not answer quality |
| Fixed stops | {c['fixed_stops']['passed']}/7 | Zero downstream evidence/model calls |
| URL membership | {c['citation_provenance']['passed']}/21 | Not claim support |
| Research fidelity | {g['fidelity_pass']} pass / {g['fidelity_fail']} fail / {g['fidelity_not_assessable']} N/A | Fallible diagnostic model labels |
| Research tasks fulfilled | {g['task_fulfilled']}/21 | Seven stops excluded |
| Applicable notices | {S['required_notice_records']}/{S['required_notice_records']} | Required text preserved |
| MLflow final rows verified | 42/42 | 21 research + 7 stops + 14 paired; zero assessment errors |

Four synthetic grader controls matched {C['calibration']['fidelity_matches']}/4 fidelity and {C['calibration']['task_matches']}/4 task expectations. These controls do not validate clinical grading. Routing probes and the extra end-to-end question are separate artifacts, not added to the 42 benchmark rows.

## What the grades mean

**Fidelity** asks whether substantive answer claims are supported by the supplied, bounded evidence pool. A fail can mean unsupported detail, a mismatched citation, or a grader mistake; it does not by itself establish medical falsity. **Task fulfillment** asks whether the requested lookup or output requirements were met. The two criteria are independent: an honest abstention can avoid unsupported claims while leaving the task incomplete.

The preceding Databricks run reported **19/21 fidelity passes and 19/21 tasks fulfilled**. Those were separate tallies, not necessarily the same 19 answers. The seven paired questions are a separate comparison, not seven additional cases to add to the 21 research answers.

| Seven paired questions | MCP workflow | Plain model |
|---|---:|---:|
| Completed | {b['mcp']['completed']}/7 | {b['plain']['completed']}/7 |
| Task fulfillment | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| Median successful-attempt seconds | {b['mcp']['median_seconds']} | {b['plain']['median_seconds']} |

The earlier **MCP 7/7 versus plain model 0/7** described completion of seven source-lookup tasks. The plain arm had no retrieval tools. Zero tasks fulfilled does not mean all answers were false or medically wrong. Both arms use the same model and shared instructions; only MCP has tools, workflow enforcement and fixed notices. This measures the workflows under these conditions, not isolated model intelligence. N/A fidelity is excluded from fidelity rates. Timing is uncontrolled and excludes retries; no speed advantage is established.

## Grading limitations

Known development cases, one retained completed sample per case, changing sources, a same-family model judge, bounded references and no clinician adjudication limit the conclusions. The judge can confuse retrieved source text with final-answer text or penalize a statement outside its reference pool. In this run, D05’s grade alleges dose values absent from the final answer. Paired R03 treats an adult-label section from the evaluator’s separate reference capture as though the answer had retrieved it; the requested adult comparison nevertheless remains incomplete. Raw negative scores remain unchanged. See [technical review](TECHNICAL_REVIEW.md) and [raw findings](grading-review.json) for this run's exact findings. Required notices and passing route checks are not clinical validation and do not eliminate false reassurance or harmful framing.

MLflow evaluates precomputed fresh captures with one root span per row. Full tool-call traces and reference evidence are artifacts, not separate tool spans. Existing CLI sign-in supplies refreshable authentication. All applicable scores, including False and N/A handling, were read back from Databricks.

## Preserved history

The preceding Databricks run remains in `../databricks-validation-2026-11-21`; the earlier local run remains in `../notice-citation-revision`. Their raw outputs and source snapshots are preserved. Existing screenshots and video illustrate the prior `.4` revision; they are historical demos, not fresh `.5` validation. Current results are in this report, the updated deck and evaluation DOCX.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8')
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Routing fix and Databricks evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Routing fix and Databricks evaluation</h1><p><a href="summary.json">Metrics</a> · <a href="grading-review.json">Raw findings</a> · <a href="TECHNICAL_REVIEW.md">Technical review</a> · <a href="'+html.escape(parent['url'])+'">MLflow run</a></p><pre>'+html.escape(report)+'</pre>',encoding='utf-8')
print(json.dumps({'chat':c,'diagnostic':g,'paired':paired,'mlflow_rows':42},indent=2))
