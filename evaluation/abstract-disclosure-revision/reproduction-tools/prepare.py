from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');OLD=P/'evaluation/grader-attribution-revision';R=P/'evaluation/abstract-disclosure-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not R.exists(),'Inspect existing revision before resuming.'
R.mkdir();(R/'origin').mkdir()
freeze=read(OLD/'local-source-freeze.json')
for name,digest in freeze['files'].items():assert sha(P/name)==digest,name
for name in ['summary.json','local-source-freeze.json','run-design.json','final-validation.json']:
 shutil.copy2(OLD/name,R/'origin'/name)
for name in ['cases.json','model-call.ps1','grader_contract.py','grader_runtime.py','score_current.py','deployed_grader.py','mlflow_suite.py']:
 shutil.copy2(OLD/name,R/name)
shutil.copytree(OLD/'tests',R/'tests',ignore=shutil.ignore_patterns('__pycache__'))
for name in ['paired_evaluation.py','run-chats.ps1','databricks_transport.py']:
 shutil.copy2(P/'evaluation/report-context-revision'/name,R/name)
for src,dst in [(P/'presentation/Parent-child Pharmacology MCP — Updated.pptx',W/'reference.pptx'),(P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx',W/'reference.docx')]:shutil.copy2(src,dst)
(W/'artifact-references.json').write_text(json.dumps({p.name:sha(p) for p in [W/'reference.pptx',W/'reference.docx']},indent=2),encoding='utf-8')
for relative in freeze['files']:
 dst=R/'source-before'/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/relative,dst)
(R/'origin.json').write_text(json.dumps({'created_at_utc':datetime.now(timezone.utc).isoformat(),'prior_revision':'grader-attribution-revision','prior_policy':'2026-11-21.9','grader_version':'3.0','fresh_answer_generation_required':True,'fresh_reference_retrieval_required':True,'no_deployment':True,'no_github_upload':True,'local_endpoint':'http://127.0.0.1:8770/mcp','cases_sha256':sha(R/'cases.json'),'grader_files':{n:sha(R/n) for n in ['grader_contract.py','grader_runtime.py']}},indent=2),encoding='utf-8')
print('Prepared a separate fresh-evaluation revision; no old captures copied.')
