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
   ('pediatric_canada_screening','find_recruiting_studies',{'topic':'epilepsy','population':'pediatric','location':'Canada','max_results':5},lambda d:'excluded_population_counts' in d and all(r['pediatric_population']['status']=='pediatric_included' and not r['eligibility_confirmed'] for r in d['studies'])),
   ('pediatric_adhd_screening','find_recruiting_studies',{'topic':'ADHD','population':'pediatric','location':'United States','max_results':5},lambda d:len(d['studies'])>0 and all(r['pediatric_population']['status']=='pediatric_included' for r in d['studies'])),
   ('separate_comment_date_status','search_parent_input_opportunities',{'topic':'pregnancy research','agency':'FDA','max_results':20},lambda d:len(d['notices'])>0 and all('comment_deadline' in r and r['submission_status']=='not_verified' and not r['meeting_dates_used_for_deadline'] and (r['comment_deadline']['relation_to_as_of']=='unknown')==(not r['comment_deadline']['date_known']) for r in d['notices'])),
   ('urgent','route_parent_question',{'question':'My baby is not breathing','country':'US'},lambda d:d['route']=='urgent_help' and not d['allow_research'] and '911' in d['message']),
   ('poison','route_parent_question',{'question':'My toddler drank medicine'},lambda d:d['route']=='poison_help' and '1-800-222-1222' in d['message']),
   ('no_guess_local_number','route_parent_question',{'question':'My baby is not breathing','country':'unknown'},lambda d:'911' not in d['message']),
   ('personal_change','route_parent_question',{'question':'Should I stop my medicine now that I am pregnant?'},lambda d:d['route']=='clinician_or_pharmacist' and not d['allow_research']),
   ('vague_identity','route_parent_question',{'question':'What is my little white pill?'},lambda d:d['route']=='confirm_identity'),
   ('privacy_route','route_parent_question',{'question':'My name is Synthetic Person'},lambda d:d['route']=='privacy'),
   ('privacy_external_block','search_literature',{'query':'parent@example.com'},lambda d:d.get('error')=='identifying_input'),
   ('recalls_wrong_lot','search_medication_recalls',{'drug':'ibuprofen','lot':'EXAMPLE-LOT-NOT-A-REAL-LOT','max_results':2},lambda d:len(d['results'])>0 and all(not r['affected_product_confirmed'] for r in d['results'])),
   ('recalls_parent_wording','search_medication_recalls',{'drug':"children's ibuprofen",'lot':'EXAMPLE-LOT','max_results':2},lambda d:len(d['results'])>0 and all(not r['affected_product_confirmed'] for r in d['results'])),
   ('alerts','search_drug_safety_alerts',{'drug':'cetirizine'},lambda d:len(d['results'])>0 and all(r['url'].startswith('https://www.fda.gov/') for r in d['results'])),
   ('recruiting','find_recruiting_studies',{'topic':'asthma','population':'pediatric','location':'United States','max_results':2},lambda d:len(d['studies'])>0 and all(r['status']=='RECRUITING' and not r['eligibility_confirmed'] for r in d['studies'])),
   ('trial_compatibility','search_trials',{'condition_or_drug':'NCT00006286','population':'any','max_results':1},lambda d:len(d['studies'])>0 and 'central_contacts' in d['studies'][0]),
   ('registries','search_pregnancy_registries',{'drug':'sertraline'},lambda d:len(d['results'])>0 and d['results'][0]['status_as_listed']),
   ('public_input','search_parent_input_opportunities',{'topic':'clinical research','agency':'NIH','max_results':3},lambda d:len(d['notices'])>0 and all('closed meeting' not in r['title'].lower() for r in d['notices']) and len(d['directories'])==2),
   ('reporting_links','get_reporting_resources',{},lambda d:not d['submission_performed'] and len(d['resources'])==4),
   ('parent_evidence','get_parent_medication_info',{'drug':'sertraline'},lambda d:d['identity']['found'] and 'monitoring' in d['interpretation'] and d['medicine_taker_label_evidence'].get('sections')),
   ('parent_identity_gate','get_parent_medication_info',{'drug':'little white pill'},lambda d:d['requires_confirmation']),
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
   (B/'deployed-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 print('Passed',sum(r['passed'] for r in results),'of',len(results))
 if not all(r['passed'] for r in results):raise SystemExit(1)
if __name__=='__main__':main()
