"""Synthetic deployed acceptance checks. Never persist bearer credentials."""
import json,subprocess,time
from pathlib import Path
import importlib.util
if importlib.util.find_spec('truststore'):
 import truststore
 truststore.inject_into_ssl()
import httpx
B=Path(__file__).parent
CLI=r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe'
URL='https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp'
def main():
 token=json.loads(subprocess.check_output([CLI,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
 results=[];counter=0
 with httpx.Client(timeout=180,headers={'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream'}) as c:
  def rpc(method,params):
   nonlocal counter
   counter+=1;r=c.post(URL,json={'jsonrpc':'2.0','id':counter,'method':method,'params':params});r.raise_for_status();body=r.json()
   if body.get('error'):raise RuntimeError('MCP protocol error')
   return body.get('result',{})
  init=rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'parent-feature-tests','version':'1'}})
  c.headers['MCP-Protocol-Version']=init['protocolVersion']
  listed=rpc('tools/list',{})['tools'];results.append({'case':'tool_count','passed':len(listed)==27,'count':len(listed)})
  cases=[
   ('wrong_medicine_article','route_parent_question',{'question':'I took the wrong medicine'},lambda d:d['route']=='poison_help' and not d['allow_research']),
   ('blood_pressure_identity','route_parent_question',{'question':'What is my blood pressure medicine called?'},lambda d:d['route']=='confirm_identity' and not d['allow_research'])
  ]
  for name,tool,args,check in cases:
   start=time.monotonic()
   try:
    raw=rpc('tools/call',{'name':tool,'arguments':args})
    d=raw.get('structuredContent') or json.loads(next(x['text'] for x in raw['content'] if x['type']=='text'))
    passed=bool(check(d) and d.get('safety',{}).get('client_enforcement_required') and d.get('disclaimer'))
    results.append({'case':name,'passed':passed,'elapsed_ms':round((time.monotonic()-start)*1000),'result':d})
    print(name,passed,flush=True)
   except Exception as e:
    results.append({'case':name,'passed':False,'error_type':type(e).__name__});print(name,type(e).__name__,flush=True)
   (B/'wording-deployed-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print('Passed',sum(r['passed'] for r in results),'of',len(results))
 if not all(r['passed'] for r in results):raise SystemExit(1)
if __name__=='__main__':main()

