from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, shutil, subprocess
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/databricks-validation-2026-11-21'
OLDW=W.parent/'.submission-databricks-review'
R=P/'evaluation/brief-paraphrase-revision'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
assert not R.exists(), 'Preserve prior evidence; do not overwrite a run'
R.mkdir(parents=True)
prior=read(OLD/'local-source-freeze.json')
files={name:sha(P/name) for name in prior['files']}
changes=[name for name,digest in prior['files'].items() if files[name]!=digest]
assert set(changes)=={'server/core/workflows.py','server/core/policy.json','server/core/output_notices.json','server/tests/test_brief_workflow.py'},changes
save(R/'local-source-freeze.json',{'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'user_facing_date':'2026-11-21 America/New_York','files':files,'policy_version':'2026-11-21.5','changed_from_previous_run':changes})
shutil.copy2(OLD/'summary.json',R/'previous-deployed-summary.json')
staged={}
for source in sorted((P/'server').rglob('*')):
 if not source.is_file() or {'.databricks','.venv','.pytest_cache','__pycache__'}.intersection(source.parts):continue
 assert source.name not in {'.env','.databrickscfg'} and not source.name.startswith('.env.'),source.name
 target=W/'server'/source.relative_to(P/'server');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 staged[source.relative_to(P/'server').as_posix()]=sha(source)
save(R/'deployment-source-manifest.json',{'prepared_at_utc':datetime.now(timezone.utc).isoformat(),'source_root':str(P/'server'),'staging_root':str(W/'server'),'files':staged,'frozen_files_verified':len(files),'app':'mcp-mc','new_compute_requested':False})
for name in ['cases.json','model-call.ps1','score_current.py','paired_evaluation.py','run-chats.ps1','databricks_transport.py','deployed_grader.py','mlflow_suite.py']:
 shutil.copy2(OLD/name,R/name)
for name in ['deploy.py','probe-deployment.py','protocol-probes.py','verify-deployed-source.py','run-chat-suite.py','run-paired-suite.py','run-mlflow.py','verify-mlflow.py']:
 text=(OLDW/name).read_text(encoding='utf-8').replace('evaluation/databricks-validation-2026-11-21','evaluation/brief-paraphrase-revision').replace('2026-11-21.4','2026-11-21.5')
 text=text.replace("W/'python-deps'", "Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps')")
 text=text.replace("'chat_capture_workers':2,'paired_capture_workers':1,'mlflow_scoring_workers':2", "'chat_capture_workers':1,'paired_capture_workers':1,'mlflow_scoring_workers':1")
 (W/name).write_text(text,encoding='utf-8')
for suffix,source in [('pptx',P/'presentation/Parent-child Pharmacology MCP — Updated.pptx'),('docx',P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx')]:
 shutil.copy2(source,W/('reference.'+suffix))
save(W/'artifact-baseline.json',{'pptx':sha(W/'reference.pptx'),'docx':sha(W/'reference.docx')})
for args,name in [(['apps','get','mcp-mc'],'app-before.json'),(['experiments','get-experiment','1096079759942705'],'experiment-before.json')]:
 result=subprocess.run([CLI,*args,'--profile','gsa-mcp-hackathon','--output','json'],capture_output=True,text=True,encoding='utf-8',check=True)
 save(R/name,json.loads(result.stdout))
save(R/'run-design.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'authorization':'User requested fixing the routing gap and repeating evaluations in the existing Databricks setup before GitHub upload.','mcp_endpoint':'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','experiment_id':'1096079759942705','model':'system.ai.gpt-5-6-luna','case_count':28,'paired_questions':7,'same_cases_and_grader_as_previous':True,'additional_gap_probes':'Separate regression checks; excluded from the unchanged 28-case benchmark.','execution_location':'Local evaluation driver and local unit tests; deployed MCP app, AI Gateway model calls and managed MLflow tracking in Databricks. No cluster, warehouse or endpoint creation.','clinical_validation':False,'github_push':False})
save(R/'run-design-verification.json',{'cases_unchanged':(R/'cases.json').read_bytes()==(OLD/'cases.json').read_bytes(),'paired_answer_and_judge_prompts_unchanged':(R/'paired_evaluation.py').read_bytes()==(OLD/'paired_evaluation.py').read_bytes(),'grader_unchanged':(R/'deployed_grader.py').read_bytes()==(OLD/'deployed_grader.py').read_bytes(),'source_change':'Evidence-brief request verbs and shared negated object grammar; version increment; regression tests.','evaluator_files':{name:sha(R/name) for name in ['cases.json','paired_evaluation.py','score_current.py','run-chats.ps1','databricks_transport.py','deployed_grader.py','mlflow_suite.py']}})
print(json.dumps({'changed_source_files':changes,'frozen_files':len(files),'staged_files':len(staged),'evidence_folder':str(R)}))
