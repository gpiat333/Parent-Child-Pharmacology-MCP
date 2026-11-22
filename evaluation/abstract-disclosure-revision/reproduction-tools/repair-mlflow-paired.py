from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,hashlib,subprocess,shutil
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision';D=R/'mlflow';A=D/'initial-paired-trace-gap'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=read(D/'paired-eval_results.json');assert len(rows)==13
assert read(D/'paired-run.json')['rows']==14
assert not A.exists();A.mkdir()
frozen={f.relative_to(R).as_posix():sha(f) for folder,pattern in [('paired-final','*.json'),('paired-judge-inputs','*.json')] for f in (R/folder).glob(pattern)}
for name in ['paired-run.json','paired-started.json','paired-eval_results.json','paired-verification.json']:
 f=D/name
 if f.exists():
  target=A/name;assert f.resolve().is_relative_to(R.resolve()) and target.resolve().is_relative_to(R.resolve());f.rename(target)
for name in ['mlflow-paired.log','verify-paired.log']:
 f=W/name
 if f.exists():shutil.copy2(f,A/name)
record={'reason':'Initial paired MLflow run recorded only 13 of 14 evaluation rows; one trace was unavailable. Re-log all 14 rows using fingerprint-validated saved grades. No answer generation, retrieval, judge call or score change is permitted by this repair.','created_at_utc':datetime.now(timezone.utc).isoformat(),'initial_run':read(A/'paired-run.json'),'initial_table_rows':13,'expected_rows':14,'frozen_paired_files':frozen}
(A/'repair-design.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
os.environ['PYTHONPATH']=r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps'
for label,args,cwd in [('mlflow-paired-repair',[W/'run-mlflow.py','--phase','paired'],W),('verify-paired-repair',[W/'verify-mlflow.py','paired'],W),('summary-checks',[R/'score_current.py'],R),('report',[W/'report.py'],W)]:
 print('Starting '+label,flush=True)
 with (W/(label+'.log')).open('w',encoding='utf-8') as log:r=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=cwd,stdout=log,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(label+' failed; inspect log')
 for name,digest in frozen.items():assert sha(R/name)==digest,('Repair modified evidence or grades',name)
 print('Finished '+label,flush=True)
record['final_run_id']=read(D/'paired-run.json')['run_id'];record['final_rows_verified']=read(D/'paired-verification.json')['rows_verified'];record['answers_and_grades_unchanged']=True
(D/'trace-recording-repair.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print('Paired tracing repaired with unchanged answers and grades.',flush=True)
