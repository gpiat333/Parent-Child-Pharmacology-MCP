from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision';OLD=P/'evaluation/report-context-revision'
sys.path.insert(0,str(R))
from grader_contract import VERSION,JUDGE_PROMPT
from paired_evaluation import MODEL
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pilot=read(R/'pilot-verification.json')
assert pilot['calibration']['controls']==10
assert pilot['calibration']['fidelity_matches']==pilot['calibration']['task_matches']==10,pilot
# Qualification checks attribution, not a desired pass score on E01.
from grader_contract import valid_cached_record
for grade_name,input_name in [('chat-judgments/E01-gap.json','chat-judge-inputs/E01-gap.json'),('paired-final/E01-gap-mcp-judge.json','paired-judge-inputs/E01-gap-mcp.json')]:
    assert valid_cached_record(read(R/grade_name),read(R/input_name),MODEL)
for name,digest in read(R/'capture-lineage.json')['files'].items():assert sha(R/name)==sha(OLD/name)==digest
for name,digest in read(R/'local-source-freeze.json')['files'].items():assert sha(P/name)==digest
for name,expected in [('local-unit-tests.xml',562),('grader-unit-tests.xml',30)]:
    suite=ET.parse(R/name).getroot().find('testsuite')
    assert int(suite.get('tests'))==expected and all(int(suite.get(k))==0 for k in ['failures','errors','skipped'])
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
app=json.loads(subprocess.check_output([CLI,'apps','get','mcp-mc','--profile','gsa-mcp-hackathon','--output','json'],encoding='utf-8'))
assert app['active_deployment']['deployment_id']==read(OLD/'summary.json')['deployment_id']
assert app['active_deployment']['status']['state']=='SUCCEEDED' and app['app_status']['state']=='RUNNING'
(R/'app-current.json').write_text(json.dumps(app,indent=2),encoding='utf-8')
design={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'grader_version':VERSION,'model':MODEL,
 'source_policy':'2026-11-21.9','deployment_changed_this_revision':False,'runtime_source_changed':False,
 'answer_generation_repeated':False,'reference_retrieval_repeated':False,'cases_unchanged':True,
 'grader_prompt_unchanged':False,'answer_prompt_unchanged':True,'old_grader':'v2','new_grader':'v3',
 'purpose':'Isolate the grader correction by regrading the exact retained .9 answers and references.',
 'benchmark_rows':42,'research_answers':21,'fixed_stops':7,'paired_answers':14,
 'calibration_controls':10,'E01_pilot_grades_reused_once':2,
 'grading_protocol':'First structurally valid grade retained. Up to three attempts only for invalid JSON, attribution, citation inventory or schema. All attempts saved. Unresolved contract errors receive no score; no manual pass overrides.',
 'scheduling':'Four MLflow workers per sequential research, stops and paired phase. Calibration and E01 pilot ran concurrently with at most two active model calls. No answers regenerated; prior answer latencies are historical, not a new timing comparison.',
 'limits':'Known development cases, same-family model grading, bounded shared reference pools, no clinician adjudication. Literal quote checks do not prove semantic correctness.',
 'grader_prompt':JUDGE_PROMPT}
(R/'run-design.json').write_text(json.dumps(design,indent=2),encoding='utf-8')
names=['cases.json','paired_evaluation.py','score_current.py','deployed_grader.py','mlflow_suite.py','grader_contract.py','grader_runtime.py','model-call.ps1','databricks_transport.py','tests/test_grader_attribution.py']
verified={'cases_unchanged':sha(R/'cases.json')==sha(OLD/'cases.json'),'captures_byte_identical':True,'runtime_source_unchanged':True,
          'grader_version':VERSION,'grader_prompt_unchanged':False,'evaluator_files':{name:sha(R/name) for name in names}}
(R/'run-design-verification.json').write_text(json.dumps(verified,indent=2),encoding='utf-8')
print(json.dumps({'frozen_evaluator_files':len(names),'retained_capture_files':len(read(R/'capture-lineage.json')['files']),'app_unchanged':True}))
