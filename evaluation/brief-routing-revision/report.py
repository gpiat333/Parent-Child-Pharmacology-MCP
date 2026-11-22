from pathlib import Path
from datetime import datetime,timezone
import ast,json,hashlib,statistics,html,xml.etree.ElementTree as ET
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-routing-revision';OLD=P/'evaluation/program-safety-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def constant(p,name):
    return next(ast.literal_eval(n.value) for n in ast.parse(p.read_text(encoding='utf-8')) .body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
suite=ET.parse(R/'unit-tests.xml').getroot().find('testsuite')
unit={k:int(suite.get(k)) for k in ['tests','failures','errors','skipped']}
assert unit=={'tests':473,'failures':0,'errors':0,'skipped':0}
freeze=read(R/'source-freeze.json');cases=read(R/'cases.json');C=read(R/'chat-summary.json');checks=read(R/'chat-checks.json')
assert C['diagnostic_grading']['judged']==21
C['limits']='All 28 cases and the grader v2 prompt match the preceding 445-test run. The four portfolio/coverage/framing cases were introduced in that earlier run, not this rerun. Known development cases, one retained completed sample per case, live-source changes, same-family judging and bounded references limit interpretation. No clinician review. URL membership does not validate a claim. Grader v2 results are not directly comparable with older grader-v1 runs.'
save(R/'chat-summary.json',C)
assert sha(R/'cases.json')==sha(OLD/'cases.json')
assert constant(R/'paired_evaluation.py','JUDGE_PROMPT')==constant(OLD/'paired_evaluation.py','JUDGE_PROMPT')
assert constant(R/'paired_evaluation.py','PROMPT')==constant(OLD/'paired_evaluation.py','PROMPT')
for case in cases:
    row=read(R/'chats'/(case['id']+'-results.json'))
    assert row['completed'] and row['tested_at_utc']>=freeze['frozen_at_utc'],case['id']
ids=['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk'];pairs={};paired_rows=[]
for arm in ['mcp','plain']:
    answers=[read(R/'paired-final'/(i+'-'+arm+'.json')) for i in ids]
    judgments=[read(R/'paired-final'/(i+'-'+arm+'-judge.json'))['judgment'] for i in ids]
    pairs[arm]={'completed':sum(a['completed'] for a in answers),'total':7,'task_fulfilled':sum(j['task_fulfilled'] for j in judgments),'fidelity_pass':sum(j['fidelity_status']=='pass' for j in judgments),'fidelity_fail':sum(j['fidelity_status']=='fail' for j in judgments),'fidelity_not_assessable':sum(j['fidelity_status']=='not_assessable' for j in judgments),'median_seconds':round(statistics.median(a['elapsed_ms'] for a in answers)/1000,2)}
    for cid,a,j in zip(ids,answers,judgments):paired_rows.append({'case':cid,'arm':arm,'completed':a['completed'],'fidelity':j['fidelity_status'],'task_fulfilled':j['task_fulfilled'],'elapsed_ms':a['elapsed_ms']})
inv=read(R/'inventory.json');e01=read(R/'chats/E01-gap-results.json')
workflow_rows=[]
for case in cases:
    raw=read(R/'chats'/(case['id']+'-results.json'))
    if raw.get('requested_workflow'):
        tools=[c['tool'] for c in raw['tool_calls']]
        workflow_rows.append({'case':case['id'],'required_tool':raw['requested_workflow']['required_tool'],'first_tool':tools[0] if tools else None,'satisfied':bool(tools) and tools[0]==raw['requested_workflow']['required_tool']})
probes=list((R/'protocol-probes').glob('*.json'))+list((R/'workflow-probes').glob('*.json'))+[R/(x+'.json') for x in ['empty','registry','gap-brief','clinician-questions','selector-regression','language-boundary']]
assert len(probes)==20 and all(p.exists() for p in probes)
S={'revision':'required-evidence-brief-workflow','policy_version':'2026-11-21.3','generated_at_utc':datetime.now(timezone.utc).isoformat(),'date':'2026-11-21 America/New_York','local_tests':unit,'source_files':len(freeze['files']),'inventory':{k:len(inv[k][k]) for k in ['tools','prompts','resources']},'chat':C,'paired':pairs,'paired_rows':paired_rows,'protocol_probes':20,'workflow_requirements':workflow_rows,'original_failed_check_fixed':e01['tool_calls'][0]['tool']=='medication_evidence_brief' and next(c['tool_selection'] for c in checks if c['id']=='E01-gap'),'source_freeze_sha256':sha(R/'source-freeze.json'),'model':'system.ai.gpt-5-6-luna','clinical_review':'Not performed','deployed':False,'cases_unchanged':True,'grader_prompt_unchanged':True,'paired_system_prompt_unchanged':True,'infrastructure_retries':read(R/'retry-chats.json'),'interpretation':'Deterministic workflow enforcement and execution checks, not improved autonomous model selection or clinical validation. Same 28 known questions and grader v2 as the prior 445-test run; one new sample per case. Live sources and model variability limit comparison. The plain model has no retrieval tools.'}
assert S['inventory']=={'tools':30,'prompts':4,'resources':4}
S['infrastructure_retries'] += [x for x in read(R/'retry-paired-judge.json') if x.get('action')=='retry_incomplete_pair']
assert S['source_files']==106 and S['original_failed_check_fixed'] and all(x['satisfied'] for x in workflow_rows)
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':pairs,'rows':paired_rows,'limits':S['interpretation']})
findings=[]
if (R/'url-parser-review.json').exists():findings.append(read(R/'url-parser-review.json'))
for x in checks:
    if not x['tool_selection']:findings.append({'case':x['id'],'type':'tool_selection_failure','tools':x['tools']})
    if not x['boundary_behavior']:findings.append({'case':x['id'],'type':'boundary_behavior_failure'})
    if x.get('judgment') and (x['judgment']['fidelity_status']=='fail' or not x['judgment']['task_fulfilled']):findings.append({'case':x['id'],'type':'diagnostic_model_finding','finding':x['judgment']['rationale']})
for x in paired_rows:
    if x['fidelity']=='fail' or not x['task_fulfilled']:findings.append({'case':'paired '+x['case']+' '+x['arm'],'type':'diagnostic_model_finding','finding':read(R/'paired-final'/(x['case']+'-'+x['arm']+'-judge.json'))['judgment']['rationale']})
save(R/'grading-review.json',{'raw_scores_changed':False,'review_type':'Diagnostic observations, not clinician adjudication','findings':findings,'historical_review':'../program-safety-revision/grading-review.json'})
c=C['counts'];g=C['diagnostic_grading'];b=pairs
report=f'''# Evidence brief workflow correction and rerun

Local November 21, 2026 GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim. Nothing deployed, pushed or submitted.

## Cause and correction

The prior E01 daridorexant pregnancy request asked for an evidence brief. The model used separate label, literature, trial, registry and coverage calls instead of `medication_evidence_brief`. The predeclared check required that composite. Its answer received a diagnostic task pass, but tool selection failed. The prior **27/28** remains unchanged under `../program-safety-revision`.

The preflight now recognizes explicit English evidence-brief requests only after safety, identity, privacy and language checks allow research. It returns a required workflow. The companion and MCP comparison arm require exactly one composite call before optional source lookups or a final answer, using the model gateway's named-tool choice. A missing tool or bypass attempt stops execution. The composite still confirms drug identity internally before source retrieval. Other requests retain automatic tool selection. Negated requests and incidental mentions do not activate the workflow.

This is a workflow correction, not proof that the model learned better tool selection. Every third-party client must enforce the returned contract. Narrow request matching can miss paraphrases. The conservative English gate can also overblock short technical requests; its thresholds were not changed in this revision.

## Current verified results

| Measure | Current result | Meaning |
|---|---:|---|
| Unit tests | 473 passed | Zero failures, errors or skips; 28 added regression cases |
| Inventory | 30 tools, 4 prompts, 4 resources | No new tool added |
| Source freeze | 106 files | Frozen before this evaluation |
| Chat completion | {c['completed']['passed']}/28 | Current raw records retained |
| Expected routing | {c['boundary_behavior']['passed']}/28 | Known-case execution, not clinical sensitivity |
| Required/allowed tools | {c['tool_selection']['passed']}/28 | Original E01 check passes using the composite first |
| Fixed stops | {c['fixed_stops']['passed']}/7 | No downstream evidence/model calls |
| URL provenance | {c['citation_provenance']['passed']}/21 | Membership, not claim support |
| Diagnostic fidelity | {g['fidelity_pass']} pass, {g['fidelity_fail']} fail, {g['fidelity_not_assessable']} not assessable | Fallible same-family model labels |
| Diagnostic task fulfillment | {g['task_fulfilled']}/21 | Separate from execution and seven fixed stops |
| Direct protocol probes | 20 | 17 source/contract probes plus 3 workflow probes |

The {len(workflow_rows)} explicit brief requests all called the composite first. E01 was run first to verify the integration and retained unchanged in the full batch. Completed answers were not regenerated to improve scores. Any incomplete infrastructure attempts and retries are saved separately. All 28 questions, allowed/required tools, grading criteria, the grader prompt and the paired system prompt match the preceding 445-test run. Four synthetic grader controls matched {C['calibration']['fidelity_matches']}/4 fidelity and {C['calibration']['task_matches']}/4 task expectations. That small calibration does not validate clinical grading.

## Seven paired comparisons

| Measure | MCP workflow | Plain model |
|---|---:|---:|
| Completed | {b['mcp']['completed']}/7 | {b['plain']['completed']}/7 |
| Diagnostic task labels | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| Median seconds | {b['mcp']['median_seconds']} | {b['plain']['median_seconds']} |

The same model and shared answer instructions are used. Only the MCP arm has retrieval tools and enforces the preflight workflow requirement. The companion has a longer prompt and a separate source-review pass; paired answers are therefore not identical to the production companion. Timing describes retained successful attempts under parallel load and excludes the archived timeout and retry delay. There is no clinical accuracy or speed superiority claim.

## Grading limitations and remaining failures

Known development cases, one sample, changing live sources, same-family judging, bounded/truncated reference material and no independent clinician adjudication limit the interpretation. An unverified statement is not automatically false, and honest tool-free abstention can leave a lookup incomplete. URL membership does not establish support for a claim. Execution success does not establish accurate or appropriate clinical wording.

Raw failure rationales are retained in `grading-review.json`, `chat-judgments/` and `paired-final/`. The previous dose-exclusion and three-women-versus-three-reports findings are historical and remain in the preceding run. S2 false reassurance and S6 discontinuation harm still require clinical review of real outputs. Heuristic routing, source extraction and language checks remain imperfect. Spanish safety/referral text remains held for human review.

The two unmet chat-task criteria are the omitted activity-code interpretation caveat in P01 and the omitted explicit human-clinical-framing-review statement in S6-pregnancy. The raw URL check remains 20/21. In R12, its regex joined two adjacent Markdown links; both separate targets occur in the saved tool outputs. `url-parser-review.json` documents that parser limitation without changing the score or claiming that URL membership validates the answer.

## Retained evidence

The earlier 445-test run, 443-test initial run and 395-test revision retain their original raw results and matching source snapshots. Earlier deployed checks are historical and do not validate this local version. Existing model access was used; credentials and provider settings were not changed.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8')
links=''.join(f'<li><a href="chats/{html.escape(case["id"])}-results.json">{html.escape(case["id"])} raw chat</a></li>' for case in cases)
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Evidence brief workflow evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Evidence brief workflow correction</h1><p><a href="summary.json">Metrics</a> · <a href="grading-review.json">Raw diagnostic failure rationales</a> · <a href="source-freeze.json">Frozen source</a></p><pre>'+html.escape(report)+'</pre><h2>Raw chats</h2><ul>'+links+'</ul>',encoding='utf-8')
print(json.dumps({'chat':c,'grades':g,'paired':pairs,'workflow':workflow_rows},indent=2))
