from pathlib import Path
from datetime import datetime, timezone
import json, statistics, html, sys, xml.etree.ElementTree as ET
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/report-context-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sys.path.insert(0,str(P/'server'))
from core.output_notices import required_notices
cases=read(R/'cases.json');C=read(R/'chat-summary.json');checks=read(R/'chat-checks.json')
u=ET.parse(R/'local-unit-tests.xml').getroot().find('testsuite')
unit={k:int(u.get(k)) for k in ['tests','failures','errors','skipped']}
assert unit==dict(tests=562,failures=0,errors=0,skipped=0)
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
S={'revision':'brief-paraphrase-revision','policy_version':'2026-11-21.9','generated_at_utc':datetime.now(timezone.utc).isoformat(),'local_tests':unit,'source_files':114,'deployed_runtime_files_verified':93,'inventory':read(R/'deployment-probes.json')['inventory'],'chat':C,'paired':paired,'paired_rows':rows,'protocol_probes':20,'valid_tool_schemas':30,'invalid_input_rejections':8,'workflow_requirements':workflow,'required_notice_records':sum(bool(n['expected_ids']) for n in notices),'required_notices_preserved':True,'deployment_id':source['deployment_id'],'app_url':app['url'],'model':'system.ai.gpt-5-6-luna','deployed':True,'deployment_scope':'Updated existing Databricks sandbox app; no new compute or infrastructure','github_push':False,'clinical_review':'Not performed','evaluation_driver':'Local driver and local unit tests; MCP app, model gateway and MLflow tracking in Databricks','mlflow':{'parent':parent,'runs':{p:read(R/'mlflow'/(p+'-run.json')) for p in ['research','stops','paired']},'final_rows_verified':42,'assessment_errors':0,'capture_mode':'Precomputed fresh deployed captures; one root span per row; full tool traces in artifacts'},'first_attempt_chat_completion':retry['initial_completion'],'retried_chat_cases':retry['retried_cases'],'cases_unchanged':True,'grader_prompt_unchanged':True,'shared_paired_prompt_clarified_for_both_arms':True,'routing_regression':regression,'additional_routing_observation':extra,'interpretation':'Known development cases; one completed sample each; changing live sources; same-family diagnostic judge; bounded reference pool; no clinician adjudication. Workflow comparison, not clinical accuracy or isolated model ability.'}
S['revision']='report-context-revision'
S['additional_unit_cases']=5
S['pilot_answers_reused']=2
S['paired_pilot_answers_reused']=2
S['additional_unit_cases_since_submission_baseline']=31
S['scheduling']=read(R/'run-design.json')['scheduling']
S['report_context_observation']=read(R/'pilot-paired-observation.json')
S['task_completeness_observation']=read(R/'task-completeness-observation.json')
S['cumulative_source_changes']=read(R/'cumulative-source-changes.json')
S['grading_review_note']=(W/'grading-note.txt').read_text(encoding='utf-8').strip() if (W/'grading-note.txt').exists() else 'Raw diagnostic grades are retained; prior runs demonstrate reference-to-answer attribution errors. No clinician adjudication.'
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
prior=read(R/'previous-deployed-summary.json')
report=f"""# Final report-context evaluation

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

Policy `{S['policy_version']}` fixes incomplete source presentation and preserves uncertainty. The cumulative changes retain available LactMed sections, extract exact numeric concentration passages, retain adult and population sections from the same selected label, include an explicit retrieved count for each requested fiscal year, preserve the FAERS population caveat, and distinguish maternal endpoints from offspring measurements.

The final repair makes FAERS report terms and counts visible in a separate `report_only_context` field. An empty observed-outcomes row no longer implies that no human reports were retrieved. Report counts remain unconfirmed signals: they do not establish outcomes, rates, causation, or the patient's population. Shared production instructions also require neutral source-attributed wording instead of an added reassuring or alarming verdict. The same clarification is supplied to both paired arms.

The existing Databricks sandbox app was updated to `{S['deployment_id']}`. No GitHub upload or official submission occurred. No new infrastructure or permissions were created. Unit tests and the driver ran locally; the app, model gateway and MLflow tracking ran in Databricks.

## Verified results

| Measure | Result | Meaning |
|---|---:|---|
| Local unit tests | 562 passed | Zero failures, errors or skips; 31 added since .5, including five for report context |
| Frozen source / verified runtime | 114 / 93 files | Active runtime matches staged files byte for byte |
| Inventory | 30 tools / 4 prompts / 4 resources | Existing sandbox |
| Schemas / invalid calls | 30 valid / 8 rejected | Runtime contracts |
| Source/workflow captures | 20 | Partial and empty statuses retained, not clinical passes |
| Separate routing probes | 12/12 | Outside the unchanged benchmark |
| Original missed brief question | Completed; brief first | Separate end-to-end regression |
| First-attempt / final chats | {S['first_attempt_chat_completion']}/28 / {c['completed']['passed']}/28 | Completed answers were not regenerated |
| Expected routes / tool selections | {c['boundary_behavior']['passed']}/28 / {c['tool_selection']['passed']}/28 | Required/allowed checks |
| Fixed stops | {c['fixed_stops']['passed']}/7 | Zero downstream evidence/model calls |
| URL membership | {c['citation_provenance']['passed']}/21 | URL presence is not claim support |
| Research fidelity | {g['fidelity_pass']} pass / {g['fidelity_fail']} fail / {g['fidelity_not_assessable']} N/A | Fallible model grades |
| Research tasks fulfilled | {g['task_fulfilled']}/21 | Seven fixed stops excluded |
| Required notices retained | {S['required_notice_records']}/{S['required_notice_records']} | Fixed application text |
| Final MLflow rows verified | 42/42 | 21 research + 7 stops + 14 paired; zero scorer execution errors |

Four synthetic controls matched {C['calibration']['fidelity_matches']}/4 fidelity and {C['calibration']['task_matches']}/4 task expectations. This does not validate the grader or establish clinical accuracy.

## Seven paired questions

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed answers | {b['mcp']['completed']}/7 | {b['plain']['completed']}/7 |
| Tasks fulfilled | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| Median successful-attempt seconds | {b['mcp']['median_seconds']} | {b['plain']['median_seconds']} |

Only MCP has retrieval, enforced workflows and fixed notices. The paired runner omits the companion's extra source-review stage. Honest abstention can leave a lookup incomplete; a task score is separate from source fidelity. This compares workflows, not isolated model ability. N/A is excluded from fidelity rates. Timings are uncontrolled and establish no speed advantage.

## Why the earlier figures changed

The .5 drop from paired MCP 7/7 to 5/7 came from two newly generated answers: R01 omitted quantitative milk findings and inferred monitoring advice from study observations; R03 left the adult warning comparison incomplete. The preceding routing-only change did not alter those tools or paired instructions, so the score change does not establish that routing caused the failures. Answers, live sources and model judgments vary.

The .5 research score 18/21 meant three answers were graded incomplete: R12 omitted a generalizability caveat, P01 omitted the numeric empty-year count, and D05 received a disputed dose allegation plus an axis-placement concern. These were model task grades, not unit-test failures.

| Historical revision | Local tests | Research fidelity / tasks | Paired tasks MCP / plain |
|---|---:|---|---|
| .4 | 508 | 19/21 / 19/21 | 7/7 / 0/7 |
| .5 | 531 | 21/21 / 18/21 | 5/7 / 0/7 |
| Intermediate .6 | 548 | 20/21 / 20/21 | 5/7 / 1/7 |
| Intermediate .8 | 557 | 20/21 / 18/21 | Full pairs intentionally not run |

The .6 run fixed the preceding research omissions and adult-label comparison, but the numeric-concentration omission persisted in paired R01. A payload-only .7 pilot also failed that requirement; both failed versions remain preserved. The .8 shared concentration clarification passed its R01 paired pilot. Its research run then exposed the omitted report context in E01 and added reassuring wording in S6-pregnancy. The .8 full paired phase was intentionally stopped before generation so these further presentation issues could be repaired; it is not a complete paired benchmark. Its separate D05 task failure quotes reference doses absent from the answer, documented in the [historical exact-text audit](../exposure-contract-revision/grader-attribution-audit.json). No historical score was changed.

## Method and limitations

The model, 28 questions, seven paired questions, criteria and grader v2 are retained. Both arms load the same production concentration, report-context and neutral-framing instructions. The answer prompt intentionally changed; the judge prompt did not. Two research pilot answers and one paired question's two answers are reused once in the final set, not extra independent samples. The final iteration changes six source files and adds five unit cases. All 15 changed source files since .5 are in the [cumulative diff](cumulative-source-changes.diff).

{S['scheduling']}

The [MLflow parent run]({parent['url']}) records precomputed fresh deployed captures with one root span per row; full tool traces and references are artifacts. This is not a remote notebook or cluster unit-test run. Existing refreshable CLI sign-in supplies authentication.

Fidelity asks whether substantive claims are supported by the bounded captured pool. Task fulfillment asks whether the lookup and output requirements were met; one omitted requirement can fail a whole task. A source-supported answer can still be incomplete. Unsupported in the captured pool does not by itself establish medical falsity. A URL match does not establish claim support.

{S['grading_review_note']}

Known development questions, one completed sample per arm, changing sources, same-family model grading, bounded references and no clinician adjudication limit the findings. Exact negatives and technical observations are retained in [TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md) and [grading-review.json](grading-review.json). Raw model scores are not overridden. Passing execution checks and required notices do not establish clinical safety, sensitivity or general accuracy.

## Artifacts

Changes are in this submission folder's `server` and `chat-client` directories. The source freeze and active deployment hashes identify the evaluated version. The deck, evaluation DOCX and package entry points use this final revision. Saved screenshots and video illustrate .4 and remain labeled historical. No GitHub upload occurred.
"""
(R/'REPORT.md').write_text(report,encoding='utf-8')
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Final report-context evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Final report-context evaluation</h1><p><a href="summary.json">Metrics</a> · <a href="TECHNICAL_REVIEW.md">Technical review</a> · <a href="'+html.escape(parent['url'])+'">MLflow run</a></p><pre>'+html.escape(report)+'</pre>',encoding='utf-8')
print(json.dumps({'chat':c,'diagnostic':g,'paired':paired,'mlflow_rows':42},indent=2))
