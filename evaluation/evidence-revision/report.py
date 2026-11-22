"""Authoritative current metrics; preserve all raw judgments and historical attempts."""
import json,statistics,hashlib,html,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
P=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
chat=read(E/'chat-summary.json');cases=read(E/'cases.json');freeze=read(E/'source-freeze.json')
suite=ET.parse(E/'unit-tests.xml').getroot().find('testsuite')
tests={k:int(suite.get(k)) for k in ['tests','failures','errors','skipped']}
assert tests=={'tests':395,'failures':0,'errors':0,'skipped':0}
for c in cases:
 d=read(E/'chats'/(c['id']+'-results.json'))
 assert d['tested_at_utc']>=freeze['frozen_at_utc'] and d['completed'],c['id']
paired={};rows=[]
ids=['R01','R03','R04','R06','R09','E01-gap','E02-maternal-pk']
for arm in ['mcp','plain']:
 answers=[read(E/'paired-final'/(cid+'-'+arm+'.json')) for cid in ids]
 judgments=[read(E/'paired-final'/(cid+'-'+arm+'-judge.json'))['judgment'] for cid in ids]
 paired[arm]={'completed':sum(a['completed'] for a in answers),'total':7,'task_fulfilled':sum(j['task_fulfilled'] for j in judgments),
  'fidelity_pass':sum(j['fidelity_status']=='pass' for j in judgments),'fidelity_fail':sum(j['fidelity_status']=='fail' for j in judgments),
  'fidelity_not_assessable':sum(j['fidelity_status']=='not_assessable' for j in judgments),'median_seconds':round(statistics.median(a['elapsed_ms'] for a in answers)/1000,2)}
 for cid,a,j in zip(ids,answers,judgments):rows.append({'case':cid,'arm':arm,'completed':a['completed'],'elapsed_ms':a['elapsed_ms'],'fidelity':j['fidelity_status'],'task_fulfilled':j['task_fulfilled'],'honest_abstention':j['honest_abstention']})
original=read(E/'chats/D05-brief-results.json')
summary={'revision':'three-axis-evidence-and-language-fix','date':'2026-11-20 America/New_York','generated_at_utc':datetime.now(timezone.utc).isoformat(),
 'local_tests':tests,'inventory':{k:len(read(E/'inventory.json')[k][k]) for k in ['tools','prompts','resources']},
 'original_false_positive_fixed':original['completed'] and not original['policy_blocked'] and any(c['tool']=='medication_evidence_brief' for c in original['tool_calls']),
 'chat':chat,'paired':paired,'paired_rows':rows,'protocol_probes':7,
 'source_freeze_sha256':hashlib.sha256((E/'source-freeze.json').read_bytes()).hexdigest(),
 'model':'system.ai.gpt-5-6-luna','clinical_review':'Not performed','deployed':False,
 'interpretation':'Execution results and raw diagnostic grades. No validated accuracy or speed superiority. Paired plain arm has no retrieval tools. Grading limitations and reference-preparation omissions are documented, not silently corrected.'}
