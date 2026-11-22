from pathlib import Path
from datetime import datetime,timezone
import difflib,hashlib,html,json,re,statistics,sys,xml.etree.ElementTree as ET
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/grader-attribution-revision';OLD=P/'evaluation/report-context-revision'
sys.path.insert(0,str(R))
from grader_contract import valid_cached_record
from paired_evaluation import MODEL,CASE_IDS
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=read(OLD/'summary.json');C=read(R/'chat-summary.json');cases=read(R/'cases.json')
def tests(name):
    t=ET.parse(R/name).getroot().find('testsuite');return {k:int(t.get(k)) for k in ['tests','failures','errors','skipped']}
assert tests('local-unit-tests.xml')==dict(tests=562,failures=0,errors=0,skipped=0)
assert tests('grader-unit-tests.xml')==dict(tests=30,failures=0,errors=0,skipped=0)
lineage=read(R/'capture-lineage.json')
for name,digest in lineage['files'].items():assert sha(R/name)==sha(OLD/name)==digest,name
for name,digest in read(R/'run-design-verification.json')['evaluator_files'].items():assert sha(R/name)==digest,name
rows=[];paired={};findings=[];attempts=0;repairs=0
for arm,ids in [('chat',[c['id'] for c in cases if not c['blocked']]),('mcp',CASE_IDS),('plain',CASE_IDS)]:
    armrows=[]
    for cid in ids:
        gradepath=Path('chat-judgments')/(cid+'.json') if arm=='chat' else Path('paired-final')/(cid+'-'+arm+'-judge.json')
        inputpath=Path('chat-judge-inputs')/(cid+'.json') if arm=='chat' else Path('paired-judge-inputs')/(cid+'-'+arm+'.json')
        record=read(R/gradepath);payload=read(R/inputpath)
        assert valid_cached_record(record,payload,MODEL),(cid,arm)
        j=record['judgment'];old=read(OLD/gradepath)['judgment'];attempts+=len(record['attempts']);repairs+=len(record['attempts'])-1
        row={'case':cid,'arm':arm,'old_fidelity':old['fidelity_status'],'fidelity':j['fidelity_status'],
             'old_task':old['task_fulfilled'],'task_fulfilled':j['task_fulfilled'],
             'changed':old['fidelity_status']!=j['fidelity_status'] or old['task_fulfilled']!=j['task_fulfilled'],
             'old_rationale':old['rationale'],'rationale':j['rationale'],
             'accepted_attempt':record['accepted_attempt'],'grade_path':gradepath.as_posix()}
        rows.append(row);armrows.append(row)
        if j['fidelity_status']=='fail' or not j['task_fulfilled']:findings.append({**row,**j})
    if arm!='chat':
        captures=[read(R/'paired-final'/(cid+'-'+arm+'.json')) for cid in ids]
        paired[arm]={'completed':sum(d['completed'] for d in captures),'total':7,
          'task_fulfilled':sum(row['task_fulfilled'] for row in armrows),
          'fidelity_pass':sum(row['fidelity']=='pass' for row in armrows),
          'fidelity_fail':sum(row['fidelity']=='fail' for row in armrows),
          'fidelity_not_assessable':sum(row['fidelity']=='not_assessable' for row in armrows),
          'retained_capture_median_seconds':round(statistics.median(d['elapsed_ms'] for d in captures)/1000,2)}
verified={phase:read(R/'mlflow'/(phase+'-verification.json')) for phase in ['research','stops','paired']}
assert sum(v['rows_verified'] for v in verified.values())==42
assert all(v['all_applicable_scores_present'] and v['assessment_errors']==0 for v in verified.values())
assert all(t['scores']['grade_attribution_valid'] for phase in ['research','paired'] for t in verified[phase]['traces'])
app=read(R/'app-current.json');assert app['active_deployment']['deployment_id']==prior['deployment_id']
S={'revision':'grader-attribution-revision','generated_at_utc':datetime.now(timezone.utc).isoformat(),
 'policy_version':'2026-11-21.9','grader_version':'3.0','model':MODEL,
 'local_tests':tests('local-unit-tests.xml'),'grader_tests':tests('grader-unit-tests.xml'),
 'chat':C,'paired':paired,'grading_rows':rows,'grading_deltas':[row for row in rows if row['changed']],
 'grounding_validation':{'accepted_grades':35,'all_passed':True,'model_attempts':attempts,'structural_repairs':repairs,'max_attempts_per_grade':3,'unscored_errors':0},
 'source_files':114,'deployed_runtime_files_previously_verified':93,'inventory':prior['inventory'],
 'capture_files_reused':len(lineage['files']),'answers_reused':42,'answer_generation_repeated':False,'reference_retrieval_repeated':False,
 'previous_summary':'../report-context-revision/summary.json','previous_grader':'v2','cases_unchanged':True,'answer_prompt_unchanged':True,'grader_prompt_unchanged':False,
 'deployment_id':prior['deployment_id'],'app_url':prior['app_url'],'deployment_performed_this_revision':False,'runtime_source_changed':False,'github_push':False,
 'clinical_review':'Not performed','manual_score_overrides':False,'historical_raw_grades_preserved':True,
 'mlflow':{'parent':read(R/'mlflow/parent-run.json'),'runs':{phase:read(R/'mlflow'/(phase+'-run.json')) for phase in verified},'final_rows_verified':42,'assessment_errors':0},
 'calibration':read(R/'calibration-summary.json'),'initial_candidate_calibration':{'fidelity_matches':7,'task_matches':7,'controls':8},
 'scheduling':read(R/'run-design.json')['scheduling'],
 'interpretation':'Grader correction on identical answers and evidence, not a new improvement in model behavior. Known development cases, one retained answer each, bounded reference pools, same-family judge, no clinician adjudication. Quote validation does not validate semantics.'}
