from pathlib import Path
import os,sys,json,subprocess,time
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
os.environ['PYTHONPATH']=r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
cases=read(R/'cases.json');pairs=['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk']
files=[R/'chats'/(c['id']+'-results.json') for c in cases]+[R/'paired-final'/(cid+'-'+arm+'.json') for cid in pairs for arm in ['mcp','plain']]
deadline=time.monotonic()+1800;last=-1
while True:
 done=0
 for f in files:
  try:done+=bool(f.exists() and read(f).get('completed'))
  except (ValueError,OSError):pass
 if done!=last:print(f'Fresh completed capture rows: {done}/42',flush=True);last=done
 if done==42:break
 if time.monotonic()>deadline:raise RuntimeError('Fresh captures incomplete; inspect generator logs before retrying')
 time.sleep(10)
def run(label,args,cwd=W):
 print('Starting '+label,flush=True)
 with (W/(label+'.log')).open('w',encoding='utf-8') as log:
  result=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=cwd,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(label+' failed; inspect '+str(W/(label+'.log')))
 print('Finished '+label,flush=True)
run('capture-lineage',[W/'capture-lineage.py'])
for phase in ['research','stops','paired']:
 run('mlflow-'+phase,[W/'run-mlflow.py','--phase',phase])
 run('verify-'+phase,[W/'verify-mlflow.py',phase])
run('summary-checks',[R/'score_current.py'],R)
run('report',[W/'report.py'])
print('Fresh evaluation and MLflow readbacks completed.',flush=True)
