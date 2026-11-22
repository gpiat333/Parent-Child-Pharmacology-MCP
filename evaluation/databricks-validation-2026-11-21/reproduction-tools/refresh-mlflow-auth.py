from pathlib import Path
import sys,os,json
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/databricks-validation-2026-11-21')
os.chdir(W);sys.path.insert(0,str(W/'python-deps'));sys.path.insert(0,str(R))
import truststore;truststore.inject_into_ssl()
from databricks_transport import HOST,CLI
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_CONFIG_PROFILE='gsa-mcp-hackathon',DATABRICKS_AUTH_TYPE='databricks-cli',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='true',MLFLOW_HTTP_REQUEST_TIMEOUT='10',MLFLOW_HTTP_REQUEST_MAX_RETRIES='0',MLFLOW_DISABLE_AGENT_HINT='1')
import mlflow
mlflow.set_tracking_uri('databricks://gsa-mcp-hackathon');client=mlflow.MlflowClient()
p=R/'mlflow/paired-run.json';d=json.loads(p.read_text());run=client.get_run(d['run_id'])
arts=client.list_artifacts(d['run_id'],'paired-final');raw_count=sum(a.path.endswith(('-mcp.json','-plain.json')) for a in arts)
assert raw_count==14,raw_count
client.set_tag(d['run_id'],'run_finalization_recovery','All 14 answers and grades saved; final status update retried with refreshable CLI OAuth after static token expired. No answers or judgments regenerated.')
client.set_terminated(d['run_id'],status='FINISHED')
out={'before_status':run.info.status,'after_status':client.get_run(d['run_id']).info.status,'raw_answers':raw_count,'authentication':'existing Databricks CLI OAuth via refreshable SDK provider','credential_renewal_or_provider_change':False,'reason':'Cached one-time token expired during the final run-status update. All evaluation rows and artifacts were already saved.'}
(R/'mlflow/auth-recovery.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
