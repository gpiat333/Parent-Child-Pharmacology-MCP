from pathlib import Path
import json,os,subprocess,sys
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/report-context-revision'
os.chdir(W)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert read(R/'mlflow/pilot-verification.json')['all_applicable_scores_present']
target=R/'routing-regression/give-results.json'
if not target.exists():
 target.parent.mkdir(parents=True,exist_ok=True)
 result=subprocess.run(['pwsh','-NoProfile','-File',str(P/'chat-client/test-mcp-chat.ps1'),'-Question','Give me a pregnancy evidence brief for lamotrigine.','-Model','system.ai.gpt-5-6-luna','-McpEndpoint','https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','-OutputDirectory',str(target.parent),'-OutputPrefix','give','-ToolProfile','full','-SaveTrace'],capture_output=True,text=True,encoding='utf-8')
 (target.parent/'client.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8');assert result.returncode==0
d=read(target);assert d['completed'] and d['tool_calls'][0]['tool']=='medication_evidence_brief'
(target.parent/'verification.json').write_text(json.dumps({'question':d['question'],'completed':True,'first_evidence_tool':'medication_evidence_brief','required_workflow':d['requested_workflow'],'excluded_from_28_case_benchmark':True,'not_clinical_validation':True},indent=2),encoding='utf-8')
env=dict(os.environ);env['PYTHONPATH']=str(W.parent/'.submission-databricks-review/python-deps')+os.pathsep+str(R);env['MLFLOW_DISABLE_AGENT_HINT']='1'
commands=[('chat-captures',['pwsh','-NoProfile','-File',str(R/'run-chats.ps1')]),('paired-captures',[sys.executable,'-X','utf8',str(R/'paired_evaluation.py'),'--phase','generate'])]
running=[]
for name,command in commands:
 log=(W/(name+'.log')).open('w',encoding='utf-8')
 process=subprocess.Popen(command,env=env,cwd=W,stdout=log,stderr=subprocess.STDOUT)
 running.append((name,process,log));print('Started independent '+name,flush=True)
errors=[]
for name,process,log in running:
 code=process.wait();log.close();print(name+' finished with '+str(code),flush=True)
 if code:errors.append(name)
assert not errors,errors
for case in read(R/'cases.json'):assert read(R/'chats'/(case['id']+'-results.json'))['completed'],case['id']
for cid in ['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk']:
 for arm in ['plain','mcp']:assert read(R/'paired-final'/(cid+'-'+arm+'.json'))['completed'],(cid,arm)
subprocess.run([sys.executable,'-X','utf8',str(W/'audit-completeness.py')],check=True)
for phase in ['research','stops','paired']:
 print('Final grading phase: '+phase,flush=True)
 subprocess.run([sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase',phase],check=True,env=env)
 subprocess.run([sys.executable,'-X','utf8',str(W/'verify-mlflow.py'),phase],check=True,env=env)
subprocess.run([sys.executable,'-X','utf8',str(R/'score_current.py')],check=True,env=env)
print('Final .9 captures and all 42 MLflow readbacks completed.',flush=True)