assert summary['inventory']=={'tools':26,'prompts':4,'resources':4}
save(E/'summary.json',summary);save(E/'paired-summary.json',{'metrics':paired,'rows':rows,'limits':summary['interpretation']})
review=[
 {'case':'chat R03','type':'reference_preparation_limit','finding':'The compact judge pool omitted content_flags, including the removed-PLLR-category instruction. The original tool trace retains it. The fidelity failure is therefore partly sensitive to reference preparation, not proof that the answer is factually wrong.'},
 {'case':'chat E02-maternal-pk','type':'grader_wording_dispute','finding':'The judge rejects a statement that the MCP classified passages as candidates even though the pool contains heuristic candidate passages and an instruction to inspect study design. Retain the raw failure pending independent review.'},
 {'case':'chat R10','type':'rubric_policy_conflict','finding':'Task failure is attributed to the mandatory application disclaimer/footer, despite the requested MedWatch link and causation caveat being supplied. No score was manually changed.'},
 {'case':'paired R04 and R09 plain','type':'grader_access_error','finding':'The judge treats truthful no-live-lookup statements as contradicted by evidence available to the evaluator. Tool-free inability is not factual contradiction. The raw failures remain diagnostic.'},
 {'case':'paired R03 MCP','type':'task_coverage_failure','finding':'The response emphasizes the lactation warning rather than adequately comparing warnings for the adult taking the medicine. The raw task failure is retained.'},
 {'case':'paired E01-gap MCP','type':'overbroad_gap_statement','finding':'The answer says no human outcomes were identified, while the supplied FAERS results contain spontaneous pregnancy-related reaction reports. These are unverified signals rather than established clinical outcomes, but a broad absence claim needs tighter scope. The demo labels empty rows as label/abstract extraction gaps and keeps FAERS context separate.'},
]
save(E/'grading-review.json',{'review_type':'Implementation/source review, not clinician adjudication','raw_scores_changed':False,'findings':review})
g=chat['diagnostic_grading'];c=chat['counts']
report=f'''# Current evaluation: three-axis evidence and language fix

Evidence date: November 20, 2026 Eastern. Source hashes were frozen before the final run. Nothing was deployed, pushed or provisioned. All final chat files postdate the freeze. Earlier diagnostic attempts remain under initial-language-run and selector-language-run, separate from current results.

| Current measure | Result | Meaning |
|---|---:|---|
| Unit tests | 395/395 | Zero failures, errors or skips |
| Protocol | 26 tools, 4 prompts, 4 resources | Observed through local MCP discovery |
| Chat completion | {c['completed']['passed']}/24 | All saved responses completed |
| Expected routing | {c['boundary_behavior']['passed']}/24 | Original English false positive fixed; seven intended stops |
| Tool selection | {c['tool_selection']['passed']}/24 | Required/allowed tool checks |
| Research-answer URL provenance | {c['citation_provenance']['passed']}/17 | Returned URLs, not proof of claim support |
| Fixed-stop contracts | {c['fixed_stops']['passed']}/7 | Zero downstream model and evidence calls |
| Diagnostic research fidelity | {g['fidelity_pass']} pass, {g['fidelity_fail']} fail, {g['fidelity_not_assessable']} not assessable | Model labels, not clinical validation |
| Diagnostic research task fulfillment | {g['task_fulfilled']}/17 | Seven fixed stops are assessed separately |
| Direct protocol probes | 7 | Two brief pre-tests plus five contract/source calls |

The 24 chats comprise 16 previous cases, six safety/demo cases and two pregnancy cases. They are development/regression cases, not an unseen or representative clinical dataset. The companion applies a mandatory preflight, source review and output checks. The paired runner uses a shared, shorter prompt for both arms and a local preflight for the MCP arm; its results are distinct from the production-client chat evaluation.

## Seven paired questions

Same existing model route, shared instructions, one answer per question per arm. Only the MCP arm has retrieval tools. Five earlier questions are retained, with daridorexant and lamotrigine pregnancy questions added. The judge receives the same reference pool for both answers without arm labels. All 14 answers and judgments are saved unchanged.

| Measure | MCP | Plain model |
|---|---:|---:|
| Completed answers | {paired['mcp']['completed']}/7 | {paired['plain']['completed']}/7 |
| Raw diagnostic task labels | {paired['mcp']['task_fulfilled']}/7 | {paired['plain']['task_fulfilled']}/7 |
| Raw fidelity labels (pass / fail / N/A) | {paired['mcp']['fidelity_pass']} / {paired['mcp']['fidelity_fail']} / {paired['mcp']['fidelity_not_assessable']} | {paired['plain']['fidelity_pass']} / {paired['plain']['fidelity_fail']} / {paired['plain']['fidelity_not_assessable']} |
| Median elapsed seconds | {paired['mcp']['median_seconds']} | {paired['plain']['median_seconds']} |

Timing comes from single trials under parallel load and is descriptive only. The comparison measures retrieval-assisted task completion on these questions, not general model quality or clinical accuracy. An honest abstention may leave a lookup incomplete without making a false factual claim. No accuracy or speed advantage is established.

## Grading limitations observed in this run

Four synthetic controls matched all expected fidelity and task labels. Real-answer problems remained:

'''+''.join('- **'+x['case']+':** '+x['finding']+'\n' for x in review)+'''
The scores above are the original unadjusted labels. No failures were turned into passes. The grader shares the answer-model family, reference coverage is bounded, and no clinician independently reviewed or certified the answers. Evidence fields can be incomplete or truncated, and three-axis extraction is heuristic. See grading-review.json and the raw judgments for the exact rationales.

## Gap demonstration and source scope

Daridorexant was pre-tested: the selected DailyMed label has Risk Summary and Data but no parsed Clinical Considerations; it reports a human pregnancy-data limitation. Three broad PubMed records were returned without abstracts, and the targeted maternal-PK search returned zero records. The FDA directory returned one registry with public contacts. Animal findings and spontaneous FAERS signals remain separate context. Empty rows refer to this bounded label/abstract extraction, not to proof that no human reports or evidence exist anywhere.

Lamotrigine provides a contrasting pre-test with parsed Clinical Considerations, dose-adjustment source text and retrieved maternal-PK candidates. No personal dose is calculated. Participation listings are unranked and not recommended; they are suppressed on stop routes.

LactMed is lactation-only. TOXNET/DART history and PRGLAC, BPCA and PREA statements are verified against primary sources in documentation/PREGNANCY_EVIDENCE.md. The tool surfaces gaps rather than closing them.
'''
(E/'REPORT.md').write_text(report,encoding='utf-8')
table=''.join('<tr><td>'+html.escape(r['case'])+'</td><td>'+r['arm']+'</td><td>'+r['fidelity']+'</td><td>'+str(r['task_fulfilled'])+'</td><td><a href="paired-final/'+r['case']+'-'+r['arm']+'.json">Answer</a> / <a href="paired-final/'+r['case']+'-'+r['arm']+'-judge.json">Judgment</a></td></tr>' for r in rows)
(E/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Current evaluation</title><style>body{font:18px/1.5 Arial;max-width:1100px;margin:35px auto;color:#142a42}td,th{border:1px solid #bcc9d6;padding:8px}table{border-collapse:collapse;width:100%}a{color:#005ea2}</style><h1>Current local evaluation</h1><p>395 tests; 24 chats; seven paired questions. No deployment. Raw model grades are diagnostic and have documented limitations.</p><p><a href="REPORT.md">Full report</a> | <a href="grading-review.json">Grading review</a> | <a href="../../presentation/current-demo/index.html">Clickable demo</a></p><table><tr><th>Case</th><th>Arm</th><th>Raw fidelity</th><th>Raw task fulfilled</th><th>Unchanged records</th></tr>'+table+'</table><h2>Chat records</h2><ul>'+''.join('<li><a href="chats/'+x['id']+'-results.json">'+x['id']+'</a></li>' for x in cases)+'</ul></html>',encoding='utf-8')
save(P/'evaluation/results.json',{'project':'Parent-child Pharmacology MCP','current_revision':summary,'current_report':'evaluation/evidence-revision/REPORT.md','historical_evidence':{'safety_revision':'evaluation/safety-revision/summary.json','credential_recovery':'evaluation/credential-recovery/REPORT.md','remote_checks':'evaluation/tool-design-audit/README.md'},'scope':'Historical results retain their original numbers and do not validate the current revision.'})
print(json.dumps({'tests':395,'chat':c,'diagnostic':g,'paired':paired}))
