from pathlib import Path
import os,subprocess,sys
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
env=dict(os.environ);env['PYTHONPATH']=str(W.parent/'.submission-databricks-review/python-deps')+os.pathsep+str(R)
env['MLFLOW_DISABLE_AGENT_HINT']='1'
subprocess.run([sys.executable,'-X','utf8',str(W/'freeze-design.py')],check=True,env=env)
for phase in ['research','stops','paired']:
    print('V3 replay phase: '+phase,flush=True)
    subprocess.run([sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase',phase],check=True,env=env)
    subprocess.run([sys.executable,'-X','utf8',str(W/'verify-mlflow.py'),phase],check=True,env=env)
subprocess.run([sys.executable,'-X','utf8',str(R/'score_current.py')],check=True,env=env)
print('All 42 retained benchmark rows regraded and verified with v3.',flush=True)