S['technical_review_notes']={
 'R04-chat':'The task grader requires returned candidate recall records and statuses, beyond the answer’s total and no-matching-lot caveats. The answer is fidelity-pass; this is an output-completeness judgment, not a finding that the bottle was cleared.',
 'R12-chat':'The fidelity grader flags ancillary methodological statements as unverified in the bounded reference pool. It accepts the report counts, coded age scope and causation/incidence caveats; this is not a finding that those counts are false.',
 'R01-mcp':'The paired fidelity grader flags comparator-study wording and the more specific phrase infant blood-level information. The literal quotes are validated, but the interpretation and clinical importance have not been independently adjudicated. Task fulfillment remains pass.',
 'E01-mcp':'The false reference-dose allegation is removed. A separate requested disclosure of absent abstracts is missing in the unchanged paired answer, so task failure remains.'}
save(R/'summary.json',S);save(R/'paired-summary.json',{'metrics':paired,'rows':[r for r in rows if r['arm']!='chat'],'limits':S['interpretation']})
save(R/'grading-deltas.json',{'historical_scores_modified':False,'manual_overrides':False,'rows':rows,'changed_rows':S['grading_deltas']})
save(R/'grading-review.json',{'manual_overrides':False,'clinical_adjudication':False,'findings':findings})
changes=[];patch=[]
for name in read(R/'run-design-verification.json')['evaluator_files']:
    old=OLD/name;new=R/name
    if not old.exists() or sha(old)!=sha(new):
        changes.append({'file':name,'before_sha256':sha(old) if old.exists() else None,'after_sha256':sha(new)})
        patch.extend(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True) if old.exists() else [],new.read_text(encoding='utf-8').splitlines(True),fromfile='v2/'+name,tofile='v3/'+name))
