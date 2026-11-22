"""Local protocol pre-test for a transparent thin-pregnancy-evidence demonstration."""
import json,time,httpx
from pathlib import Path
P=Path(__file__).resolve().parents[2];OUT=P/'evaluation/evidence-revision'
OUT.mkdir(exist_ok=True)
c=httpx.Client(timeout=240,trust_env=False,headers={'Accept':'application/json, text/event-stream'})
def rpc(method,params):
 r=c.post('http://127.0.0.1:18080/mcp',json={'jsonrpc':'2.0','id':1,'method':method,'params':params});r.raise_for_status();d=r.json()
 if d.get('error'):raise RuntimeError('MCP protocol error')
 return d['result']
def save(name,d): (OUT/name).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
init=rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'evidence-pretest','version':'1'}})
c.headers['MCP-Protocol-Version']=init['protocolVersion']
save('inventory.json',{k:rpc(k+'/list',{}) for k in ['tools','prompts','resources']})
for drug in ['daridorexant','lamotrigine']:
 start=time.perf_counter();raw=rpc('tools/call',{'name':'medication_evidence_brief','arguments':{'drug':drug,'population':'pregnancy'}})
 payload=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
 save('pretest-'+drug+'.json',{'drug':drug,'payload':payload,'elapsed_ms':round((time.perf_counter()-start)*1000)})
 rows=payload.get('ingredient_evidence',[])
 print(json.dumps({'drug':drug,'status':payload.get('status'),'ingredients':payload.get('queried_ingredients'),'rows':[{
  'label':r['label'].get('title'),'pllr':r['label'].get('pllr_8_1',{}).get('parse_status'),
  'subsections':{k:v['found'] for k,v in r['label'].get('pllr_8_1',{}).get('subsections',{}).items()},
  'articles':len(r['literature'].get('articles',[])),'search_metadata':[s.get('search_metadata') for s in r['literature'].get('searches',[])],
  'axes':[(a['axis'],len(a['items']),len(a['context_only']),len(a['reported_gaps'])) for a in r['evidence_axes']],
  'pk_empty':r['maternal_pharmacokinetics']['no_data_found'],
  'registries':len(r['participation']['registries'].get('results',[]))} for r in rows]}),flush=True)
c.close()
