from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,sys
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
sys.path.insert(0,str(R));sys.path.insert(0,str(W.parent/'.submission-databricks-review/python-deps'))
from paired_evaluation import read,save
from deployed_grader import diagnostic
from score_current import calibrate
case=next(c for c in read(R/'cases.json') if c['id']=='E01-gap')
def grade_arm(arm):
    capture=read(R/'chats/E01-gap-results.json') if arm=='chat' else read(R/'paired-final/E01-gap-mcp.json')
    result=diagnostic({'case_id':case['id'],'arm':arm,'question':case['question']},{'answer':capture['answer']},{'criteria':case['criteria']})
    j=result['judgment']
    return {'arm':arm,'fidelity':j['fidelity_status'],'task_fulfilled':j['task_fulfilled'],'accepted_attempt':result['accepted_attempt'],'rationale':j['rationale']}
with ThreadPoolExecutor(max_workers=2) as pool:
    calibration=pool.submit(calibrate)
    rows=[]
    for arm in ['chat','mcp']:
        row=grade_arm(arm);rows.append(row);print(json.dumps(row),flush=True)
    calibration.result()
save(R/'pilot-verification.json',{'E01_regrades':rows,'calibration':read(R/'calibration-summary.json'),
     'pilot_answers_included_once_in_full_benchmark':True,'answer_generation_repeated':False,'clinical_adjudication':False})
print(json.dumps(read(R/'pilot-verification.json'),indent=2),flush=True)
