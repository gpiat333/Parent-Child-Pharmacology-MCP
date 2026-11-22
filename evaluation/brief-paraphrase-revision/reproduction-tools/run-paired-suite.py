from pathlib import Path
import os,sys,json,subprocess
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/brief-paraphrase-revision')
assert json.loads((R/'mlflow/pilot-verification.json').read_text())['all_applicable_scores_present']
env=dict(os.environ);env['PYTHONPATH']=str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps'))+os.pathsep+str(R);env['MLFLOW_DISABLE_AGENT_HINT']='1'
for command in [[sys.executable,'-X','utf8',str(R/'paired_evaluation.py'),'--phase','generate'],[sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase','paired']]:
 print('Paired stage:',command[-1],flush=True);subprocess.run(command,check=True,env=env)
print('Seven deployed pairs and MLflow grading completed.',flush=True)
