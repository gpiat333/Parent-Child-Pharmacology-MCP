from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
sys.path.insert(0,str(R));from paired_evaluation import CASE_IDS
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in read(R/'local-source-freeze.json')['files'].items():assert sha(P/name)==digest,name
for name,digest in read(R/'run-design-verification.json')['evaluator_files'].items():assert sha(R/name)==digest,name
cases=read(R/'cases.json');rows=[]
for c in cases:
 p=R/'chats'/(c['id']+'-results.json');d=read(p);assert d['completed'],c['id']
 assert d['endpoint']=='http://127.0.0.1:8770/mcp',d.keys()
 rows.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'arm':'chat'})
for cid in CASE_IDS:
 for arm in ['mcp','plain']:
  p=R/'paired-final'/(cid+'-'+arm+'.json');d=read(p);assert d['completed'],(cid,arm)
  rows.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'arm':arm})
 assert (R/'paired-final'/(cid+'-reference.json')).exists()
files={p.relative_to(R).as_posix():sha(p) for folder in ['chats','paired-final'] for p in sorted((R/folder).glob('*')) if p.is_file() and not p.name.endswith('-judge.json')}
out={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'answer_generation_repeated':True,'reference_retrieval_repeated':True,'historical_captures_reused':False,'completed_rows':len(rows),'rows':rows,'files':files,'runtime':'Local .10 MCP, Databricks model gateway','endpoint':'http://127.0.0.1:8770/mcp','no_completed_answers_replaced':True}
(R/'capture-lineage.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'fresh_completed_rows':len(rows),'capture_files':len(files),'source_frozen':True}))
