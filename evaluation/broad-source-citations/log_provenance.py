"""Attach final provenance, implementation snapshots and review notes to all runs."""
import json,os,subprocess
from pathlib import Path
import truststore
truststore.inject_into_ssl()
B=Path(__file__).parent
cli=r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe'
token=json.loads(subprocess.check_output([cli,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
os.environ['DATABRICKS_HOST']='https://dbc-aae0ba16-8727.cloud.databricks.com'
os.environ['DATABRICKS_TOKEN']=token
try:
    from mlflow import MlflowClient
    client=MlflowClient(tracking_uri='databricks')
    for suite in ['pubmed','trials','cross_source','safety']:
        run=json.loads((B/f'{suite}-mlflow.json').read_text())['run_id']
        for name in ['manifest.json','implementation-hashes.json','test-mcp-chat.ps1','citation-output.ps1','parser-comparison.json','changes.txt','review-notes.json']:
            client.log_artifact(run,str(B/name))
        client.set_tag(run,'deployment_revision','01f1e2e1cd961d0db874f80dd0995ead')
        client.set_tag(run,'judge_rubrics','unchanged')
        print(suite+': provenance saved')
except Exception as exc:
    print('Provenance upload failed: '+type(exc).__name__)
    raise SystemExit(1)
finally:
    os.environ.pop('DATABRICKS_TOKEN',None)
