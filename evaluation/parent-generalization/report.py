import json,html
from pathlib import Path
B=Path(__file__).parent
cases=json.loads((B/'cases.json').read_text());byq={x['question']:x for x in cases}
checks=json.loads((B/'full-checks.json').read_text());records=json.loads((B/'full-eval_results.json').read_text())
run=json.loads((B/'full-run.json').read_text());cal=json.loads((B/'calibration-gates.json').read_text())
summary={'rows':len(checks),'research_rows':sum(not c['blocked'] for c in cases),'boundary_rows':sum(c['blocked'] for c in cases),'run':run,'calibration':cal,'counts':{},'flags':[],'extra_calls':[]}
for name in ['completed','tool_selection','boundary_behavior','citation_provenance']:
 summary['counts'][name]={'passed':sum(bool(c[name]) for c in checks),'total':len(checks)}
for name in ['evidence_fidelity_v2','task_fulfillment_v2']:
 values=[r.get(name+'/value') for r in records]
 summary['counts'][name]={'passed':sum(v is True or v=='yes' for v in values),'total':len(records),'missing_or_error':sum(v not in [True,False,'yes','no'] for v in values)}
 research=[r for r in records if not byq[r['request']['question']]['blocked']]
 summary['counts'][name]['research_passed']=sum(r.get(name+'/value') is True or r.get(name+'/value')=='yes' for r in research)
 for r in records:
  if r.get(name+'/value') is not True and r.get(name+'/value')!='yes':
   summary['flags'].append({'id':byq[r['request']['question']]['id'],'check':name,'value':r.get(name+'/value'),'rationale':r.get(name+'/rationale'),'error':r.get(name+'/error')})
summary['extra_calls']=[{'id':c['id'],'tools':c['out_of_scope_calls']} for c in checks if c['out_of_scope_calls']]
(B/'summary.json').write_text(json.dumps(summary,indent=2))
table=''.join('<tr><td>'+html.escape(k)+'</td><td>'+str(v['passed'])+'/'+str(v['total'])+'</td></tr>' for k,v in summary['counts'].items())
flags=''.join('<li><b>'+html.escape(f['id']+' '+f['check'])+'</b>: '+html.escape(f['rationale'] or str(f['error']))+'</li>' for f in summary['flags'])
url='https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/'+run['run_id']
body=f'''<!doctype html><html><meta charset="utf-8"><title>Fresh parent generalization evaluation</title><style>body{{font:17px Arial;line-height:1.5;max-width:1050px;margin:40px auto;color:#173047}}h1,h2{{color:#001970}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd8e0;padding:10px;text-align:left}}th{{background:#17467d;color:white}}li{{margin:14px 0}}</style><h1>Fresh parent-question MLflow evaluation</h1><p>November 19, 2026. Sixteen newly worded development questions: twelve research questions and four fixed boundary cases. Same deployed server and full 27-tool inventory throughout; no answer regeneration to improve scores.</p><table><tr><th>Check</th><th>Raw result</th></tr>{table}</table><p><a href="{url}">Completed MLflow run</a>. Eighty case assessments, plus twenty separate calibration assessments. The two v2 quality scores combine twelve AI-judged research answers with four deterministic approved-refusal checks; they are not clinical accuracy measures.</p><h2>Coverage</h2><p>Amoxicillin, sumatriptan and metformin breastfeeding evidence; naproxen recalls; topiramate pregnancy registry; pediatric ADHD and Canadian epilepsy studies; FDA pregnancy public input; montelukast safety notices; MedWatch reporting; PubMed levetiracetam abstracts; infant acetaminophen adverse-event reports. Boundaries test a negated-dose phrase followed by an actual stop request, vague pill appearance, missed-dose scheduling and unidentified blood-pressure medicine.</p><h2>Judge calibration</h2><pre>{html.escape(json.dumps(cal,indent=2))}</pre><p>The four synthetic controls contain both correct and deliberately wrong answers. A failed calibration marks that judge diagnostic-only. Even four correct control verdicts do not establish broad judge reliability or clinical validation.</p><h2>Raw flags</h2><ul>{flags or '<li>No raw judge flags.</li>'}</ul><h2>Tool scope</h2><pre>{html.escape(json.dumps(summary['extra_calls'],indent=2))}</pre><h2>Interpretation and limitations</h2><p>These are development cases with new wording and several new medicines, not independently authored clinical gold questions. Source evidence is the live tool response; source correctness/completeness is not independently certified. One generation per question and unpinned judge versions limit comparisons. Citation provenance checks returned URLs, not support for every clinical sentence. Manual review, including disputed flags, is saved separately without replacing raw verdicts.</p><p>Reproduction: cases.json and manifest.json freeze questions and client hash; run.ps1 captures each response; score.py evaluates captured answers. Original earlier experiments are preserved. See summary.json, full-eval_results.json and review-notes.json for detailed evidence.</p></html>'''
(B/'report.html').write_text(body,encoding='utf-8')
notes=json.loads((B/'review-notes.json').read_text())
review='<h2>Manual review: confirmed weaknesses and disputed flags</h2><ul>'+''.join('<li><b>'+html.escape(f['id']+' — '+f['status'])+'</b>: '+html.escape(f['finding'])+'</li>' for f in notes['findings'])+'</ul><p>Several raw judge rationales contradict the captured text: R01 cites its record and was not truncated; R06 requested up to two studies, not exactly two; R08 explicitly says no submission was made; R09 states the current-index limit; R11 was specifically an abstract-summary request. These flags remain in raw scores. No corrected clinical-accuracy percentage is calculated.</p>'
body=body.replace('<h2>Raw flags</h2>',review+'<h2>Raw flags</h2>')
(B/'report.html').write_text(body,encoding='utf-8')
print(json.dumps(summary,indent=2))
