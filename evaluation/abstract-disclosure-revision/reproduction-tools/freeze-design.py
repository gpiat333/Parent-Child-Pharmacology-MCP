from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys,subprocess,xml.etree.ElementTree as ET
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
sys.path.insert(0,str(R));from grader_contract import VERSION,JUDGE_PROMPT
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
origin=read(R/'origin.json')
assert sha(R/'cases.json')==origin['cases_sha256']
for name,digest in origin['grader_files'].items():assert sha(R/name)==digest
for name,count in [('local-unit-tests.xml',592),('grader-unit-tests.xml',30)]:
 t=ET.parse(R/name).getroot().find('testsuite');assert int(t.get('tests'))==count and all(int(t.get(k))==0 for k in ['failures','errors','skipped'])
base=read(R/'origin/local-source-freeze.json')['files'];names=sorted(set(base)|{'server/core/abstract_coverage.py','server/tests/test_abstract_coverage.py'})
snap=R/'source-snapshot';assert not snap.exists();snap.mkdir()
for name in names:
 target=snap/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,target)
save(R/'local-source-freeze.json',{'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'policy_version':'2026-11-21.10','files':{name:sha(P/name) for name in names}})
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
app=json.loads(subprocess.check_output([CLI,'apps','get','mcp-mc','--profile','gsa-mcp-hackathon','--output','json'],encoding='utf-8'))
assert app['active_deployment']['deployment_id']=='01f1e5f7f6fc162fb8c3cc875e7f8546';save(R/'app-current.json',app)
save(R/'run-design.json',{'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'grader_version':VERSION,'model':'system.ai.gpt-5-6-luna','source_policy':'2026-11-21.10','deployed_policy':'2026-11-21.9','deployment_changed_this_revision':False,'runtime_source_changed':True,'answer_generation_repeated':True,'reference_retrieval_repeated':True,'cases_unchanged':True,'grader_prompt_unchanged':True,'answer_prompt_unchanged':False,'benchmark_rows':42,'research_answers':21,'fixed_stops':7,'paired_answers':14,'calibration_controls':10,'purpose':'Test abstract disclosure and general output-grounding improvements with fresh answers and live references. No historical captures reused.','grading_protocol':'First structurally valid grade retained; up to three attempts only for invalid grading contracts. All attempts saved, unresolved errors unscored; no manual pass overrides.','scheduling':'One sequential chat generator and one sequential paired generator; four workers for offline MLflow grading. No completed answer replaced to improve a score.','limits':'Known development questions, one answer per case/arm, live-source and model variability, same-family grading, bounded reference pools, no clinician adjudication. MCP has retrieval, workflow enforcement and application notices; plain does not.','grader_prompt':JUDGE_PROMPT})
eval_names=['cases.json','paired_evaluation.py','score_current.py','deployed_grader.py','mlflow_suite.py','grader_contract.py','grader_runtime.py','model-call.ps1','databricks_transport.py','run-chats.ps1','tests/test_grader_attribution.py']
save(R/'run-design-verification.json',{'cases_unchanged':True,'grader_prompt_unchanged':True,'grader_core_byte_identical':True,'grader_version':VERSION,'runtime_source_unchanged':False,'evaluator_files':{n:sha(R/n) for n in eval_names}})
print(json.dumps({'frozen_source_files':len(names),'tests':592,'grader_tests':30,'app_deployment_unchanged':True,'fresh_answer_generation':True}))
