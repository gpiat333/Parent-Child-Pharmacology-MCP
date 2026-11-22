from pathlib import Path
import json,shutil,hashlib
from datetime import datetime,timezone
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/databricks-validation-2026-11-21')
cases=json.loads((R/'cases.json').read_text());rows=[]
archive=R/'incomplete-attempts/chat-http429-attempt1';archive.mkdir(parents=True,exist_ok=True)
for c in cases:
    path=R/'chats'/(c['id']+'-results.json');raw=json.loads(path.read_text(encoding='utf-8-sig'))
    if not raw['completed']:
        assert raw['failure']=='HttpResponseException (HTTP 429)',raw['failure']
        dst=archive/path.name
        assert not dst.exists()
        shutil.copy2(path,dst)
        rows.append({'case':c['id'],'first_attempt_failure':raw['failure'],'archive':str(dst.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'action':'retry incomplete case only, after paired grading, at chat concurrency one'})
assert len(rows)==4
(R/'retry-chats.json').write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),'rows':rows,'completed_answers_unchanged':True},indent=2),encoding='utf-8')
p=R/'run-chats.ps1';p.write_text(p.read_text().replace('-ThrottleLimit 2','-ThrottleLimit 1').replace('Start-Sleep -Seconds 8','Start-Sleep -Seconds 20'),encoding='utf-8')
p=W/'run-mlflow.py';p.write_text(p.read_text().replace("['MLFLOW_GENAI_EVAL_MAX_WORKERS']='2'","['MLFLOW_GENAI_EVAL_MAX_WORKERS']='1'"),encoding='utf-8')
print('Archived four HTTP 429 attempts. Subsequent chats and MLflow research scoring use one worker.')
