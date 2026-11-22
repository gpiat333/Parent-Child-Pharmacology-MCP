from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil

W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/report-context-revision'
R=P/'evaluation/grader-attribution-revision'
assert not R.exists(), 'New grading revision already exists; inspect rather than overwrite.'
R.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['cases.json','model-call.ps1','databricks_transport.py','local-source-freeze.json']:
    shutil.copy2(OLD/name,R/name)
for name in ['chats','source-snapshot']:
    shutil.copytree(OLD/name,R/name)
(R/'paired-final').mkdir()
for path in (OLD/'paired-final').glob('*.json'):
    if path.name.endswith(('-mcp.json','-plain.json','-reference.json')):
        shutil.copy2(path,R/'paired-final'/path.name)
(R/'origin').mkdir()
for name in ['summary.json','run-design.json','run-design-verification.json','deployed-source-verification.json','grader-attribution-audit.json','local-unit-tests.xml']:
    shutil.copy2(OLD/name,R/'origin'/name)
shutil.copy2(OLD/'paired-final/design.json',R/'origin/paired-design.json')
captures=[p for folder in ['chats','paired-final'] for p in (R/folder).rglob('*') if p.is_file()]
for p in captures:
    assert sha(p)==sha(OLD/p.relative_to(R)),p
origin={'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'source_revision':'report-context-revision','source_policy':'2026-11-21.9',
        'source_mlflow_parent':read(OLD/'summary.json')['mlflow']['parent'],
        'answer_generation_repeated':False,'reference_retrieval_repeated':False,
        'unchanged_case_file_sha256':sha(R/'cases.json'),
        'files':{p.relative_to(R).as_posix():sha(p) for p in sorted(captures)},
        'reason':'Regrade unchanged answers and evidence to isolate the grading correction. Historical v2 grades remain untouched.'}
(R/'capture-lineage.json').write_text(json.dumps(origin,indent=2),encoding='utf-8')
for name in ['server','chat-client']:
    for relative,digest in read(R/'local-source-freeze.json')['files'].items():
        if relative.startswith(name+'/'):assert sha(P/relative)==digest,relative
bridge=(OLD/'paired_evaluation.py').read_text(encoding='utf-8').split('class MCP:')[0]
a=bridge.index("JUDGE_PROMPT = '''");b=bridge.index('\ndef save',a)
bridge=bridge[:a]+'from grader_contract import JUDGE_PROMPT\n'+bridge[b:]
bridge=bridge.replace("'max_tokens': 3000", "'max_tokens': 6000")
bridge+='\nif __name__ == "__main__":\n    raise SystemExit("This revision regrades retained captures; answer generation is disabled.")\n'
(R/'paired_evaluation.py').write_text(bridge,encoding='utf-8')
score=(OLD/'score_current.py').read_text(encoding='utf-8')
a=score.index('def judge(payload):');b=score.index('\ndef calibrate():',a)
score=score[:a]+"def judge(payload):\n from grader_runtime import judge as grounded_judge\n return grounded_judge(payload,model_call,MODEL)\n\n"+score[b:]
score=score.replace("if previous.exists() and read(previous).get('judgment'):row.update(read(previous))", "if previous.exists() and valid_cached_record(read(previous),payload,MODEL):row.update(read(previous))")
score=score.replace('from url_checks import check_url_membership','from url_checks import check_url_membership\nfrom grader_contract import valid_cached_record')
score=score.replace("'method':'Fixed execution checks plus diagnostic model judgments", "'grader_version':'3.0','method':'Regrading unchanged .9 answers and evidence. Grounded quotes and versioned cache checks plus diagnostic model judgments")
score=score.replace('Same 28 known questions, criteria and grader v2 as the preceding local run. Deployed MCP app, Databricks model gateway and managed MLflow tracking; local evaluation driver. One retained completed sample, changing live sources and same-family grading; no clinician adjudication.', 'Same 28 known questions and criteria; unchanged .9 captures regraded with grader v3. Model gateway and MLflow tracking in Databricks; local evaluation driver. No new answer generation or source retrieval. Same-family grading; no clinician adjudication.')
(R/'score_current.py').write_text(score,encoding='utf-8')
for src,target in [(P/'presentation/Parent-child Pharmacology MCP — Updated.pptx',W/'reference.pptx'),(P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx',W/'reference.docx')]:shutil.copy2(src,target)
(W/'artifact-references.json').write_text(json.dumps({p.name:sha(p) for p in [W/'reference.pptx',W/'reference.docx']},indent=2),encoding='utf-8')
print(json.dumps({'retained_capture_files':len(captures),'runtime_changed':False,'new_revision':str(R)}))
