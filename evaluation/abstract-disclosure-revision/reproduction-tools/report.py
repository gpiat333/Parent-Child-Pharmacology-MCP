from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,difflib,sys,statistics,xml.etree.ElementTree as ET
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision';OLD=P/'evaluation/grader-attribution-revision'
sys.path.insert(0,str(R));from paired_evaluation import CASE_IDS,MODEL
from grader_contract import valid_cached_record
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def tests(name):
 t=ET.parse(R/name).getroot().find('testsuite');return {k:int(t.get(k)) for k in ['tests','failures','errors','skipped']}
for name,count in [('local-unit-tests.xml',592),('grader-unit-tests.xml',30)]:assert tests(name)==dict(tests=count,failures=0,errors=0,skipped=0)
lineage=read(R/'capture-lineage.json');assert lineage['completed_rows']==42 and not lineage['historical_captures_reused']
for name,digest in lineage['files'].items():assert sha(R/name)==digest,name
frozen=read(R/'local-source-freeze.json')['files']
for name,digest in frozen.items():assert sha(P/name)==sha(R/'source-snapshot'/name)==digest,name
for name,digest in read(R/'run-design-verification.json')['evaluator_files'].items():assert sha(R/name)==digest,name
C=read(R/'chat-summary.json');cases=read(R/'cases.json');rows=[];paired={};findings=[];attempts=0
for arm,ids in [('chat',[c['id'] for c in cases if not c['blocked']]),('mcp',CASE_IDS),('plain',CASE_IDS)]:
 armrows=[]
 for cid in ids:
  gp=Path('chat-judgments')/(cid+'.json') if arm=='chat' else Path('paired-final')/(cid+'-'+arm+'-judge.json')
  ip=Path('chat-judge-inputs')/(cid+'.json') if arm=='chat' else Path('paired-judge-inputs')/(cid+'-'+arm+'.json')
  record=read(R/gp);assert valid_cached_record(record,read(R/ip),MODEL),(cid,arm)
  j=record['judgment'];old=read(OLD/gp)['judgment'];attempts+=len(record['attempts'])
  row={'case':cid,'arm':arm,'old_fidelity':old['fidelity_status'],'fidelity':j['fidelity_status'],'old_task':old['task_fulfilled'],'task_fulfilled':j['task_fulfilled'],'changed':old['fidelity_status']!=j['fidelity_status'] or old['task_fulfilled']!=j['task_fulfilled'],'rationale':j['rationale'],'failure_reasons':j['failure_reasons'],'grade_path':gp.as_posix()}
  rows.append(row);armrows.append(row)
  if j['fidelity_status']=='fail' or not j['task_fulfilled']:findings.append(row)
 if arm!='chat':
  ds=[read(R/'paired-final'/(cid+'-'+arm+'.json')) for cid in ids]
  paired[arm]={'completed':sum(d['completed'] for d in ds),'total':7,'task_fulfilled':sum(r['task_fulfilled'] for r in armrows),'fidelity_pass':sum(r['fidelity']=='pass' for r in armrows),'fidelity_fail':sum(r['fidelity']=='fail' for r in armrows),'fidelity_not_assessable':sum(r['fidelity']=='not_assessable' for r in armrows),'median_seconds':round(statistics.median(d['elapsed_ms'] for d in ds)/1000,2)}
