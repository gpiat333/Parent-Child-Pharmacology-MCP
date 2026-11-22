"""Check actual MCP schemas and boundary handling; never save credentials."""
import json
import subprocess
from pathlib import Path
import httpx
import truststore
truststore.inject_into_ssl()
CLI=r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe'
URL='https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp'
token=json.loads(subprocess.check_output([CLI,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
results=[]
with httpx.Client(timeout=120,headers={'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream'}) as c:
    def rpc(method,params):
        r=c.post(URL,json={'jsonrpc':'2.0','id':len(results)+1,'method':method,'params':params})
        r.raise_for_status()
        return r.json()
    init=rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'contract-regression','version':'1'}})
    c.headers['MCP-Protocol-Version']=init['result']['protocolVersion']
    tools=rpc('tools/list',{})['result']['tools']
    for t in tools:
        results.append({'case':'schema:'+t['name'],'passed':t['inputSchema'].get('additionalProperties') is False and set(t.get('outputSchema',{}).get('required',[])) >= {'safety','disclaimer'}})
    for label,name,args in [
        ('blank','search_lactmed',{'drug':'  '}),
        ('negative_limit','search_lactmed',{'drug':'sertraline','max_results':-1}),
        ('oversized_limit','search_lactmed',{'drug':'sertraline','max_results':21}),
        ('numeric_string','search_lactmed',{'drug':'sertraline','max_results':'5'}),
        ('extra_field','get_reporting_resources',{'unexpected':True}),
        ('bad_enum','search_trials',{'condition_or_drug':'sertraline','population':'adult'}),
        ('bad_id','get_lactmed_record',{'book_id':'sertraline'}),
        ('empty_list','get_abstracts',{'pmids':[]}),
    ]:
        raw=rpc('tools/call',{'name':name,'arguments':args})
        results.append({'case':label,'passed':bool(raw.get('error') or raw.get('result',{}).get('isError'))})
    raw=rpc('tools/call',{'name':'get_reporting_resources','arguments':{}})['result']
    data=raw.get('structuredContent',{})
    results.append({'case':'typed_output_preserves_resources','passed':bool(not raw.get('isError') and len(data.get('resources',[]))==4 and data.get('safety',{}).get('client_enforcement_required') is True and data.get('disclaimer'))})
Path(__file__).with_name('deployed-contract-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(f"Passed {sum(x['passed'] for x in results)}/{len(results)} deployed contract checks")
if not all(x['passed'] for x in results): raise SystemExit(1)
