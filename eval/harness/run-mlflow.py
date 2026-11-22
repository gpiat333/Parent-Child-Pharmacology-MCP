from pathlib import Path
from datetime import datetime,timezone
import sys,os,json,argparse,hashlib,time
W=Path(__file__).parent;R=W;P=Path(os.environ['MCP_REPO_ROOT'])
os.environ['MLFLOW_DISABLE_AGENT_HINT']='1';os.environ['MLFLOW_GENAI_EVAL_MAX_WORKERS']='1';os.environ['MLFLOW_HTTP_REQUEST_TIMEOUT']='60'
import truststore;truststore.inject_into_ssl()
from databricks_transport import HOST,CLI,oauth_token
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ['MCP_GATEWAY_PROFILE']=os.environ.get('DATABRICKS_CONFIG_PROFILE','gsa-mcp-hackathon')
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_TOKEN=oauth_token(),DATABRICKS_AUTH_TYPE='pat',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='false')
os.environ.pop('DATABRICKS_CONFIG_PROFILE',None)  # Cached bearer stays in this process only.
import mlflow
from mlflow.genai.scorers import list_scorers,get_scorer
from mlflow.entities.trace_location import MlflowExperimentLocation
from paired_evaluation import read,save,CASE_IDS
from score_current import unpack,compact
from mlflow_suite import execution_contracts,diagnostic_contracts
EXPERIMENT=os.environ['MLFLOW_EXPERIMENT_ID']
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['pilot','research','stops','paired'],required=True);parser.add_argument('--attempt',default='');args=parser.parse_args()
if args.phase=='stops':os.environ['MLFLOW_GENAI_EVAL_MAX_WORKERS']='4'  # No model calls in fixed-stop checks.
label=args.phase+('-'+args.attempt if args.attempt else '')
mlflow.set_tracking_uri('databricks');mlflow.set_experiment(experiment_id=EXPERIMENT)
mlflow.tracing.set_destination(MlflowExperimentLocation(experiment_id=EXPERIMENT))
client=mlflow.MlflowClient();out=R/'mlflow';out.mkdir(exist_ok=True)
deployment='unchanged; see Databricks app receipt'
parent_path=out/'parent-run.json'
if parent_path.exists():parent=read(parent_path)
else:
 run=client.create_run(EXPERIMENT,tags={'mlflow.runName':'mcp-mc-local-task-reliability-2026-11-22','deployment_id':deployment,'evaluation_driver':'local .15 MCP and evaluation driver; model and MLflow in Databricks; deployed .9 app unchanged','policy_version':'2026-11-22.15','grader_version':'3.1','clinical_validation':'false','github_push':'authorized-private-only'})
 parent={'run_id':run.info.run_id,'experiment_id':EXPERIMENT,'url':HOST+'/ml/experiments/'+EXPERIMENT+'/runs/'+run.info.run_id,'started_at_utc':datetime.now(timezone.utc).isoformat()};save(parent_path,parent)
registered={s.name:s for s in list_scorers(experiment_id=EXPERIMENT)}
for scorer in [execution_contracts,diagnostic_contracts]:
 if scorer.name not in registered:scorer.register(experiment_id=EXPERIMENT)
registered={s.name:s for s in list_scorers(experiment_id=EXPERIMENT)}
assert all(s.name in registered for s in [execution_contracts,diagnostic_contracts])
suite=[get_scorer(name=s.name,experiment_id=EXPERIMENT) for s in ([execution_contracts] if args.phase=='stops' else [diagnostic_contracts] if args.phase=='paired' else [execution_contracts,diagnostic_contracts])]
save(out/'registered-scorers.json',[{'name':s.name,'class':type(s).__name__} for s in registered.values()])
cases=read(R/'cases.json');data=[]
if args.phase=='paired':
 for case in cases:
  if case['id'] not in CASE_IDS:continue
  answers={arm:read(R/'paired-final'/(case['id']+'-'+arm+'.json')) for arm in ['mcp','plain']}
  references=read(R/'paired-final'/(case['id']+'-reference.json'))+answers['mcp'].get('calls',[])
  for arm,d in answers.items():
   assert d['completed'],(case['id'],arm)
   data.append({'inputs':{'case_id':case['id'],'arm':arm,'question':case['question']},'outputs':{'answer':d['answer'],'completed':d['completed'],'capture_artifact':'paired-final/'+case['id']+'-'+arm+'.json'},'expectations':{'criteria':case['criteria'],'reference_artifact':'paired-final/'+case['id']+'-reference.json','shared_pool_includes_mcp_calls':True}})
