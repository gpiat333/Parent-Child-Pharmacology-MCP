from pathlib import Path
import json,subprocess,hashlib
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-paraphrase-revision'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
def run(args,name,parse=True):
 result=subprocess.run([CLI,*args,'--profile','gsa-mcp-hackathon','--output','json'],cwd=W/'server',capture_output=True,text=True,encoding='utf-8')
 (R/(name+'.stderr.txt')).write_text(result.stderr,encoding='utf-8')
 (R/(name+('.json' if parse else '.txt'))).write_text(result.stdout,encoding='utf-8')
 if result.returncode:raise RuntimeError(name+' failed; inspect saved CLI log')
 return json.loads(result.stdout) if parse else result.stdout
manifest=json.loads((R/'deployment-source-manifest.json').read_text(encoding='utf-8'))
for name,digest in manifest['files'].items():assert hashlib.sha256((W/'server'/name).read_bytes()).hexdigest()==digest,name
validated=run(['bundle','validate'],'bundle-validation')
assert list(validated['resources'])==['apps'] and list(validated['resources']['apps'])==['mcp_mc']
plan=run(['bundle','plan'],'bundle-plan')
assert all(v['action']=='skip' for v in plan['plan'].values()),'Unexpected resource change; inspect before deployment'
print('Plan verified: existing mcp-mc app; zero infrastructure resource changes.',flush=True)
run(['bundle','deploy','--auto-approve'],'bundle-deployment',False)
print('Frozen source uploaded to existing bundle path.',flush=True)
source=validated['resources']['apps']['mcp_mc']['source_code_path']
deployment=run(['apps','deploy','mcp-mc','--source-code-path',source,'--mode','SNAPSHOT','--no-wait'],'deployment-request')
print(json.dumps({'deployment_id':deployment['deployment_id'],'status':deployment.get('status'),'source_code_path':source}),flush=True)
