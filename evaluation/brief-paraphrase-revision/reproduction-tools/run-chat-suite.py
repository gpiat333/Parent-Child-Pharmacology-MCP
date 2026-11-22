from pathlib import Path
import os,sys,json,subprocess
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/brief-paraphrase-revision')
assert json.loads((R/'mlflow/pilot-verification.json').read_text())['all_applicable_scores_present']
env=dict(os.environ);env['PYTHONPATH']=str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps'))+os.pathsep+str(R);env['MLFLOW_DISABLE_AGENT_HINT']='1'
commands=[['pwsh','-NoProfile','-File',str(R/'run-chats.ps1')],
 [sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase','research'],
 [sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase','stops'],
 [sys.executable,'-X','utf8',str(R/'score_current.py')]]
for i,command in enumerate(commands):
 print('Chat stage:',command[-1],flush=True)
 if i==1:
  cases=json.loads((R/'cases.json').read_text());incomplete=[c['id'] for c in cases if not (R/'chats'/(c['id']+'-results.json')).exists() or not json.loads((R/'chats'/(c['id']+'-results.json')).read_text(encoding='utf-8-sig')).get('completed')]
  if incomplete:raise RuntimeError('Retain and inspect incomplete cases: '+','.join(incomplete))
 subprocess.run(command,check=True,env=env)
print('Full deployed chat and MLflow suite completed.',flush=True)
