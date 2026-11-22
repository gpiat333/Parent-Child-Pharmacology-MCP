import json,statistics,html
from pathlib import Path
B=Path(__file__).parent
cases=json.loads((B/'cases.json').read_text());byq={c['question']:c['id'] for c in cases}
summary={};failures=[]
for profile in ['full','parent']:
 checks=json.loads((B/f'{profile}-checks.json').read_text())
 summary[profile]={k:sum(bool(x[k]) for x in checks) for k in ['completed','tool_selection','boundary_behavior','citation_provenance']}
 summary[profile].update(rows=len(checks),tool_calls=sum(x['tool_count'] for x in checks),total_tokens=sum(x['total_tokens'] for x in checks),median_elapsed_ms=statistics.median(x['elapsed_ms'] for x in checks if x['elapsed_ms'] is not None),out_of_scope_calls=sum(len(x['out_of_scope_calls']) for x in checks))
 fp=B/f'{profile}-eval_results.json'
 if fp.exists():
  records=json.loads(fp.read_text())
  for name in ['evidence_fidelity','task_fulfillment']:
   values=[r.get(name+'/value') for r in records]
   summary[profile][name]={'passed':sum(v in [True,'yes'] for v in values),'failed':sum(v in [False,'no'] for v in values),'errors_or_missing':sum(v not in [True,False,'yes','no'] for v in values)}
   for r in records:
    if r.get(name+'/value') not in [True,'yes']:
     q=r.get('request',{}).get('question','')
     failures.append({'profile':profile,'id':byq.get(q,q),'check':name,'value':r.get(name+'/value'),'rationale':r.get(name+'/rationale'),'error':r.get(name+'/error')})
 run=B/f'{profile}-run.json'
 if run.exists():summary[profile]['run']=json.loads(run.read_text())
(B/'summary.json').write_text(json.dumps(summary,indent=2));(B/'judge-flags.json').write_text(json.dumps(failures,indent=2))
print(json.dumps({'summary':summary,'flags':failures},indent=2))
