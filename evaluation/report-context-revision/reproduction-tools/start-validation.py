from pathlib import Path
import json,sys,subprocess,time
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/report-context-revision'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
requested=json.loads((R/'deployment-request.json').read_text())['deployment_id']
for attempt in range(60):
 state=json.loads(subprocess.check_output([CLI,'apps','get','mcp-mc','--profile','gsa-mcp-hackathon','--output','json'],text=True,encoding='utf-8'))
 active=state.get('active_deployment',{})
 if active.get('deployment_id')==requested and active.get('status',{}).get('state')=='SUCCEEDED' and state.get('app_status',{}).get('state')=='RUNNING':break
 if active.get('deployment_id')==requested and active.get('status',{}).get('state')=='FAILED':raise RuntimeError('Deployment failed; inspect app status')
 print('Waiting for requested app version to be running.',flush=True);time.sleep(10)
else:raise RuntimeError('App readiness deadline exceeded')
subprocess.run([sys.executable,'-X','utf8',str(W/'probe-deployment.py')],check=True,cwd=W)
app=json.loads((R/'app-after.json').read_text(encoding='utf-8'))
source=app['active_deployment']['deployment_artifacts']['source_code_path']
assert source.endswith('/'+app['active_deployment']['deployment_id'])
with (W/'source-download.log').open('w',encoding='utf-8') as log:
 subprocess.run([CLI,'workspace','export-dir',source,str(W/'deployed-source'),'--profile','gsa-mcp-hackathon'],stdout=log,stderr=subprocess.STDOUT,check=True)
for name in ['verify-deployed-source.py','protocol-probes.py','pilot-paired.py','run-pilot.py']:
 print('Validation stage: '+name,flush=True)
 subprocess.run([sys.executable,'-X','utf8',str(W/name)],check=True,cwd=W)
print('Targeted .9 captures and grades ready for inspection; completed answers retained.',flush=True)