save(R/'grader-changes.json',{'runtime_files_changed':0,'evaluator_files_changed':len(changes),'changes':changes})
(R/'grader-changes.diff').write_text(''.join(patch),encoding='utf-8')
g=C['diagnostic_grading'];b=paired;parent=S['mlflow']['parent'];cal=S['calibration']
e01_main=read(R/'chat-judgments/E01-gap.json')['judgment'];e01_pair=read(R/'paired-final/E01-gap-mcp-judge.json')['judgment']
e01_note=f"E01 main answer: fidelity {e01_main['fidelity_status']}, task fulfilled {e01_main['task_fulfilled']}. E01 paired answer: fidelity {e01_pair['fidelity_status']}, task fulfilled {e01_pair['task_fulfilled']}. The false dose allegations are removed without changing either answer."
e01_note+=' Main rationale: '+e01_main['rationale']+' Paired rationale: '+e01_pair['rationale']
report=f'''# Grader attribution correction and replay evaluation

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

Grader v3 fixes the E01 reference-to-answer mix-up. The old grader requested exact quotations but never verified that they appeared in the candidate answer. It attributed animal-study doses and eligibility timing from the reference pool to two answers that did not contain them. The [historical exact-text audit](../report-context-revision/grader-attribution-audit.json) and original v2 grades remain unchanged.

The corrected grader separates the candidate and references, requires candidate quotations for negative content findings, anchors omissions to requested requirements, and validates cited URLs against the answer. A cache entry must match the grader implementation, model and exact grading inputs. It accepts the first structurally valid grade, whether pass or fail. Invalid JSON or attribution may trigger up to two correction attempts; all attempts are saved. Unresolved errors receive no score. No code converts a failure to a pass.

## Controlled rerun

All 28 chat captures and 14 paired answers, their evidence and case criteria are byte-identical to the completed .9 run. No answer was regenerated and no source lookup was repeated. This isolates the grading change and avoids mixing it with variation in new answers or live sources. It is not a new independent model-performance sample.

The runtime remains policy .9 on deployment `{S['deployment_id']}`. No app deployment, infrastructure or permission change occurred in this revision. No GitHub upload or official submission occurred. Unit tests and the evaluation driver ran locally; grader calls and MLflow tracking used the existing Databricks services.

## Verified results

| Measure | Result | Scope |
|---|---:|---|
| Server unit tests | 562 passed | Fresh rerun of unchanged application code |
| Evaluator unit tests | 30 passed | Separate attribution, citation binding, cache and error-handling suite |
| Synthetic controls | {cal['fidelity_matches']}/{cal['controls']} fidelity; {cal['task_matches']}/{cal['controls']} task | Includes a true dose violation, source-only dose, concentration, genuine omission and ranking behavior |
| Retained chats checked | {C['counts']['completed']['passed']}/28 | Existing answers; no new generation |
| Routes / tool selections | {C['counts']['boundary_behavior']['passed']}/28 / {C['counts']['tool_selection']['passed']}/28 | Recomputed from retained traces |
| Fixed stops | {C['counts']['fixed_stops']['passed']}/7 | Retained traces contain zero downstream evidence/model calls |
| URL membership | {C['counts']['citation_provenance']['passed']}/21 | Membership is not claim support |
| Research fidelity | {g['fidelity_pass']} pass / {g['fidelity_fail']} fail / {g['fidelity_not_assessable']} N/A | New v3 model judgments |
| Research tasks fulfilled | {g['task_fulfilled']}/21 | Separate from fidelity |
| Grounded grading records | 35/35 | Literal attribution checks; not clinical validation |
| MLflow rows verified | 42/42 | 21 research + 7 fixed stops + 14 paired; zero scorer execution errors |

| Paired measure | MCP | Plain model |
|---|---:|---:|
| Retained completed answers | 7/7 | 7/7 |
| Tasks fulfilled | {b['mcp']['task_fulfilled']}/7 | {b['plain']['task_fulfilled']}/7 |
| Fidelity pass / fail / N/A | {b['mcp']['fidelity_pass']} / {b['mcp']['fidelity_fail']} / {b['mcp']['fidelity_not_assessable']} | {b['plain']['fidelity_pass']} / {b['plain']['fidelity_fail']} / {b['plain']['fidelity_not_assessable']} |
| New answers generated | 0 | 0 |

Only the MCP workflow originally had retrieval, workflow enforcement and fixed notices. Honest abstention can leave a lookup incomplete. The same-family judge uses a bounded shared reference pool that may include material a particular answer never received. N/A is excluded from fidelity rates. No new latency comparison or speed claim is made.

## E01 and historical comparison

{e01_note} The retained pilot record reports each accepted attempt. Minor citation placement issues remain visible in the retained outputs and judge notes; no clinician adjudication is implied. Fixing a false allegation does not erase a different, supported omission.

| Grader on the same .9 answers | Research fidelity / tasks | Paired tasks MCP / plain |
|---|---|---|
| Historical v2 | 21/21 / 20/21 | 6/7 / 1/7 |
| Current v3 | {g['fidelity_pass']}/21 / {g['task_fulfilled']}/21 | {b['mcp']['task_fulfilled']}/7 / {b['plain']['task_fulfilled']}/7 |

All {len(S['grading_deltas'])} rows whose pass/fail scores changed are itemized in [grading-deltas.json](grading-deltas.json), alongside the old and new rationales for every answer. E01 paired remains task-fail, but for a different, supported omission rather than the old false dose allegation. Score differences can reflect the new rubric and model-judge variability; they are not new behavior by the answer model. The earlier .5 figures of research 18/21 tasks and paired MCP 5/7 belong to an older runtime and remain historical.

Current research negatives need separate interpretation. R04 is fidelity-pass but task-fail because the judge expects returned candidate recall records and their statuses, beyond the answer's total and no-matching-lot caveats. R12 meets the requested task, but its ancillary methodological statements are unverified in the bounded pool. The judge accepts R12's counts, coded age scope and causation/incidence caveats. Neither result establishes a clinically false answer. These technical observations do not override the model grades.

The paired MCP R01 answer meets the task but receives a fidelity failure for comparator-study wording and a more specific infant blood-level statement. Its quoted passages are present in the answer and sources; that mechanical check does not validate the judge's interpretation or the clinical importance of the wording. Independent clinical adjudication remains absent.

## Development checks and limitations

The initial v3 candidate matched 7/8 fidelity and 7/8 task control expectations. It incorrectly counted an epistemic caveat as a source claim and a reversed study direction as task-complete. Generic rubric definitions were clarified before the final freeze; the initial results remain in [development/initial-v3-candidate](development/initial-v3-candidate/STATUS.json). A subsequent candidate matched all eight controls but mistyped a long E01 citation URL on all three attempts, so no score was accepted for that answer. Those attempts remain in [development/url-copy-candidate](development/url-copy-candidate/STATUS.json). The implementation now assigns citation IDs to original answer URLs and binds those IDs in code, retaining the model's support judgments. The next candidate incorrectly demanded the word "unranked" even when an answer did not rank anything; its raw grades remain in [development/citation-id-candidate](development/citation-id-candidate/STATUS.json). The final rubric distinguishes behavioral compliance from required disclosures, and adds compliant-list and actual-ranking controls. Missing-abstract disclosures remain required when the task asks for them. All ten final controls match their expectations. These are development controls, not held-out validation.

The final benchmark needed {attempts} model assessment attempts for 35 accepted grades, including {repairs} structural corrections. Correction requests are triggered by attribution/schema checks, not by an undesirable score. The two E01 pilot assessments are reused once in the final benchmark. No completed benchmark answer was replaced. Full raw model attempts, failure-reason fields and input hashes are saved with each grade.

Literal quote validation cannot establish that a quotation is relevant, that an omission is clinically important, or that an answer is safe. The grader remains fallible. Known cases, one retained answer per case/arm, bounded references and no clinician review limit interpretation. Fidelity and task fulfillment are separate. A supported statement may leave a task incomplete; an unverified statement in the bounded pool is not automatically medically false.

{S['scheduling']}

The [MLflow parent run]({parent['url']}) contains the new scores, raw captures, grader code and final documents. Precomputed replay produces one root span per row; full original tool traces are in artifacts. This was not a remote notebook unit-test run.

## Files

The grader changes are confined to `evaluation/grader-attribution-revision`; `server` and `chat-client` remain unchanged. See [grader-changes.diff](grader-changes.diff), [capture-lineage.json](capture-lineage.json), [TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md), and [summary.json](summary.json). The updated deck and evaluation DOCX use these metrics. Saved .4 demo images and video remain explicitly historical.
'''
(R/'REPORT.md').write_text(report,encoding='utf-8')
parts=['# Technical review of v3 replay grades','Historical v2 results are preserved. No manual score overrides or clinician adjudication occurred.','## Every changed score',
       '| Case / arm | Old fidelity → new | Old task → new |','|---|---|---|']
