from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,difflib,xml.etree.ElementTree as ET,ast
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/exposure-contract-revision';R=P/'evaluation/report-context-revision'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
assert not R.exists(),'Preserve existing evidence'
assert read(OLD/'INTERMEDIATE_STATUS.json')['full_benchmark_complete'] is False
suite=ET.parse(W/'local-unit-tests.xml').getroot().find('testsuite')
assert int(suite.get('tests'))==562 and all(int(suite.get(k,0))==0 for k in ['failures','errors','skipped'])
prior=read(OLD/'local-source-freeze.json')
for name,digest in prior['files'].items():
 assert sha(OLD/'source-snapshot'/name)==digest,name
 assert sha(P/name)==digest,'Submission changed before candidate promotion: '+name
candidate=W/'candidate'
changes=[name for name,digest in prior['files'].items() if sha(candidate/name)!=digest]
assert len(changes)==6,changes
for name in changes:shutil.copy2(candidate/name,P/name)
R.mkdir(parents=True)
files={name:sha(P/name) for name in prior['files']}
save(R/'local-source-freeze.json',{'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'user_facing_date':'2026-11-21 America/New_York','files':files,'policy_version':'2026-11-21.9','changed_from_previous_run':changes})
diff=[]
for name in changes:diff.extend(difflib.unified_diff((OLD/'source-snapshot'/name).read_text(encoding='utf-8').splitlines(True),(P/name).read_text(encoding='utf-8').splitlines(True),fromfile='before-.8/'+name,tofile='after-.9/'+name))
(R/'source-changes.diff').write_text(''.join(diff),encoding='utf-8')
shutil.copy2(W/'local-unit-tests.xml',R/'local-unit-tests.xml');shutil.copy2(OLD/'summary.json',R/'previous-deployed-summary.json')
staged={}
for source in sorted((P/'server').rglob('*')):
 if not source.is_file() or {'.databricks','.venv','.pytest_cache','__pycache__'}.intersection(source.parts):continue
 assert source.name not in {'.env','.databrickscfg'} and not source.name.startswith('.env.')
 target=W/'server'/source.relative_to(P/'server');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 staged[source.relative_to(P/'server').as_posix()]=sha(source)
save(R/'deployment-source-manifest.json',{'prepared_at_utc':datetime.now(timezone.utc).isoformat(),'source_root':str(P/'server'),'staging_root':str(W/'server'),'files':staged,'frozen_files_verified':len(files),'app':'mcp-mc','new_compute_requested':False})
names=['cases.json','model-call.ps1','score_current.py','paired_evaluation.py','run-chats.ps1','databricks_transport.py','deployed_grader.py','mlflow_suite.py']
for name in names:shutil.copy2(OLD/name,R/name)
paired=R/'paired_evaluation.py'
text=paired.read_text(encoding='utf-8').replace('Same model, unchanged shared instructions,','Same model, shared production instructions clarified for report context and neutral framing in both arms,')
paired.write_text(text,encoding='utf-8')
def literal(path,name):
 return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
assert literal(paired,'JUDGE_PROMPT')==literal(OLD/'paired_evaluation.py','JUDGE_PROMPT')
for suffix,source in [('pptx',P/'presentation/Parent-child Pharmacology MCP — Updated.pptx'),('docx',P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx')]:shutil.copy2(source,W/('reference.'+suffix))
save(W/'artifact-baseline.json',{s:sha(W/('reference.'+s)) for s in ['pptx','docx']})
for args,name in [(['apps','get','mcp-mc'],'app-before.json'),(['experiments','get-experiment','1096079759942705'],'experiment-before.json')]:
 result=subprocess.run([CLI,*args,'--profile','gsa-mcp-hackathon','--output','json'],capture_output=True,text=True,encoding='utf-8',check=True);save(R/name,json.loads(result.stdout))
save(R/'run-design.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'authorization':'Fix remaining Mother-child MCP task failures, rerun Databricks evaluations and update local submission artifacts; no GitHub upload.','mcp_endpoint':'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','experiment_id':'1096079759942705','model':'system.ai.gpt-5-6-luna','case_count':28,'paired_questions':7,'same_cases_and_grader_as_previous':True,'paired_system_prompt_unchanged':False,'shared_prompt_clarification_applies_to_both_arms':True,'companion_instructions_changed':'Shared production instructions distinguish report-only FAERS context from observed outcomes and require neutral source-attributed framing. Prior concentration clarification is retained.','source_change':'Explicit report-only outcome context, without promoting report counts into confirmed outcomes, plus neutral source-attributed wording.','scheduling':'Chat and paired captures each use one worker and run as independent concurrent pipelines. Inter-case chat pause is two seconds. MLflow grading uses four workers per sequential phase. Timing is uncontrolled and no speed comparison is claimed.','pilot_reuse':'Two research pilot answers and one paired question (two arms) are retained once in the final benchmark, not additional independent samples.','execution_location':'Local driver and unit tests; deployed app, AI Gateway and MLflow tracking in Databricks.','clinical_validation':False,'github_push':False})
save(R/'run-design-verification.json',{'cases_unchanged':sha(R/'cases.json')==sha(OLD/'cases.json'),'paired_answer_and_judge_prompts_unchanged':False,'grader_prompt_unchanged':True,'shared_instructions_applied_to_both_arms':True,'shared_prompt_file_sha256':sha(P/'chat-client/exposure-presentation-instructions.txt'),'grader_unchanged':sha(R/'deployed_grader.py')==sha(OLD/'deployed_grader.py'),'source_change':'Report-only context and neutral framing; same shared production instructions for both arms.','scheduling_changed':True,'evaluator_files':{name:sha(R/name) for name in names}})
print(json.dumps({'tests':562,'frozen_files':len(files),'changed_files':changes,'staged_files':len(staged),'folder':str(R)},indent=2))
