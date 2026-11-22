from pathlib import Path
import json,hashlib,os,sys
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((R/'mlflow/parent-final-state.json').read_text(encoding='utf-8-sig'));assert state['status']=='FINISHED'
manifest_path=R/'evidence-manifest.json'
manifest={f.relative_to(R).as_posix():sha(f) for f in sorted(R.rglob('*')) if f.is_file() and not {'.pytest_cache','__pycache__'}.intersection(f.parts) and f.name!='evidence-manifest.json'}
manifest_path.write_text(json.dumps(dict(sorted(manifest.items())),indent=2),encoding='utf-8')
checksums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (P/'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines() if line}
for name,digest in manifest.items():checksums[(R/ name).relative_to(P).as_posix()]=digest
checksums[manifest_path.relative_to(P).as_posix()]=sha(manifest_path)
(P/'SHA256SUMS.txt').write_text(''.join(digest+'  '+name+'\n' for name,digest in sorted(checksums.items())),encoding='utf-8')
os.chdir(W);sys.path.insert(0,str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps')));sys.path.insert(0,str(R))
import truststore;truststore.inject_into_ssl()
from databricks_transport import HOST,CLI
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_CONFIG_PROFILE='gsa-mcp-hackathon',DATABRICKS_AUTH_TYPE='databricks-cli',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='true',MLFLOW_HTTP_REQUEST_TIMEOUT='30',MLFLOW_HTTP_REQUEST_MAX_RETRIES='1',MLFLOW_DISABLE_AGENT_HINT='1')
import mlflow
mlflow.set_tracking_uri('databricks://gsa-mcp-hackathon');c=mlflow.MlflowClient()
for p in [manifest_path,P/'SHA256SUMS.txt',R/'mlflow/parent-final-state.json']:c.log_artifact(state['run_id'],str(p),'integrity')
assert c.get_run(state['run_id']).info.status=='FINISHED'
print(json.dumps({'parent_status':'FINISHED','package_files_with_checksums':len(checksums),'evidence_files_with_checksums':len(manifest),'integrity_artifacts_uploaded':3,'github_push':False},indent=2))