verified={phase:read(R/'mlflow'/(phase+'-verification.json')) for phase in ['research','stops','paired']}
assert sum(v['rows_verified'] for v in verified.values())==42
assert all(v['assessment_errors']==0 and v['all_applicable_scores_present'] for v in verified.values())
S={'revision':'abstract-disclosure-revision','generated_at_utc':datetime.now(timezone.utc).isoformat(),'policy_version':'2026-11-21.10','deployed_policy':'2026-11-21.9','grader_version':'3.0','model':MODEL,'local_tests':tests('local-unit-tests.xml'),'grader_tests':tests('grader-unit-tests.xml'),'chat':C,'paired':paired,'grading_rows':rows,'grading_deltas':[r for r in rows if r['changed']],'remaining_negative_grades':findings,'source_files':len(frozen),'inventory':read(R/'inspector/summary.json')['inventory'],'inspector':read(R/'inspector/summary.json'),'answer_generation_repeated':True,'reference_retrieval_repeated':True,'answers_reused':0,'fresh_answers':42,'cases_unchanged':True,'grader_prompt_unchanged':True,'grader_core_byte_identical':True,'answer_prompt_unchanged':False,'previous_summary':'../grader-attribution-revision/summary.json','deployment_id':read(R/'app-current.json')['active_deployment']['deployment_id'],'app_url':read(OLD/'summary.json')['app_url'],'deployment_performed_this_revision':False,'runtime_source_changed':True,'github_push':False,'clinical_review':'Not performed','manual_score_overrides':False,'historical_raw_grades_preserved':True,'grounding_validation':{'accepted_grades':35,'all_passed':True,'model_attempts':attempts,'structural_repairs':attempts-35,'unscored_errors':0},'calibration':read(R/'calibration-summary.json'),'mlflow':{'parent':read(R/'mlflow/parent-run.json'),'runs':{phase:read(R/'mlflow'/(phase+'-run.json')) for phase in verified},'final_rows_verified':42,'assessment_errors':0},'interpretation':read(R/'run-design.json')['limits']}
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':paired,'rows':[r for r in rows if r['arm']!='chat'],'limits':S['interpretation']});save(R/'grading-review.json',{'manual_overrides':False,'clinical_adjudication':False,'findings':findings});save(R/'grading-deltas.json',{'historical_scores_modified':False,'same_answers':False,'grader_unchanged':True,'rows':rows})
S['technical_grade_audit']=read(R/'technical-grade-audit.json')
S['mlflow_recording_repair']={'initial_paired_rows_in_result_table':13,'expected':14,'action':'All 14 paired rows re-logged from the same fingerprint-validated grades; no new answers or judge calls. Initial attempt retained, excluded from final 42-row count.'}
save(R/'summary.json',S)
changes=[];patch=[]
for name in frozen:
 old=R/'source-before'/name;new=P/name
 if not old.exists() or sha(old)!=sha(new):
  changes.append({'file':name,'before_sha256':sha(old) if old.exists() else None,'after_sha256':sha(new)})
  patch.extend(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True) if old.exists() else [],new.read_text(encoding='utf-8').splitlines(True),fromfile='before/'+name,tofile='after/'+name))
save(R/'source-changes.json',{'changed_files':len(changes),'changes':changes});(R/'source-changes.diff').write_text(''.join(patch),encoding='utf-8')
g=C['diagnostic_grading'];b=paired;cal=S['calibration'];count=C['counts']
parts=['# Fresh local MCP evaluation: abstract disclosure and answer grounding','GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.',
'The prior version returned blank PubMed abstracts without an explicit coverage contract; its composite brief dropped the abstract-fetch wrapper. The local .10 version returns PMID-level coverage, distinguishes missing text, unreturned records and request failures, and preserves it through combination-product briefs. Both companion clients append the required disclosure from validated structured coverage, even when the model omits it. A later successful refetch updates the disclosure. Policy and identity stops still suppress downstream retrieval and notices. Arbitrary third-party clients must honor the payload contract themselves.',
'General response instructions now retain returned recall candidates and statuses, keep separate studies and comparator medicines separate, preserve unspecified infant specimens, and avoid unsupported methodological additions. These were development changes motivated by prior failures, not changes to the evaluation cases or grader.',
'## Verified results',
'| Measure | Current result | Scope |','|---|---:|---|',
f'| Server unit tests | {S["local_tests"]["tests"]} passed | Local final source; zero failures, errors or skips |',
'| Grader unit tests | 30 passed | Unchanged grader v3; separate suite |',
f'| Synthetic development controls | {cal["fidelity_matches"]}/{cal["controls"]} fidelity, {cal["task_matches"]}/{cal["controls"]} task | Not held-out or clinical validation |',
f'| Fresh chats completed | {count["completed"]["passed"]}/28 | 21 research + seven fixed stops |',
f'| Routes / tool selection | {count["boundary_behavior"]["passed"]}/28 / {count["tool_selection"]["passed"]}/28 | Deterministic execution checks |',
f'| Fixed stops | {count["fixed_stops"]["passed"]}/7 | No downstream evidence or model calls |',
f'| URL membership | {count["citation_provenance"]["passed"]}/21 | Membership is not claim support |',
f'| Research fidelity | {g["fidelity_pass"]} pass / {g["fidelity_fail"]} fail / {g["fidelity_not_assessable"]} N/A | Model judgment against bounded retrieved pool |',
f'| Research tasks fulfilled | {g["task_fulfilled"]}/21 | Separate requested-output completeness |',
'| MLflow rows verified | 42/42 | 21 research + seven stops + 14 paired; zero scorer errors |',
f'| MCP Inspector | {S["inspector"]["passed"]}/{S["inspector"]["checks"]} checks | Local protocol and tool checks; not clinical validation |',
'## Fresh paired comparison','| Measure | MCP | Plain model |','|---|---:|---|',
f'| Completed answers | {b["mcp"]["completed"]}/7 | {b["plain"]["completed"]}/7 |',
f'| Tasks fulfilled | {b["mcp"]["task_fulfilled"]}/7 | {b["plain"]["task_fulfilled"]}/7 |',
f'| Fidelity pass / fail / N/A | {b["mcp"]["fidelity_pass"]} / {b["mcp"]["fidelity_fail"]} / {b["mcp"]["fidelity_not_assessable"]} | {b["plain"]["fidelity_pass"]} / {b["plain"]["fidelity_fail"]} / {b["plain"]["fidelity_not_assessable"]} |',
'Both arms use the same model and shared application instructions, with newly retrieved reference pools. Retrieval uses the normal source clients, including their caches and dated snapshots; fresh tool calls do not imply that every upstream record is newly updated. Only MCP receives tools, enforced routing and application notices. The main chat companion also has an extra source-review pass that the paired runner does not use. A shared pool can contain evidence the plain answer never received. Honest abstention can leave a requested lookup incomplete. This is a workflow comparison, not proof of superior intrinsic model ability, clinical accuracy or speed.',
'## Grading limits and historical comparison',
'The previous .9 captures, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The new scores come from fresh .10 answers and live references. Cases and grader core are byte-identical, but prompts, application code, live sources and model outputs can differ. This is not a controlled causal estimate of the code change. Older results remain historical, including .5 research tasks 18/21 and paired MCP 5/7.',
f'The unchanged grader v3 accepted 35 grades in {attempts} model attempts ({attempts-35} structural correction attempts). It validates answer quotations for negative content claims, anchors omissions to requested requirements, and binds citation IDs to original answer URLs. It retains the first structurally valid grade, including failures. No manual score overrides occurred. Literal quotation checks do not establish semantic correctness, clinical importance or safety. The ten synthetic controls are known development cases.',
'Fidelity asks whether factual claims are supported by the captured pool. Task fulfillment asks whether the requested work was completed. These measures are separate. Unverified in a bounded pool does not prove medically false; N/A means no assessable source claims and is excluded from fidelity rates. The same-family judge is fallible. One answer per known development case and no independent clinician review limit all results.',
'## Targeted cases']
for cid,arm in [('E01-gap','chat'),('E01-gap','mcp'),('R04','chat'),('R12','chat'),('R01','mcp')]:
 row=next(r for r in rows if r['case']==cid and r['arm']==arm)
 parts.append(f'**{cid} / {arm}: fidelity {row["fidelity"]}; task fulfilled {row["task_fulfilled"]}.** {row["rationale"]}')
