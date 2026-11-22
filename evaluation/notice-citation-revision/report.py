from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,statistics,html,sys,xml.etree.ElementTree as ET
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/notice-citation-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
sys.path.insert(0,str(P/'server'))
from core.output_notices import required_notices
suite=ET.parse(R/'unit-tests.xml').getroot().find('testsuite');unit={k:int(suite.get(k)) for k in ['tests','failures','errors','skipped']}
assert unit=={'tests':508,'failures':0,'errors':0,'skipped':0}
freeze=read(R/'source-freeze.json');cases=read(R/'cases.json');C=read(R/'chat-summary.json');checks=read(R/'chat-checks.json')
assert C['diagnostic_grading']['judged']==21
C['limits']='Same 28 known cases and grader v2 as the preceding 473-test run. Only URL extraction changed in deterministic checks. MCP clients now append applicable fixed application notices; before-notice text is retained. One retained completed sample per case, live-source variation, same-family judging, bounded references and no independent clinician review limit interpretation. URL membership is not claim support.'
save(R/'chat-summary.json',C)
assert all(read(R/'run-design-verification.json')['checks'].values())
notice_rows=[];workflow=[]
for case in cases:
    raw=read(R/'chats'/(case['id']+'-results.json'))
    assert raw['completed'] and raw['tested_at_utc']>=freeze['frozen_at_utc']
    expected=required_notices([x['tool'] for x in raw['tool_calls']],raw.get('policy_blocked',False))
    notice_rows.append({'case':case['id'],'expected_ids':[n['id'] for n in expected],'recorded_ids':raw.get('required_notice_ids',[]),'all_required_text_present':all(n['text'] in raw['answer'] for n in expected),'blocked':raw.get('policy_blocked',False)})
    if raw.get('requested_workflow'):
        tool=raw['requested_workflow']['required_tool'];workflow.append({'case':case['id'],'required_tool':tool,'first_tool':raw['tool_calls'][0]['tool'],'satisfied':raw['tool_calls'][0]['tool']==tool})
assert all(x['all_required_text_present'] and x['expected_ids']==x['recorded_ids'] for x in notice_rows)
assert all(x['satisfied'] for x in workflow)
save(R/'notice-contract-checks.json',notice_rows)
ids=['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk'];pairs={};paired_rows=[]
for arm in ['mcp','plain']:
    answers=[read(R/'paired-final'/(i+'-'+arm+'.json')) for i in ids]
    judgments=[read(R/'paired-final'/(i+'-'+arm+'-judge.json'))['judgment'] for i in ids]
    assert all(a['completed'] for a in answers)
    pairs[arm]={'completed':7,'total':7,'task_fulfilled':sum(j['task_fulfilled'] for j in judgments),'fidelity_pass':sum(j['fidelity_status']=='pass' for j in judgments),'fidelity_fail':sum(j['fidelity_status']=='fail' for j in judgments),'fidelity_not_assessable':sum(j['fidelity_status']=='not_assessable' for j in judgments),'median_seconds':round(statistics.median(a['elapsed_ms'] for a in answers)/1000,2)}
    for cid,a,j in zip(ids,answers,judgments):
        expected=required_notices([x['tool'] for x in a.get('calls',[])]) if arm=='mcp' else []
        assert all(n['text'] in a['answer'] for n in expected)
        paired_rows.append({'case':cid,'arm':arm,'completed':True,'fidelity':j['fidelity_status'],'task_fulfilled':j['task_fulfilled'],'elapsed_ms':a['elapsed_ms'],'required_notice_ids':a.get('required_notice_ids',[])})
inv=read(R/'inventory.json');probes=list((R/'protocol-probes').glob('*.json'))+list((R/'workflow-probes').glob('*.json'))+[R/(x+'.json') for x in ['empty','registry','gap-brief','clinician-questions','selector-regression','language-boundary']]
assert len(probes)==20 and all(p.exists() for p in probes)
retries=[]
for name in ['retry-chats.json','retry-paired-judge.json']:
    if (R/name).exists():retries += [x for x in read(R/name) if x.get('action','').startswith('retry') or 'retry' in x]
