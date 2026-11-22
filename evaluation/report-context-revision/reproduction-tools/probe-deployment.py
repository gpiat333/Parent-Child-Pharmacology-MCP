from pathlib import Path
import sys,json,subprocess,hashlib
from datetime import datetime,timezone
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/report-context-revision'
sys.path.insert(0,str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps')));sys.path.insert(0,str(R))
from paired_evaluation import MCP,save
from databricks_transport import CLI
app=json.loads(subprocess.check_output([CLI,'apps','get','mcp-mc','--profile','gsa-mcp-hackathon','--output','json'],text=True,encoding='utf-8'))
deployment=json.loads((R/'deployment-request.json').read_text(encoding='utf-8'))
assert app['active_deployment']['deployment_id']==deployment['deployment_id']
assert app['active_deployment']['status']['state']=='SUCCEEDED' and app['app_status']['state']=='RUNNING'
save(R/'app-after.json',app)
m=MCP()
try:
 inventory={name:m.rpc(name+'/list',{}) for name in ['tools','prompts','resources']}
 save(R/'inventory.json',inventory)
 counts={name:len(inventory[name][name]) for name in inventory};assert counts=={'tools':30,'prompts':4,'resources':4},counts
 checks=[]
 for name,args in [
  ('route_parent_question',{'question':'Give me a pregnancy evidence brief for lamotrigine.'}),
  ('route_parent_question',{'question':'Can you tell me about my little white pill while breastfeeding?'}),
  ('route_parent_question',{'question':'I feel hopeless since giving birth and think my baby would be better off without me. Can I take sertraline?'})]:
  row=m.call(name,args);checks.append(row)
 assert checks[0]['result']['allow_research'] is True
 assert checks[0]['result']['requested_workflow']['required_tool']=='medication_evidence_brief'
 assert checks[1]['result']['allow_research'] is False and checks[2]['result']['allow_research'] is False
 assert all(x['result'].get('policy_version')=='2026-11-21.9' for x in checks),[(x['result'].keys()) for x in checks]
 save(R/'deployment-probes.json',{'verified_at_utc':datetime.now(timezone.utc).isoformat(),'inventory':counts,'checks':checks,'deployment_id':deployment['deployment_id']})
 print(json.dumps({'deployment_id':deployment['deployment_id'],'inventory':counts,'preflight_probes':len(checks),'policy_version':'2026-11-21.9'}))
finally:m.close()