parts+=['## Remaining negative grades']
for row in findings:parts.append(f'- {row["case"]} / {row["arm"]}: fidelity {row["fidelity"]}, task {row["task_fulfilled"]}. {row["rationale"]}')
parts+=['## Technical review of grader limitations']
for item in S['technical_grade_audit']['findings']:parts.append('**'+item['case']+' / '+item['arm']+':** '+item['interpretation'])
parts+=['The numerical grades remain unchanged. The audit demonstrates why the model grader is not an authoritative human assessment: a structurally valid rationale can still misdescribe a candidate or apply a broad requirement too strictly. See [technical-grade-audit.json](technical-grade-audit.json).',
'## MLflow recording repair',S['mlflow_recording_repair']['action']+' The initial run created 14 traces but returned only 13 scored result-table rows; the readback caught that mismatch. It is a tracking failure, not an extra model-performance sample.']
parts+=['## Where work ran',f'Application changes are in the submission folder’s `server` and `chat-client`; this revision’s evidence is in `evaluation/abstract-disclosure-revision`. The MCP ran on local loopback. Unit tests, MCP Inspector, answer drivers and offline evaluation orchestration ran locally. Model calls, grading model calls and MLflow tracking used existing Databricks services. These were not remote notebook unit tests. The deployed app remains policy .9, deployment `{S["deployment_id"]}`. No deployment, infrastructure or permission change, GitHub upload or official submission occurred.',f'The [MLflow parent run]({S["mlflow"]["parent"]["url"]}) records the fresh evaluation and updated artifacts. Every one of the 42 saved evaluation rows was read back. Full tool traces are retained in artifacts; offline grading creates a root evaluation span per row. See [summary.json](summary.json), [source-changes.diff](source-changes.diff), [capture-lineage.json](capture-lineage.json), [run-design.json](run-design.json), and [grading-review.json](grading-review.json). Saved .4 demo screenshots and video remain historical; no new demonstration video was generated.']
(R/'REPORT.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')
(R/'TECHNICAL_REVIEW.md').write_text('# Technical review of fresh .10 grades\n\nNo score overrides or clinician adjudication.\n\n'+'\n\n'.join(f'## {r["case"]} / {r["arm"]}\n\n{r["rationale"]}\n\n```json\n'+json.dumps(r['failure_reasons'],indent=2,ensure_ascii=False)+'\n```' for r in findings),encoding='utf-8')
with (R/'TECHNICAL_REVIEW.md').open('a',encoding='utf-8') as f:f.write('\n\n## Evidence-based audit, without score overrides\n\n'+'\n\n'.join(x['case']+': '+x['interpretation'] for x in S['technical_grade_audit']['findings']))
print(json.dumps({'research':g,'paired':paired,'source_changes':len(changes),'mlflow_verified':42},indent=2))
