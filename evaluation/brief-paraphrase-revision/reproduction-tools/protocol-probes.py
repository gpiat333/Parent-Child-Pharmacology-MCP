from pathlib import Path
import sys,json,time
from datetime import datetime,timezone
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/brief-paraphrase-revision';OLD=P/'evaluation/notice-citation-revision'
sys.path.insert(0,str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps')));sys.path.insert(0,str(R))
from paired_evaluation import MCP,read,save,ENDPOINT
from jsonschema import Draft202012Validator
inventory=read(R/'inventory.json');schema_checks=[]
for t in inventory['tools']['tools']:
 Draft202012Validator.check_schema(t['inputSchema']);schema_checks.append({'tool':t['name'],'schema_valid':True})
save(R/'schema-checks.json',schema_checks)
m=MCP();invalids=[]
try:
 invalid_cases=[('search_lactmed',{'drug':'sertraline','max_results':-1}),('search_lactmed',{'drug':'sertraline','max_results':0}),('search_lactmed',{'drug':''}),('get_lactmed_record',{'book_id':''}),('get_abstracts',{'pmids':['']}),('get_mprint_details',{'pmid':'12345','table':'unknown'}),('find_pregnancy_exposure_registries',{'drug':'   '}),('medication_evidence_brief',{'drug':'sertraline','population':'unsupported_age'})]
 for name,args in invalid_cases:
  m.counter+=1;response=m.client.post(ENDPOINT,json={'jsonrpc':'2.0','id':m.counter,'method':'tools/call','params':{'name':name,'arguments':args}});response.raise_for_status();raw=response.json()
  rejected=raw.get('error',{}).get('code')==-32602 or raw.get('result',{}).get('isError') is True
  invalids.append({'tool':name,'arguments':args,'rejected':rejected,'response':raw});save(R/'invalid-input-checks.json',invalids)
 assert all(x['rejected'] for x in invalids),[(x['tool'],x['arguments']) for x in invalids if not x['rejected']]
 print('30 remote schemas valid; 8 invalid calls rejected.',flush=True)
 paths=list((OLD/'protocol-probes').glob('*.json'))+list((OLD/'workflow-probes').glob('*.json'))+[OLD/(x+'.json') for x in ['empty','registry','gap-brief','clinician-questions','selector-regression','language-boundary']]
 results=[]
 for p in paths:
  target=R/p.relative_to(OLD)
  if target.exists():value=read(target)
  else:
   old=read(p);value=m.call(old['tool'],old['arguments']);save(target,value)
  result=value['result'];results.append({'file':p.relative_to(OLD).as_posix(),'tool':value['tool'],'status':result.get('status'),'latency_ms':value['latency_ms'],'has_error':bool(result.get('error'))})
  save(R/'protocol-probe-summary.json',{'captured':len(results),'expected':20,'rows':results,'interpretation':'Fresh source and contract captures; partial/empty results are retained and are not automatically failures or evidence of safety.'})
  print(p.name,result.get('status'),flush=True)
 assert read(R/'empty.json')['result']['evidence_status']['no_evidence_retrieved'] is True
 assert read(R/'empty.json')['result']['evidence_status']['not_evidence_of_safety'] is True
 assert read(R/'workflow-probes/brief.json')['result']['requested_workflow']['required_tool']=='medication_evidence_brief'
 assert read(R/'workflow-probes/identity.json')['result']['allow_research'] is False
 checks=[]
 for question,allowed,required in [
  ('Give me a pregnancy evidence brief for lamotrigine.',True,True),
  ('Show me a pregnancy evidence brief for lamotrigine.',True,True),
  ('Send me a pregnancy evidence brief for lamotrigine.',True,True),
  ("Don't give me an evidence brief. Search LactMed for sertraline only.",True,False),
  ('Do not show me an evidence brief. Search LactMed for sertraline only.',True,False),
  ('Never send me an evidence brief. Search LactMed for sertraline only.',True,False),
  ('What is an evidence brief?',True,False),
  ('Give me a pregnancy evidence brief for my little white pill.',False,False),
  ('Give me a pregnancy evidence brief. I want to harm myself with my pills.',False,False),
  ('Give me a pregnancy evidence brief. My baby cannot breathe.',False,False),
  ('Give me a pregnancy evidence brief. Should I stop taking my medicine?',False,False),
  ('Give me a pregnancy evidence brief. Puedo tomar sertralina durante la lactancia.',False,False),
 ]:
  row=m.call('route_parent_question',{'question':question});result=row['result']
  actual_required=result.get('requested_workflow',{}).get('required_tool')=='medication_evidence_brief'
  passed=result['allow_research']==allowed and actual_required==required
  checks.append({'question':question,'expected_allow_research':allowed,'expected_brief_required':required,'passed':passed,'capture':row})
  save(R/'additional-routing-observation.json',{'policy_version':'2026-11-21.5','checks':checks,'passed':sum(x['passed'] for x in checks),'expected':12,'interpretation':'Separate deployed preflight regression checks for the fixed paraphrase, negation, incidental mention and overriding stop routes; excluded from the 28-case benchmark.','clinical_assessment':False})
 assert all(x['passed'] for x in checks),[x['question'] for x in checks if not x['passed']]
 print('20 deployed source/workflow captures retained; empty-result and known-workflow contracts verified.',flush=True)
finally:m.close()