for row in S['grading_deltas']:parts.append(f"| {row['case']} / {row['arm']} | {row['old_fidelity']} → {row['fidelity']} | {row['old_task']} → {row['task_fulfilled']} |")
parts+=['## Current negative grades']
for f in findings:
    parts += [f"### {f['case']} — {f['arm']}",f"Fidelity: {f['fidelity_status']}. Task fulfilled: {f['task_fulfilled']}.",f['rationale']]
    for reason in f['failure_reasons']:
        parts.append(f"- {reason['dimension']} / {reason['kind']}: {reason['explanation']}\n  - Candidate quote: {reason.get('answer_quote')!r}\n  - Requirement quote: {reason.get('requirement_quote')!r}\n  - Reference quote: {reason.get('reference_quote')!r}")
    parts.append(f"[Full grade, validation and raw attempts]({f['grade_path']})")
parts += ['## Interpretation','Validated quotes prove literal presence only. They do not prove the correctness of the model interpretation. Missing source context, inappropriate reassurance or alarm, and clinically meaningful omissions still require human review.',e01_note,'The exact v2 misattribution remains documented; the correction does not amount to a clinician-certified pass.']
parts+=['## Technical interpretation without score overrides']+[f"- {key}: {value}" for key,value in S['technical_review_notes'].items()]
(R/'TECHNICAL_REVIEW.md').write_text(re.sub(r'(?<=\|)\n\n(?=\|)','\n','\n\n'.join(parts))+'\n',encoding='utf-8')
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Grader v3 replay evaluation</title><style>body{font:18px/1.5 Arial;max-width:1050px;margin:40px auto;color:#203849}a{color:#006b93}pre{white-space:pre-wrap}</style><h1>Grader v3 replay evaluation</h1><p><a href="summary.json">Metrics</a> · <a href="TECHNICAL_REVIEW.md">Technical review</a> · <a href="'+html.escape(parent['url'])+'">MLflow run</a></p><pre>'+html.escape(report)+'</pre>',encoding='utf-8')
print(json.dumps({'research':g,'paired':paired,'grade_changes':len(S['grading_deltas']),'structural_repairs':repairs,'rows_verified':42},indent=2))