fixes={'P01_portfolio_notice':next(x['all_required_text_present'] and 'portfolio_interpretation' in x['recorded_ids'] for x in notice_rows if x['case']=='P01-portfolio'),'S6_pregnancy_review_notice':next(x['all_required_text_present'] and 'clinical_framing_review' in x['recorded_ids'] for x in notice_rows if x['case']=='S6-pregnancy'),'historical_R12_adjacent_links':next(x['corrected_parser_pass'] for x in read(R/'url-checker-regression.json')['rows'] if x['case']=='R12'),'current_R12_url_check':next(x['citation_provenance'] for x in checks if x['id']=='R12')}
S={'revision':'required-notices-and-citation-boundaries','policy_version':'2026-11-21.4','generated_at_utc':datetime.now(timezone.utc).isoformat(),'date':'2026-11-21 America/New_York','local_tests':unit,'source_files':len(freeze['files']),'inventory':{k:len(inv[k][k]) for k in ['tools','prompts','resources']},'chat':C,'paired':pairs,'paired_rows':paired_rows,'protocol_probes':20,'workflow_requirements':workflow,'required_notice_records':sum(bool(x['expected_ids']) for x in notice_rows),'required_notices_preserved':all(x['all_required_text_present'] for x in notice_rows),'targeted_fixes':fixes,'source_freeze_sha256':sha(R/'source-freeze.json'),'model':'system.ai.gpt-5-6-luna','clinical_review':'Not performed','deployed':False,'cases_unchanged':True,'grader_prompt_unchanged':True,'paired_system_prompt_unchanged':True,'url_checker_changed':True,'infrastructure_retries':retries,'interpretation':'Deterministic application notices and URL boundary correction, not clinical validation or improved raw-model reasoning. Same known cases and same-family grader. The MCP arm alone has retrieval, workflow enforcement and required notices.'}
assert S['source_files']==112 and S['inventory']=={'tools':30,'prompts':4,'resources':4}
assert fixes['P01_portfolio_notice'] and fixes['S6_pregnancy_review_notice'] and fixes['historical_R12_adjacent_links']
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':pairs,'rows':paired_rows,'limits':S['interpretation']})
findings=[]
for x in checks:
    for flag in ['tool_selection','boundary_behavior','citation_provenance']:
        if x.get(flag) is False:findings.append({'case':x['id'],'type':flag+'_failure','tools':x['tools'],'unmatched_urls':x.get('unmatched_urls',[])})
    if x.get('judgment') and (x['judgment']['fidelity_status']=='fail' or not x['judgment']['task_fulfilled']):findings.append({'case':x['id'],'type':'diagnostic_model_finding','finding':x['judgment']['rationale']})
for x in paired_rows:
    if x['fidelity']=='fail' or not x['task_fulfilled']:findings.append({'case':'paired '+x['case']+' '+x['arm'],'type':'diagnostic_model_finding','finding':read(R/'paired-final'/(x['case']+'-'+x['arm']+'-judge.json'))['judgment']['rationale']})
