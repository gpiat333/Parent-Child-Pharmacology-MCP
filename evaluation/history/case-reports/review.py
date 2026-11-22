import json,hashlib,html,re
from pathlib import Path
B=Path('evaluation/case-reports');R=Path.cwd()
notes={
'C01':('pass','Preserves 24 hours after feeding cessation and antibiotics stopped before resumed feeding; does not combine the interventions or assert proven causality. One repetition only.'),
'C02':('flag','Event order and recurrence interval preserved, but gives 1 gram twice despite explicit no-dosing instruction. Historical quantities, not a treatment recommendation.'),
'C03':('pass','Distinguishes earlier cephalothin exposure from subsequent cephalexin plus probenecid; diarrhea continued rather than newly began at switch.'),
'C04':('pass','Preserves infant cefazolin versus maternal cephalexin, nine-day and two-day relationships, and testing four weeks after completion of TEN treatment. Retains probable attribution.'),
'C05':('flag','Initial turn requested identity confirmation and did not answer; confirmed follow-up retrieved the record and preserved ten days after cessation, but added 1.5 g daily despite no-dosing instruction.'),
'C06':('flag','Core exposures and recurrence preserved; follow-up at 16 months omits explicit of age. This is ambiguous, not a definite claim of 16-month follow-up duration; make the age explicit.'),
'C07':('flag','Main age landmarks and two-week reduced-feeding phase preserved. Adds 10/20 mg doses despite no-dosing instruction. Says exact timing of improvement relative to feeding cessation not specified without distinguishing reported 4.5-to-5-month age landmarks from unknown exact dates.'),
'C08':('flag','Correct order and limits, but includes 10 mg daily despite explicit no-dosing instruction.'),
'C09':('pass','Preserves possible prenatal/transplacental exposure and does not assert milk exposure as established causal route or invent recovery.'),
'C10':('pass','Preserves mixed feeding, weight percentiles and developmental finding. Added infant plasma finding is supported by the same report in the full live Drug Levels section; no fabricated developmental delay.'),
'C11':('pass','Preserves multiple drug exposures, solids at six months and assessments at two/four/six months. Historical feeding pattern described, not recommended.'),
'C12':('flag','Thriving at three months and concurrent drugs correctly reported; broad claim that thyroidectomy timing relative to assessment is unspecified blurs known prior thyroidectomy versus unknown date/elapsed time. Should explicitly preserve prior surgery.')}
rows=[]; packets=[]
cases=json.loads((B/'cases.json').read_text())
for c in cases:
 id=c['id'];base=f'case-report-{id}'+('-confirmed' if id=='C05' else '')
 p=R/'presentation-evidence'/f'{base}-results.json';d=json.loads(p.read_text(encoding='utf-8-sig'));a=d['answer']
 status,note=notes[id]
 doses=re.findall(r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|grams?|g)\b',a,re.I)
 row=dict(id=id,status=status,reviewer='Codex source comparison; NOT independent clinical review',rationale=note,completed=d['completed'],source_cited=c['source']['url'] in a,footer_count=a.count('Informational only; not medical advice.'),dose_quantity_flags=doses,trace=str(p),seconds=d['elapsed_ms']/1000)
 rows.append(row)
 packets.append('<h2>'+id+' — '+html.escape(c['drug'])+' — '+status.upper()+'</h2><p>'+html.escape(note)+'</p><h3>Question</h3><p>'+html.escape(c['question'])+'</p><h3>Checks</h3><ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in c['expected_facts']+c['critical_errors'])+'</ul><h3>Answer</h3><pre>'+html.escape(a)+'</pre><h3>Source excerpt</h3><p><a href="'+c['source']['url']+'">Source</a></p><pre>'+html.escape(c['source']['text'])+'</pre><p>Independent reviewer: ______ | Event order: pass/flag | Unknown intervals: pass/flag | Causal claims: pass/flag | Unsupported extras: pass/flag | Notes: ______</p>')
(B/'review-results.json').write_text(json.dumps(rows,indent=2))
summary='''12 distinct case-report scenarios across 9 LactMed records; 13 chat turns including one identity-confirmation follow-up. All 12 final answers cited the expected source and retained exactly one standard disclaimer. All 12 source-backed final answers used full, untruncated retrieved records (initial C05 confirmation did not retrieve a record). No backend errors occurred. No changes to deployed server or client were made for this batch.
Codex source comparison: six passes under the targeted rubric (C01/C03/C04/C09/C10/C11), six flagged (C02/C05/C06/C07/C08/C12). Four contain unrequested historical dose quantities (C02/C05/C07/C08), which violates the test instruction but is not the same as personalized dosing advice. Three contain imprecise temporal or age qualification (C06/C07/C12); C07 overlaps both groups. These ambiguity flags are conservative review findings, not claims of proven clinical harm. No final answer was found to assert definitive drug causation under this review.
Clindamycin C01 preserved the intended relationships this time. One successful response does not establish reliability given previously inconsistent repeats. Do not replace old failures or call this a clean clinical-accuracy pass.
Method: expected facts and critical-error criteria were saved and hashed before execution; the existing production client and deployed MCP were used. Answers were compared against both frozen excerpts and complete retrieved source records, including added factual claims. No additional MLflow judge run was used for this batch: execution checks are code-based and content adjudication is Codex source comparison, not a blinded human review. Previously used source topics make this a development regression, not held-out validation.
Next: enforce the explicit no-dose instruction through the final-review step, distinguish unknown dates from known before/after relationships, and require age-at-follow-up wording where that is what the source reports. Then rerun flagged cases plus repeat controls. The attached review packet is ready for a qualified clinician/pharmacist; no external reviewer has been contacted and independent review is pending.
'''
(B/'summary.txt').write_text(summary)
style='<style>body{font:16px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:20px}pre{white-space:pre-wrap}td,th{padding:10px;border:1px solid #ccc;text-align:left}h2{border-top:2px solid #789;padding-top:20px}@media print{h2{break-before:page}}</style>'
table='<table><tr><th>Case</th><th>Status</th><th>Source review</th></tr>'+''.join('<tr><td>'+x['id']+'</td><td>'+x['status']+'</td><td>'+html.escape(x['rationale'])+'</td></tr>' for x in rows)+'</table>'
(B/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>Case-report testing results</title>'+style+'<h1>Focused case-report testing</h1><pre>'+html.escape(summary)+'</pre>'+table+'<p><a href="independent-review-packet.html">Independent review packet</a></p>',encoding='utf-8')
(B/'independent-review-packet.html').write_text('<!doctype html><meta charset="utf-8"><title>Independent clinical review packet</title>'+style+'<h1>Independent review packet</h1><p>Review requested, not completed. Compare every claim with its source; assess event order, elapsed time, causal certainty, unsupported extras and instruction adherence. Preliminary Codex flags are shown; this packet is not blinded. Historical source excerpts are not treatment recommendations.</p>'+''.join(packets),encoding='utf-8')
paths=[R/'test-mcp-chat.ps1',R/'chat-output.ps1',Path(r'C:\Users\piatkowskigs\Documents\mcp-mother-child\server.py')]
(B/'execution-manifest.json').write_text(json.dumps({'model_alias':'models.ai.gpt-5-6-luna','files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'source_review':'same model, reasoning low','clinical_review':'pending','source_topics':'previously used, development benchmark'},indent=2))
print(summary)
