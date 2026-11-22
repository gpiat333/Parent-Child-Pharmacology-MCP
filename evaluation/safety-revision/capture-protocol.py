import httpx,json,time
from pathlib import Path
root=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
out=root/'evaluation/safety-revision'; c=httpx.Client(timeout=180)
headers={'Accept':'application/json, text/event-stream'}
def rpc(method,params):
 r=c.post('http://127.0.0.1:18080/mcp',headers=headers,json={'jsonrpc':'2.0','id':1,'method':method,'params':params});r.raise_for_status();v=r.json()
 if 'error' in v:raise RuntimeError(v['error']['code'])
 return v['result']
init=rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'safety-revision-local-check','version':'1'}})
headers['MCP-Protocol-Version']=init['protocolVersion']
inv={k:rpc(k+'/list',{}) for k in ['tools','prompts','resources']}
(out/'inventory.json').write_text(json.dumps(inv,indent=2),encoding='utf-8')
cases=[('empty','search_lactmed',{'drug':'SYNTHETIC-ZZNOEVIDENCE-QZX'}),('spanish-education','get_patient_education',{'topic':'What information is available in Spanish for sertraline?','rxcui':'36437','language':'es'}),('combination-identity','normalize_drug',{'name':'Augmentin'}),('brief','medication_evidence_brief',{'drug':'sertraline','population':'lactation'}),('mprint-metadata','find_mprint_records',{'pmid':'38841362'}),('mprint-details','get_mprint_details',{'pmid':'38841362','table':'silver_classifications'}),('inactive-vector','semantic_search_lactmed',{'question':'What lactation evidence exists for sertraline?'})]
for cid,name,args in cases:
 start=time.perf_counter();result=rpc('tools/call',{'name':name,'arguments':args})
 payload=result.get('structuredContent') or json.loads(result['content'][0]['text'])
 doc={'id':cid,'tool':name,'arguments':args,'endpoint':'http://127.0.0.1:18080/mcp','kind':'new local protocol call; live sources where enabled','elapsed_ms':round((time.perf_counter()-start)*1000),'payload':payload}
 (out/(cid+'.json')).write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding='utf-8')
 print(cid,payload.get('status'),payload.get('evidence_status',{}).get('state'),flush=True)
c.close()
