from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,re,shutil,xml.etree.ElementTree as ET
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');W=Path(__file__).parent;R=P/'evaluation/brief-routing-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=read(R/'summary.json');freeze=read(R/'source-freeze.json');M=read(R/'slide-map.json')
assert S['local_tests']=={'tests':473,'failures':0,'errors':0,'skipped':0}
assert S['inventory']=={'tools':30,'prompts':4,'resources':4}
assert S['chat']['counts']['completed']=={'passed':28,'total':28}
assert S['protocol_probes']==20 and S['original_failed_check_fixed']
assert all(x['satisfied'] for x in S['workflow_requirements'])
assert all(read(R/'run-design-verification.json')['checks'].values())
for name,digest in freeze['files'].items():
    assert sha(P/name)==digest,name
    target=R/'source-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,target)
for folder in ['program-safety-revision','program-safety-initial','evidence-revision']:
    old=P/'evaluation'/folder;frozen=read(old/'source-freeze.json')
    for name,digest in frozen['files'].items():assert sha(old/'source-snapshot'/name)==digest,(folder,name)
for case in read(R/'cases.json'):
    result=read(R/'chats'/(case['id']+'-results.json'))
    assert result['completed'] and result['tested_at_utc']>=freeze['frozen_at_utc']
assert len(list((R/'paired-final').glob('*-judge.json')))==14
assert read(R/'infrastructure-attempts/paired/R03-mcp-1.json')['error_type']=='TimeoutExpired'
assert read(R/'local-listener-stop.json')['confirmed_connection_refused']
deck=P/'presentation/Parent-child Pharmacology MCP — Updated.pptx';doc=P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
disclaimer='THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.'
with zipfile.ZipFile(deck) as z:
    files=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]))
    assert len(files)==49
    pages=[ET.fromstring(z.read(n)) for n in files]
    title=''.join(x.text or '' for x in pages[0].findall('.//a:t',NS));assert disclaimer in title
    assert 'B4232C' in z.read(files[0]).decode()
    assert all(p.get('show')=='0' for p in pages[15:]) and all(p.get('show')!='0' for p in pages[:15])
    alltext=' '.join(x.text or '' for p in pages for x in p.findall('.//a:t',NS))
    assert '473' in alltext and '106 source files' in alltext
    assert 'Current failures show why review is still needed' not in alltext
    assert 'pending' not in alltext.lower()
with zipfile.ZipFile(doc) as z:
    root=ET.fromstring(z.read('word/document.xml'));alltext=' '.join(n.text or '' for n in root.findall('.//w:t',NS))
    assert '473' in alltext and '106' in alltext and 'E01' in alltext
assert len(read(W/'docx-text.json'))==10
assert sha(deck)==sha(W/'output/professional-v1.pptx')
assert sha(doc)==sha(W/'evaluation-updated.docx')
assert read(P/'evaluation/results.json')['current_revision']==S
video=P/'presentation/Parent-child Pharmacology MCP - Narrated demo.webm'
v=read(P/'presentation/current-demo/video-validation.json')
assert v['width']==1280 and v['height']==720 and v['audio_peak']>.01
assert read(P/'presentation/current-demo/package-viewer-checks.json')['missing_local_links']==0
validation={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'source_files':106,'unit_tests':473,'tools':30,'chat_cases':28,'tool_checks':S['chat']['counts']['tool_selection'],'paired_questions':7,'protocol_probes':20,'deck_slides':49,'main_slides':15,'appendix_slides':34,'docx_pages':10,'original_E01_tool_check_fixed':True,'cases_and_grader_unchanged':True,'exact_red_title_disclaimer_preserved':True,'native_powerpoint_and_word_renders_inspected':True,'docx_renderer_fallback':'Bundled renderer lacks LibreOffice; native Word PDF export and page PNG review used.','source_snapshots_verified':['current','program-safety-revision','program-safety-initial','evidence-revision'],'historical_27_of_28_retained':True,'incomplete_gateway_timeout_retained_before_retry':True,'clinical_review':False,'deployed':False,'listener_stopped':True,'artifacts':{str(f.relative_to(P)):sha(f) for f in [deck,doc,video]}}
(R/'final-validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
manifest={str(f.relative_to(R)):sha(f) for f in sorted(R.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name!='evidence-manifest.json'}
(R/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
files=[f for f in sorted(P.rglob('*')) if f.is_file() and not {'.pytest_cache','__pycache__','.venv'}.intersection(f.parts) and f.name!='SHA256SUMS.txt']
(P/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+f.relative_to(P).as_posix()+'\n' for f in files),encoding='utf-8')
print(json.dumps(validation,indent=2))
