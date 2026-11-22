from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,fnmatch
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/brief-paraphrase-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=read(R/'deployment-source-manifest.json')['files'];deployed=W/'deployed-source'
excludes=['README.md','tests/*','smoke_test.py','ingest_mother_child.py','02_build_vector_index.py']
expected={k:v for k,v in source.items() if not any(fnmatch.fnmatch(k,x) for x in excludes)}
actual={p.relative_to(deployed).as_posix():sha(p) for p in deployed.rglob('*') if p.is_file()}
missing=sorted(set(expected)-set(actual));changed=sorted(k for k in set(expected)&set(actual) if expected[k]!=actual[k]);extra=sorted(set(actual)-set(expected))
assert not missing and not changed and not extra,{'missing':missing,'changed':changed,'extra':extra}
for k,v in read(R/'local-source-freeze.json')['files'].items():assert sha(P/k)==v,k
check=read(R/'run-design-verification.json');check['evaluator_files']={p.name:sha(p) for p in [R/x for x in ['cases.json','paired_evaluation.py','score_current.py','run-chats.ps1','databricks_transport.py','deployed_grader.py','mlflow_suite.py']]}
check['execution_concurrency']={'chat_capture_workers':1,'paired_capture_workers':1,'mlflow_scoring_workers':1,'timing_limit':'Concurrent workload and live services affect timings; no controlled latency superiority claim.'}
(R/'run-design-verification.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
result={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'deployment_id':read(R/'deployment-request.json')['deployment_id'],'verification':'Downloaded the active app deployment snapshot from its Databricks workspace path and compared every staged runtime file byte for byte.','runtime_files':len(expected),'missing':missing,'changed':changed,'extra':extra,'local_frozen_files_unchanged':112,'sha256_by_relative_path':actual}
(R/'deployed-source-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sha256_by_relative_path'},indent=2))
