from pathlib import Path
import os,sys,json,hashlib
W=Path(__file__).parent
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/report-context-revision')
os.chdir(W);sys.path.insert(0,str(W.parent/'.submission-databricks-review/python-deps'));sys.path.insert(0,str(R))
import truststore;truststore.inject_into_ssl()
from paired_evaluation import read,save,answer,reference
from deployed_grader import diagnostic
case=next(c for c in read(R/'cases.json') if c['id']=='E01-gap')
out=R/'paired-final';out.mkdir(exist_ok=True)
if not (out/'E01-gap-reference.json').exists():save(out/'E01-gap-reference.json',reference(case))
for arm in ['plain','mcp']:
 path=out/('E01-gap-'+arm+'.json')
 if not path.exists():save(path,answer(case,arm))
 assert read(path)['completed'],arm
 print('Paired report-context pilot '+arm+' captured',flush=True)
for arm in ['plain','mcp']:
 d=read(out/('E01-gap-'+arm+'.json'))
 diagnostic({'case_id':'E01-gap','arm':arm,'question':case['question']},{'answer':d['answer']},{'criteria':case['criteria']})
d=read(out/'E01-gap-mcp.json');g=read(out/'E01-gap-mcp-judge.json')['judgment']
brief=next(c['result'] for c in d['calls'] if c['tool']=='medication_evidence_brief')
outcome=next(a for a in brief['evidence_axes'] if a['axis']=='fetal_infant_outcomes')['by_ingredient'][0]
context=outcome['report_only_context']
assert context and not context[0]['confirmed_clinical_outcomes']
observation={'case':'E01-gap','paired_answers_reused_in_final_run':2,'completed':True,
 'raw_fidelity':g['fidelity_status'],'raw_task_fulfilled':g['task_fulfilled'],
 'report_only_context_retrieved':bool(context),'outcome_items_empty':not bool(outcome['items']),
 'answer_mentions_faers':'faers' in d['answer'].casefold(),
 'reported_terms_retained':context[0]['reported_terms'],
 'answer_sha256':hashlib.sha256(d['answer'].encode()).hexdigest(),
 'scores_not_overridden':True,'same_v2_grader':True,'clinical_validation':False}
save(R/'pilot-paired-observation.json',observation)
print(json.dumps({k:v for k,v in observation.items() if k!='reported_terms_retained'},indent=2),flush=True)
