import hashlib,html,json,re
from pathlib import Path
B=Path(__file__).parent; R=B.parent.parent
cases=json.loads((B/'gold-questions.json').read_text())
assert hashlib.sha256((B/'gold-questions.json').read_bytes()).hexdigest()==json.loads((B/'manifest.json').read_text())['dataset_sha256']
rows=[]; checks=[]; bodies=[]
for c in cases:
 p=R/'presentation-evidence'/f'gold-v2-production-{c["id"]}-results.json'
 d=json.loads(p.read_text(encoding='utf-8-sig')); a=d['answer'] or ''
 first=next((x.strip() for x in a.splitlines() if x.strip()),'')
 first=re.sub(r'^answer\s*:\s*','',first.replace('*','').replace('`',''),flags=re.I).strip().rstrip('.').lower()
 checks.append(dict(id=c['id'],completed=d['completed'],first_line_match=first in [x.lower() for x in c['accepted_answers']],standard_footer_count=a.count('Informational only; not medical advice.'),tool_calls=len(d['tool_calls'])))
 rows.append({'inputs':{'request':c['question']},'outputs':{'response':a},'expectations':{'expected_facts':c['expected_facts'],'accepted_answers':c['accepted_answers']}})
 bodies.append(f'<h2>{c["id"]}</h2><p>{html.escape(c["question"])}</p><pre>{html.escape(a)}</pre>')
(B/'answers-production.json').write_text(json.dumps(rows,indent=2))
(B/'checks.json').write_text(json.dumps(checks,indent=2))
(B/'results.html').write_text('<!doctype html><meta charset="utf-8"><title>Version 2 targeted regression</title><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:40px auto}pre{white-space:pre-wrap}</style><h1>Version 2 targeted regression</h1><p>Development benchmark; questions and prompt revised before running. Version 1 preserved. These scores are not directly comparable as an unchanged benchmark. Expert review remains pending.</p><pre>'+html.escape(json.dumps(checks,indent=2))+'</pre>'+''.join(bodies),encoding='utf-8')
print(json.dumps(checks,indent=2))