review_notes=[
 {'case':'D05-brief','observation':'The raw grader alleges dose disclosure but quotes participant counts (12 lactating women and 11 mother-infant pairs). Inspection of the saved final answer found study sizes, exposure percentages and gestational age, but no medication-dose values. This appears to be a grader error; the raw task-failure label is retained. Its other comments about overbroad study-design claims still require review.'},
 {'case':'P01-portfolio','observation':'The original activity-code caveat is present and acknowledged by the grader. The new task failure concerns the absence of an explicit FY2024 grouped count from a capped retrieval. A missing group does not establish zero funded research. The grader also treats the application caveat as an uncited source claim; application policy text is not a retrieved finding.'},
 {'case':'E01-gap','observation':'The answer preserves empty evidence axes but omits returned FAERS signals. The grader disputes its broad no-findings language. Spontaneous reports should remain distinct from confirmed pregnancy-population outcomes; the population/signal interpretation needs review. The raw fidelity/task failures are retained.'},
 {'case':'paired E01-gap mcp','observation':'The raw grader flags dose-bearing animal details and FAERS reaction-count alignment. These remain unresolved output-quality findings; the required notice does not correct them.'}
]
save(R/'grading-review.json',{'raw_scores_changed':False,'review_type':'Diagnostic observations, not clinician adjudication','findings':findings,'technical_review_notes':review_notes,'historical_review':'../brief-routing-revision/grading-review.json'})
c=C['counts'];g=C['diagnostic_grading'];b=pairs
report=f'''# Required caveats and citation-checker correction

Local November 21, 2026 GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim. Nothing deployed, pushed, uploaded or submitted. NIHRePORTERAgent was not modified.

## What changed

The preceding 473-test run omitted two required caveats in generated answers: P01 did not state that activity codes alone do not establish research success; S6-pregnancy did not state that human clinical framing review remains required. Both limits already existed in the payload, but the model dropped them.

The server now exposes applicable `required_display_notices`. The companion and MCP comparison arm render the fixed notices after generation, selecting only trusted local policy text by tool identity. Funding tools require the activity-code interpretation notice. Clinical evidence tools require the clinical-framing-review notice. Repeated rendering does not duplicate exact notice lines. Stop responses do not receive these additions. Before-notice text and applied notice IDs are saved in evaluation traces. Third-party clients must enforce the display contract.

The URL checker now separates adjacent Markdown links and preserves balanced or escaped parentheses. It retains missing/unknown-URL failures and exact query distinctions. This is a bounded HTTP(S) scanner, not a complete Markdown renderer or claim-support grader. On the same historical saved outputs, the old check was 20/21 and the corrected parser is {read(R/'url-checker-regression.json')['corrected_pass']}/21. Historical raw scores remain unchanged; that parser-only comparison is stored separately.

## Current verified results

| Measure | Current result | Meaning |
|---|---:|---|
| Unit tests | 508 passed | Zero failures, errors or skips; 35 added regressions |
| Source freeze | 112 files | Frozen before evaluation |
| Inventory | 30 tools, 4 prompts, 4 resources | No new MCP tools |
| Chat completion | {c['completed']['passed']}/28 | Current saved answers |
| Expected routes | {c['boundary_behavior']['passed']}/28 | Known-case routing, not clinical sensitivity |
| Required/allowed tools | {c['tool_selection']['passed']}/28 | Separate from answer quality |
| Fixed stops | {c['fixed_stops']['passed']}/7 | Zero downstream evidence/model calls |
| URL provenance | {c['citation_provenance']['passed']}/21 | Corrected extraction; membership only |
| Diagnostic fidelity | {g['fidelity_pass']} pass, {g['fidelity_fail']} fail, {g['fidelity_not_assessable']} not assessable | Fallible model labels |
| Diagnostic task fulfillment | {g['task_fulfilled']}/21 | Separate from seven fixed stops |
| Applicable chat notices | {S['required_notice_records']}/{S['required_notice_records']} preserved | Deterministic final-output check |
| Direct protocol probes | 20 | Source/contract and workflow captures |

P01 and S6-pregnancy contain the previously omitted notices. The earlier E01 composite-first workflow remains enforced; all {len(workflow)} explicit brief requests honored it. The same 28 questions, allowed/required tools, criteria, grader v2 prompt and paired answer prompt were retained. Only URL extraction changed in the execution checker. Synthetic grader controls matched {C['calibration']['fidelity_matches']}/4 fidelity and {C['calibration']['task_matches']}/4 task expectations; this does not validate clinical grading.

## Seven paired questions

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | 7/7 | 7/7 |
| Diagnostic task labels | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| Median successful-attempt seconds | {b['mcp']['median_seconds']} | {b['plain']['median_seconds']} |

The same model and shared answer instructions are used. Only MCP has retrieval tools, required workflow enforcement and fixed application notices. The paired runner uses a shorter prompt than the companion and omits its separate source-review stage. This compares two workflows; it does not isolate raw-model ability. Timings include service/retrieval effects under parallel load and exclude incomplete attempts and retry delays. No accuracy or speed superiority claim is made.

## Grading limitations and retained evidence

Known development cases, one retained completed sample, changing live sources, same-family judging, bounded/truncated references and no independent clinician adjudication limit interpretation. Honest abstention can leave a lookup incomplete without making a false claim. URL membership does not establish support for a claim. A mandatory caveat cannot by itself prevent false reassurance or alarm-inducing framing. S2 and S6 still require human clinical review of real outputs. Conservative English routing can overblock short technical questions; Spanish safety text remains held for human review.

Technical inspection identifies limitations in the current raw judgments. D05's grader alleges doses while quoting participant counts; the final answer contains study sizes, exposure percentages and gestational age, but no medication-dose values were found. This appears to be a grader error, not a corrected score. Its other study-design comments remain reviewable. P01 now includes the original caveat; its current task failure concerns a missing FY2024 grouped count in a capped retrieval, which must not be read as zero funded research. The grader also treats fixed application-policy notices as uncited source claims. E01's omission of returned FAERS signals requires review while preserving the distinction between spontaneous reports and confirmed pregnancy outcomes. The paired E01 output retains dose-bearing animal details and reaction-count alignment concerns.

All current failures and raw rationales remain in `grading-review.json`, `chat-judgments/` and `paired-final/`, with separate technical observations and no manual score adjustments or clinician adjudication. Completed answers were not regenerated to improve scores. Incomplete infrastructure attempts, if any, were retained before retry. The 473-test run and earlier 445, 443 and 395-test runs retain matching source snapshots and original results. Existing managed model access was used without renewing credentials or changing provider settings.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8')
links=''.join(f'<li><a href="chats/{html.escape(x["id"])}-results.json">{html.escape(x["id"])} raw chat</a></li>' for x in cases)
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Required notices and citation evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Required caveats and citation-checker correction</h1><p><a href="summary.json">Metrics</a> · <a href="grading-review.json">Diagnostic failures</a> · <a href="url-checker-regression.json">Parser-only regression</a></p><pre>'+html.escape(report)+'</pre><h2>Raw chats</h2><ul>'+links+'</ul>',encoding='utf-8')
print(json.dumps({'chat':c,'grades':g,'paired':pairs,'fixes':fixes},indent=2))
