from pathlib import Path
import hashlib,json
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(R/'evidence-manifest.json')
for name,digest in manifest.items():assert sha(R/name)==digest,('evidence',name)
checks={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (P/'SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines() if line}
for name,digest in checks.items():assert sha(P/name)==digest,('package',name)
for name,digest in read(R/'local-source-freeze.json')['files'].items():assert sha(P/name)==digest,('source',name)
for name,digest in read(R/'capture-lineage.json')['files'].items():assert sha(R/name)==digest,('capture',name)
state=read(R/'mlflow/parent-final-state.json');assert state['status']=='FINISHED' and state['final_rows_verified']==42 and not state['app_deployment'] and not state['github_push']
S=read(R/'summary.json');assert read(P/'evaluation/results.json')['current_revision']==S
assert read(R/'artifact-metric-consistency.json')['all_checks_passed']
v=read(R/'final-validation.json');assert v['deployment_id']==read(R/'app-final.json')['active_deployment']['deployment_id']
for name,digest in v['artifacts'].items():assert sha(P/name)==digest
artifact_keys={name.replace('\\','/'):digest for name,digest in v['artifacts'].items()}
assert artifact_keys['presentation/Parent-child Pharmacology MCP - Narrated demo.webm']=='858f6f90f749e116987264b0991c09539730b665aa34291e9a0ad385c277dd1a'
out={'all_checks_passed':True,'package_files':len(checks),'evidence_files':len(manifest),'source_files':len(read(R/'local-source-freeze.json')['files']),'mlflow_status':state['status'],'mlflow_rows_verified':42,'github_push':False,'deployed':False,'artifacts':v['artifacts']}
(W/'final-integrity-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
