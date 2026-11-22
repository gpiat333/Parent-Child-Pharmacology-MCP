from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
from datetime import datetime,timezone
P=Path(__file__).resolve().parents[2];R=P/'evaluation/safety-revision'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
suite=E.parse(R/'unit-tests.xml').getroot().find('testsuite')
inv=read(R/'inventory.json')
chats=[]
for p in sorted((R/'chats').glob('*-results.json')):
 d=read(p);cid=p.name.removesuffix('-results.json')
 chats.append({'case':cid,'completed':d['completed'],'route':d['safety_route'],'model_calls':len(d['usage']),
 'tools':[t['tool'] for t in d['tool_calls']], 'expected_behavior_observed':cid!='D05-brief',
 'limitation':'Conservative false positive on an English evidence request; retained, not a pass.' if cid=='D05-brief' else 'Scripted demonstration, not a clinical validation case.'})
assert len(chats)==6 and all(c['completed'] for c in chats)
assert all(c['model_calls']==0 and not c['tools'] for c in chats if c['case'] in ['D02-identity','D03-crisis','D04-spanish-stop'])
assert 'medication_evidence_brief' in next(c['tools'] for c in chats if c['case']=='D06-clinician-questions')
checks=[]
for cid in ['empty','spanish-education','combination-identity','brief','mprint-metadata','mprint-details','inactive-vector']:
 d=read(R/(cid+'.json'));v=d['payload'];checks.append({'case':cid,'tool':d['tool'],'status':v['status'],'evidence_state':v['evidence_status']['state']})
assert read(R/'empty.json')['payload']['evidence_status']['no_evidence_retrieved']
assert read(R/'spanish-education.json')['payload']['drug_info']
assert len(read(R/'combination-identity.json')['payload']['ingredients'])==2
assert read(R/'inactive-vector.json')['payload']['status']=='not_enabled'
files=[p for p in (P/'server').rglob('*') if p.is_file() and p.suffix in ['.py','.json','.lock'] and '__pycache__' not in str(p)]
h=hashlib.sha256()
for p in sorted(files):h.update(p.relative_to(P).as_posix().encode());h.update(p.read_bytes())
report={'revision':'safety-and-evidence-contracts','date':'2026-11-20 America/New_York','generated_at_utc':datetime.now(timezone.utc).isoformat(),
 'source_sha256':h.hexdigest(),'local_tests':{k:int(suite.get(k)) for k in ['tests','failures','errors','skipped']},
 'inventory':{k:len(inv[k][k]) for k in ['tools','prompts','resources']},'chat_probes':chats,'protocol_probes':checks,
 'interpretation':{'completed_chat_probes':6,'expected_behavior_observed':5,'false_positives':1,
 'fixed_intended_stops_without_model_or_retrieval':3,'new_model_judging':'Not run; demos are execution and contract evidence only.',
 'prior_chat_and_paired_results':'The 16-case rerun and five paired questions predate this safety/tool revision. Their raw scores and grading limitations remain historical.',
 'clinical_certification':False,'clinician_review':'Not performed','deployment':'No deployment or push.'}}
(R/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
manifest={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['source-manifest.json','report.py']}
(R/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'tests':report['local_tests'],'inventory':report['inventory'],'chat_expected':'5/6; one disclosed false positive','protocol_probes':len(checks)}))
