import json,hashlib,html,re
from pathlib import Path
B=Path(__file__).parent;R=B.parent.parent
cases=json.loads((B/'cases.json').read_text());assert hashlib.sha256((B/'cases.json').read_bytes()).hexdigest()==json.loads((B/'manifest.json').read_text())['dataset_sha256']
rows=[];panels=[]
for c in cases:
 p=R/'presentation-evidence'/f'case-report-{c["id"]}-results.json'
 if not p.exists():continue
 d=json.loads(p.read_text(encoding='utf-8-sig')); a=d.get('answer') or ''; retrieved=[]
 for call in d.get('tool_calls',[]):
  if call['tool']!='get_lactmed_record':continue
  for item in call['result'].get('content',[]):
   try:v=json.loads(item.get('text',''))
   except:continue
   if isinstance(v,dict) and v.get('text'):retrieved.append(v)
 row={'id':c['id'],'completed':d['completed'],'review_applied':d.get('source_review_applied'), 'standard_footer_count':a.count('Informational only; not medical advice.'),'expected_source_cited':c['source']['url'] in a,'retrieved_expected_source':any(v.get('url')==c['source']['url'] for v in retrieved),'has_untruncated_expected_source':any(v.get('url')==c['source']['url'] and not v.get('truncated') for v in retrieved),'seconds':d['elapsed_ms']/1000}
 rows.append(row)
 panels.append('<h2>'+c['id']+' — '+html.escape(c['drug'])+'</h2><p>'+html.escape(c['question'])+'</p><h3>Expected facts</h3><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in c['expected_facts'])+'</ul><h3>Critical errors to check</h3><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in c['critical_errors'])+'</ul><h3>Answer</h3><pre>'+html.escape(a)+'</pre><details><summary>Frozen source excerpt</summary><a href="'+c['source']['url']+'">Original source</a><pre>'+html.escape(c['source']['text'])+'</pre></details><details><summary>Live retrieved source</summary><pre>'+html.escape(json.dumps(retrieved,indent=2))+'</pre></details><p>Independent reviewer: __________ | Timing: pass / flag | Causality: pass / flag | Unsupported claims: pass / flag | Notes: __________</p>')
(B/'execution-checks.json').write_text(json.dumps(rows,indent=2))
(B/'review-packet.html').write_text('<!doctype html><meta charset="utf-8"><title>12 case-report review packet</title><style>body{font:16px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:20px}pre{white-space:pre-wrap}h2{border-top:2px solid #789;padding-top:20px}@media print{details{display:block}h2{break-before:page}}</style><h1>Case-report fidelity review</h1><p>Development regression, not clinical certification. Independent clinician/pharmacist review pending. Review each full answer, not just its short answer. Source text is historical evidence, not treatment advice. No messages have been sent to an external reviewer.</p>'+''.join(panels),encoding='utf-8')
print(json.dumps(rows,indent=2))
