from pathlib import Path
from datetime import datetime,timezone
import ast,json,hashlib,sys
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/notice-citation-revision';OLD=P/'evaluation/brief-routing-revision'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def constant(path,name):
    return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
checks={'same_case_file':sha(R/'cases.json')==sha(OLD/'cases.json'),'same_grader':constant(R/'paired_evaluation.py','JUDGE_PROMPT')==constant(OLD/'paired_evaluation.py','JUDGE_PROMPT'),'same_paired_system_prompt':constant(R/'paired_evaluation.py','PROMPT')==constant(OLD/'paired_evaluation.py','PROMPT')}
assert all(checks.values())
record={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'cases_sha256':sha(R/'cases.json'),'execution_check_change':'Only URL extraction changes: balanced delimiters separate adjacent Markdown links. Completion, expected routes and required/allowed tool definitions are unchanged. Historical raw scores remain unchanged.','workflow_change':'MCP clients append applicable application-owned portfolio and clinical-review notices after generation. Plain model has no tools or appended notices. Before-notice text is retained.','retry_policy':'Retain incomplete attempts, retry incomplete answers or judgments only. Never regenerate a completed answer to improve its score.','evaluator_files':{n:sha(R/n) for n in ['paired_evaluation.py','score_current.py','cases.json']}}
(R/'run-design-verification.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
sys.path.insert(0,str(R));import score_current as sc
checks_old=sc.read(OLD/'chat-checks.json');results=[]
for row in checks_old:
    if row['expected_stop']:continue
    raw=sc.read(OLD/'chats'/(row['id']+'-results.json'))
    evidence=[{'tool':x['tool'],'arguments':x['arguments'],'result':sc.compact(sc.unpack(x['result']))} for x in raw['tool_calls']]
    new=sc.check_url_membership(raw['answer'],sc.strings(evidence))
    results.append({'case':row['id'],'historical_raw_pass':row['citation_provenance'],'corrected_parser_pass':new['citation_provenance'],'unmatched_urls':new['unmatched_urls']})
assert next(x for x in results if x['case']=='R12')['corrected_parser_pass']
(R/'url-checker-regression.json').write_text(json.dumps({'historical_scores_modified':False,'method':'Same saved answers and tool outputs, corrected extraction only. This does not grade claim support.','old_pass':sum(x['historical_raw_pass'] for x in results),'corrected_pass':sum(x['corrected_parser_pass'] for x in results),'total':len(results),'rows':results},indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
