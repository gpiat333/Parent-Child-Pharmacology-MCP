import hashlib,json,re
from pathlib import Path
B=Path(__file__).parent;R=B.parent.parent
assert hashlib.sha256((B/'cases.json').read_bytes()).hexdigest()==json.loads((B/'manifest.json').read_text())['dataset_sha256']
cases=json.loads((B/'cases.json').read_text());rows=[]
for c in cases:
 p=R/'presentation-evidence'/f'mprint-legend-retest-{c["id"]}-results.json'
 d=json.loads(p.read_text(encoding='utf-8-sig'));ids=set()
 # Conservative heuristic: numerical IDs occurring in actual tool content or the question.
 # This is not a complete semantic provenance check; the LLM source-fidelity scorer and review complement it.
 evidence=json.dumps(d.get('tool_calls',[]),ensure_ascii=False)
 ids.update(re.findall(r'\b\d{4,10}\b',evidence+c['question']))
 rows.append({'inputs':{'request':c['question'],'reference_evidence':json.dumps({'frozen_reference':c['reference_evidence'],'actual_retrieved_evidence':d.get('tool_calls',[])},ensure_ascii=False)},'outputs':{'response':d.get('answer') or '[NO COMPLETED ANSWER]'},'expectations':{'expected_facts':c['expected_facts'],'allowed_identifiers':sorted(ids),'completed':d['completed'],'tool_execution_observed':d['tool_execution_observed']}})
(B/'answers-production.json').write_text(json.dumps(rows,indent=2))
print('Assembled',len(rows),'answers;',sum(x['expectations']['completed'] for x in rows),'completed')
