"""Retry execution errors only, never negative verdicts. Keep original runs intact."""
import json,os,subprocess
from pathlib import Path
B=Path(__file__).parent
import truststore
truststore.inject_into_ssl()
cli=r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe'
token=json.loads(subprocess.check_output([cli,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
os.environ['DATABRICKS_HOST']='https://dbc-aae0ba16-8727.cloud.databricks.com';os.environ['DATABRICKS_TOKEN']=token;os.environ['MLFLOW_GENAI_EVAL_MAX_WORKERS']='1';os.environ['MLFLOW_DISABLE_AGENT_HINT']='1'
try:
 import mlflow
 from mlflow.genai.scorers import Guidelines
 mlflow.set_tracking_uri('databricks');mlflow.set_experiment(experiment_id='1096079759942705')
 jobs=[]
 for suite in ['pubmed','trials','cross_source','safety']:
  rows=json.loads((B/f'{suite}-eval_results.json').read_text())
  inputs={r['inputs']['request']:r for r in json.loads((B/f'{suite}-answers.json').read_text())}
  for row in rows:
   request=row['request'];request=json.loads(request) if isinstance(request,str) else request
   for a in row['assessments']:
    error=a.get('error') or a.get('feedback',{}).get('error')
    if error and a.get('metadata',{}).get('guideline'):
     jobs.append({'suite':suite,'question':request['request'],'scorer':a['assessment_name'],'guideline':a['metadata']['guideline'],'original_error':error,'row':inputs[request['request']]})
 summaries=[]
 for index,job in enumerate(jobs):
  with mlflow.start_run(run_name='broad-source-v1-judge-error-retry') as run:
   mlflow.set_tags({'benchmark':'broad-source-v1','retry_type':'execution-error-only','original_suite':job['suite'],'clinical_certification':'false'})
   result=mlflow.genai.evaluate(data=[job['row']],scorers=[Guidelines(name=job['scorer'],guidelines=job['guideline'],model='databricks')])
   table=result.tables['eval_results'];table.to_json(B/f'judge-retry-{index}.json',orient='records',indent=2,default_handler=str)
   summaries.append({'run_id':run.info.run_id,'suite':job['suite'],'question':job['question'],'scorer':job['scorer'],'original_error':job['original_error'],'metrics':result.metrics})
 (B/'judge-retries.json').write_text(json.dumps(summaries,indent=2,default=str))
 print(json.dumps(summaries,default=str))
except Exception as exc:
 print('Judge retry failed: '+type(exc).__name__)
 raise SystemExit(1)
finally:os.environ.pop('DATABRICKS_TOKEN',None)
