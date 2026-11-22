import json,os,subprocess
from pathlib import Path
B=Path(__file__).parent
import truststore;truststore.inject_into_ssl()
from databricks.sdk.config import Config
Config._resolve_host_metadata=lambda self:None
token=json.loads(subprocess.check_output([r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe','auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
os.environ.update(DATABRICKS_HOST='https://dbc-aae0ba16-8727.cloud.databricks.com',DATABRICKS_TOKEN=token,MLFLOW_DISABLE_AGENT_HINT='1')
try:
 import mlflow
 mlflow.set_tracking_uri('databricks')
 with mlflow.start_run(run_id=json.loads((B/'full-run.json').read_text())['run_id']):
  mlflow.set_tag('task_judge_score_use','diagnostic_only_do_not_use_as_acceptance_gate')
  mlflow.set_tag('evaluator_version','v2-fixed-refusal-contract-and-research-guidelines')
  for f in ['summary.json','report.html','calibration-gates.json','quality_gate.py','refusal_contract.py','review-notes.json']:
   mlflow.log_artifact(str(B/f))
 print('Report and calibration limits logged to completed MLflow run')
finally:os.environ.pop('DATABRICKS_TOKEN',None)

