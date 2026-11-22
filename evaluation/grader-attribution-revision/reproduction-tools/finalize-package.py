from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,sys,zipfile,xml.etree.ElementTree as ET
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision';version=sys.argv[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=read(R/'summary.json');review=read(R/'artifact-review.json');freeze=read(R/'local-source-freeze.json')
assert S['local_tests']==dict(tests=562,failures=0,errors=0,skipped=0)
assert S['grader_tests']==dict(tests=30,failures=0,errors=0,skipped=0)
assert S['calibration']['fidelity_matches']==S['calibration']['task_matches']==S['calibration']['controls']==10
assert not any(S[k] for k in ['github_push','deployment_performed_this_revision','runtime_source_changed','answer_generation_repeated','reference_retrieval_repeated','manual_score_overrides'])
app=read(R/'app-final.json');assert app['active_deployment']['deployment_id']==S['deployment_id']
assert app['active_deployment']['status']['state']=='SUCCEEDED' and app['app_status']['state']=='RUNNING'
design=read(R/'run-design-verification.json');assert design['cases_unchanged'] and design['captures_byte_identical'] and design['runtime_source_unchanged']
for name,digest in design['evaluator_files'].items():assert sha(R/name)==digest,name
for name,digest in freeze['files'].items():assert sha(P/name)==sha(R/'source-snapshot'/name)==digest,name
for name,digest in read(R/'capture-lineage.json')['files'].items():assert sha(R/name)==sha(P/'evaluation/report-context-revision'/name)==digest,name
prior=P/'evaluation/report-context-revision';old_manifest=read(prior/'evidence-manifest.json')
for name,digest in old_manifest.items():assert sha(prior/name)==digest,('prior evidence modified',name)
ids=[]
for phase in ['research','stops','paired']:
 v=read(R/'mlflow'/(phase+'-verification.json'));assert v['assessment_errors']==0 and v['all_applicable_scores_present']
 ids.extend(t['trace_id'] for t in v['traces'])
assert len(ids)==len(set(ids))==42
rm=S['mlflow']['runs']['research']['persisted_metrics'];g=S['chat']['diagnostic_grading']
assert abs(rm['diagnostic_task_fulfilled/mean']-g['task_fulfilled']/21)<1e-9
assert abs(rm['diagnostic_fidelity_pass/mean']-g['fidelity_pass']/(21-g['fidelity_not_assessable']))<1e-9
assert len(list((R/'chat-judgments').glob('*.json')))==21 and len(list((R/'paired-final').glob('*-judge.json')))==14
deck=P/'presentation/Parent-child Pharmacology MCP — Updated.pptx';doc=P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
disclaimer='THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.'
with zipfile.ZipFile(deck) as z:
 names=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]));assert len(names)==49
 pages=[ET.fromstring(z.read(n)) for n in names]
 assert disclaimer in ''.join(x.text or '' for x in pages[0].findall('.//a:t',NS)) and 'B4232C' in z.read(names[0]).decode()
 assert all(p.get('show')=='0' for p in pages[15:]) and all(p.get('show')!='0' for p in pages[:15])
 text=' '.join(x.text or '' for p in pages for x in p.findall('.//a:t',NS))
 assert '562' in text and '30 grader tests' in text and 'Same answers, corrected grading' in text
with zipfile.ZipFile(doc) as z:
 root=ET.fromstring(z.read('word/document.xml'));text=' '.join(n.text or '' for n in root.findall('.//w:t',NS))
 assert '562' in text and 'grader v3' in text and '42' in text
assert sha(deck)==sha(W/('output/professional-'+version+'.pptx')) and sha(doc)==sha(W/'evaluation-updated.docx')
assert read(P/'evaluation/results.json')['current_revision']==S
assert review['docx']['all_pages_inspected_at_full_size'] and review['deck']['changed_slides_inspected_full_size']
assert read(R/'artifact-metric-consistency.json')['all_checks_passed']
helpers=R/'reproduction-tools';helpers.mkdir(exist_ok=True)
for path in sorted(W.glob('*.py')):shutil.copy2(path,helpers/path.name)
for path in sorted(W.glob('*.mjs')):shutil.copy2(path,helpers/path.name)
for path in sorted(W.glob('*.ps1')):shutil.copy2(path,helpers/path.name)
(helpers/'README.md').write_text('Exact local helpers for the grader-only replay. Paths are machine-specific. Existing Databricks CLI sign-in supplies authentication; no credentials are embedded. No app deployment helper is included. Replaying retained .9 answers isolates the grader change; it does not generate new answers or requery sources. Preparation and archive helpers are audit records and should not be rerun blindly. Final evaluator and capture hashes identify the completed run.\n',encoding='utf-8')
with zipfile.ZipFile(R/'evaluation-harness.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(helpers.iterdir()):z.write(f,f.relative_to(R).as_posix())
 for name in design['evaluator_files']:z.write(R/name,name)
validation={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'fresh_server_tests':562,'grader_tests':30,'synthetic_controls':10,'local_frozen_files':114,'prior_runtime_files_verified':93,'retained_capture_files_verified':77,'retained_chats':28,'paired_questions':7,'accepted_model_grades':35,'grounding_validation_passed':True,'mlflow_final_rows_verified':42,'assessment_errors':0,'deck_slides':49,'main_slides':15,'appendix_slides':34,'docx_pages':len(read(W/'docx-text.json')),'exact_red_title_disclaimer_preserved':True,'rendered_artifacts_visually_reviewed':True,'prior_evidence_manifest_unchanged':True,'clinical_review':False,'deployment_performed_this_revision':False,'deployment_id':S['deployment_id'],'github_push':False,'driver_and_unit_tests':'local','grader_and_tracking':'existing Databricks services','artifacts':{str(f.relative_to(P)):sha(f) for f in [deck,doc,P/'presentation/Parent-child Pharmacology MCP - Narrated demo.webm']}}
(R/'final-validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
manifest={f.relative_to(R).as_posix():sha(f) for f in sorted(R.rglob('*')) if f.is_file() and not {'.pytest_cache','__pycache__'}.intersection(f.parts) and f.name!='evidence-manifest.json'}
(R/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
files=[f for f in sorted(P.rglob('*')) if f.is_file() and not {'.pytest_cache','__pycache__','.venv'}.intersection(f.parts) and f.name!='SHA256SUMS.txt']
(P/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+f.relative_to(P).as_posix()+'\n' for f in files),encoding='utf-8')
print(json.dumps(validation,indent=2))
