from pathlib import Path
from datetime import datetime,timezone
import json,sys,importlib.metadata as metadata
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/report-context-revision'
sys.path.insert(0,str(W.parent/'.submission-databricks-review/python-deps'));sys.path.insert(0,str(R))
from score_current import unpack
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
checks=[]
def capture(cid):return read(R/'chats'/(cid+'-results.json'))
def results(cid):return [(x['tool'],unpack(x['result'])) for x in capture(cid)['tool_calls']]
def check(name,passed,detail):
 checks.append({'check':name,'passed':bool(passed),'detail':detail})
 if not passed:raise AssertionError(name)
r1=next(r for tool,r in results('R01') if tool=='get_lactmed_record')
check('LactMed exposes all source section roles',set(r1['sections'])==set(r1['sections_found']),{'returned':r1['sections_returned'],'missing':r1['sections_missing'],'truncated':r1['truncated']})
r3s=results('R03')
label=next((r['medicine_taker_label_evidence'] for tool,r in r3s if tool=='get_parent_medication_info'),None)
if label:
 check('Adult and population label sections retained together','adverse_reactions' in label['sections'] and 'lactation' in label['population_sections'],{'setid':label['setid'],'adult_sections':list(label['sections']),'population_sections':list(label['population_sections'])})
else:
 label=next(r for tool,r in r3s if tool=='get_label_sections')
 check('Adult and population label sections retained together','adverse_reactions' in label['medicine_taker_sections'] and 'lactation' in label['sections'],{'setid':label['setid'],'adult_sections':list(label['medicine_taker_sections']),'population_sections':list(label['sections'])})
r12=next(r for tool,r in results('R12') if tool=='get_adverse_event_signals')
check('FAERS subset cannot generalize',r12['report_count_interpretation']['generalizable_to_all_infants'] is False and 'faers_population_scope' in capture('R12')['required_notice_ids'] and 'cannot be generalized to all infants' in capture('R12')['answer'],{'cohort_scope':r12['cohort_scope'],'notice_ids':capture('R12')['required_notice_ids']})
brief=next(r for tool,r in results('D05-brief') if tool=='medication_evidence_brief')
maternal=brief['ingredient_evidence'][0]['lactmed']
check('Long LactMed brief retains maternal section','Effects on Lactation and Breastmilk' in maternal['sections_returned'],{'returned':maternal['sections_returned'],'omitted':maternal['sections_omitted_by_limit'],'section_status':maternal['section_status']})
portfolio=next(r for tool,r in results('P01-portfolio') if tool=='summarize_research_portfolio')
requested=set(portfolio['query_criteria']['fiscal_years'])
check('Every requested year has an explicit count',set(x['fiscal_year'] for x in portfolio['requested_year_coverage'])==requested and all(isinstance(x['retrieved_project_records'],int) for x in portfolio['requested_year_coverage']),{'year_coverage':portfolio['requested_year_coverage'],'complete_result_set':portfolio['complete_result_set']})
check('Capped empty years do not claim zero full portfolio',portfolio['complete_result_set'] or all(x['portfolio_project_records'] is None for x in portfolio['requested_year_coverage']),{'retrieved':portfolio['retrieved_project_records'],'total_matching':portfolio['total_matching_records']})
out={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':len(checks),'source':'Selected current-run captures from the unchanged 28-case benchmark.','scope':'Structural source/display contracts, not clinical validation or a separate answer score.'}
(R/'task-completeness-observation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
env={'python':sys.version,'platform':sys.platform,'packages':{n:metadata.version(n) for n in ['mlflow','databricks-sdk','truststore','httpx','jsonschema']},'model_identifier':'system.ai.gpt-5-6-luna','driver':'Local; app, model gateway and MLflow tracking in Databricks','grader_prompt':'Unchanged v2, same as preceding Databricks run','unit_test_environment':'Existing pinned local locked-venv; separate from MLflow evaluator'}
(R/'evaluation-environment.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
print(json.dumps({'checks_passed':len(checks),'clinical_validation':False},indent=2))
