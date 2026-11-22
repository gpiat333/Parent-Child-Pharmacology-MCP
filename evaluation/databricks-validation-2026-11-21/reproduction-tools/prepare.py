from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/notice-citation-revision'
R=P/'evaluation/databricks-validation-2026-11-21'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
assert not R.exists(),'Use a new evaluation folder; do not replace existing evidence'
R.mkdir(parents=True)
freeze=read(OLD/'source-freeze.json')
for name,digest in freeze['files'].items():assert sha(P/name)==digest,name
shutil.copy2(OLD/'source-freeze.json',R/'local-source-freeze.json')
shutil.copy2(OLD/'summary.json',R/'previous-local-summary.json')
shutil.copy2(OLD/'unit-tests.xml',R/'local-unit-tests.xml')
files={}
for source in sorted((P/'server').rglob('*')):
 if not source.is_file() or {'.databricks','.venv','.pytest_cache','__pycache__'}.intersection(source.parts):continue
 assert source.name not in {'.env','.databrickscfg'} and not source.name.startswith('.env.'),source.name
 target=W/'server'/source.relative_to(P/'server');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 files[source.relative_to(P/'server').as_posix()]=sha(source)
save(R/'deployment-source-manifest.json',{'prepared_at_utc':datetime.now(timezone.utc).isoformat(),'source_root':str(P/'server'),'staging_root':str(W/'server'),'files':files,'prior_frozen_files_verified':len(freeze['files']),'app':'mcp-mc','new_compute_requested':False})
for name in ['cases.json','model-call.ps1','score_current.py','paired_evaluation.py','run-chats.ps1']:
 shutil.copy2(OLD/name,R/name)
for args,name in [(['apps','get','mcp-mc'],'app-before.json'),(['experiments','get-experiment','1096079759942705'],'experiment-before.json')]:
 result=subprocess.run([CLI,*args,'--profile','gsa-mcp-hackathon','--output','json'],capture_output=True,text=True,encoding='utf-8',check=True)
 save(R/name,json.loads(result.stdout))
save(R/'run-design.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'authorization':'User requested updating the existing Databricks app and running MLflow evaluations; GitHub deferred.','mcp_endpoint':'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','experiment_id':'1096079759942705','model':'system.ai.gpt-5-6-luna','case_count':28,'paired_questions':7,'same_cases_and_grader_as_local':True,'execution_location':'Local evaluation driver; deployed MCP app, AI Gateway model calls and managed MLflow tracking in Databricks. No cluster, warehouse or endpoint creation.','clinical_validation':False,'github_push':False})
print(json.dumps({'frozen_files_verified':len(freeze['files']),'staged_files':len(files),'evidence_folder':str(R)}))