else:
 selected=[c for c in cases if (c['id'] in ['E01-gap','S6-pregnancy'] if args.phase=='pilot' else c['blocked'] if args.phase=='stops' else not c['blocked'])]
 for case in selected:
  d=read(R/'chats'/(case['id']+'-results.json'));assert d['completed'],case['id']
  evidence=[{'tool':x['tool'],'arguments':x['arguments'],'result':compact(unpack(x['result']))} for x in d.get('tool_calls',[])]
  data.append({'inputs':{'case_id':case['id'],'arm':'chat','question':case['question']},'outputs':{'answer':d['answer'],'completed':d['completed'],'capture_artifact':'chats/'+case['id']+'-results.json'},'expectations':{'case':case,'criteria':case.get('criteria','Fixed stop contract'),'reference_artifact':'chats/'+case['id']+'-results.json'}})
summary_path=out/(label+'-run.json')
assert not summary_path.exists(),'Completed MLflow run already recorded; inspect rather than overwrite'
with mlflow.start_run(run_name='fresh-local-'+label+'-v3.1-2026-11-22',tags={'mlflow.parentRunId':parent['run_id'],'deployment_id':deployment,'phase':args.phase,'input_mode':'fresh local .15 captures; offline evaluation of saved answers','grader':'v3.1-grounded-attribution','clinical_validation':'false','evidence_storage':'Full evidence in artifacts; compact references in expectations.'}) as run:
 started=time.time();save(out/(label+'-started.json'),{'run_id':run.info.run_id,'rows':len(data),'started_at_utc':datetime.now(timezone.utc).isoformat()})
 mlflow.log_params({'cases':len(data),'model':'system.ai.gpt-5-6-luna','deployment_id':deployment,'driver':'local','mcp_runtime':'Local loopback submission .15; not deployed','model_runtime':'Databricks AI Gateway'})
 result=mlflow.genai.evaluate(data=data,scorers=suite)
 for name,table in result.tables.items():
  table.to_json(out/(label+'-'+name+'.json'),orient='records',indent=2,default_handler=str)
 persisted=client.get_run(run.info.run_id)
 summary={'run_id':run.info.run_id,'experiment_id':EXPERIMENT,'url':HOST+'/ml/experiments/'+EXPERIMENT+'/runs/'+run.info.run_id,'rows':len(data),'phase':args.phase,'metrics':result.metrics,'table_names':list(result.tables),'elapsed_seconds':round(time.time()-started,2),'persisted_metrics':persisted.data.metrics,'deployment_id':deployment,'pilot_rows_reused_in_full_run':False,'answer_generation_repeated':True}
 save(summary_path,summary)
 for row in data:
  raw=R/row['outputs']['capture_artifact'];mlflow.log_artifact(str(raw),str(raw.relative_to(R).parent).replace('\\','/'))
  if args.phase=='paired':
   cid=row['inputs']['case_id'];mlflow.log_artifact(str(R/'paired-final'/(cid+'-reference.json')),'paired-final')
   mlflow.log_artifact(str(R/'paired-final'/(cid+'-mcp.json')),'paired-final')
  grade=R/'chat-judgments'/(row['inputs']['case_id']+'.json') if row['inputs']['arm']=='chat' else R/'paired-final'/(row['inputs']['case_id']+'-'+row['inputs']['arm']+'-judge.json')
  if grade.exists():mlflow.log_artifact(str(grade),'judgments')
 for path in [R/'cases.json',R/'run-design.json',R/'deployed_grader.py',R/'mlflow_suite.py',R/'grader_contract.py',R/'grader_runtime.py',summary_path]:mlflow.log_artifact(str(path),'method')
 print(json.dumps(summary,indent=2,default=str),flush=True)
os.environ.pop('DATABRICKS_TOKEN',None)
