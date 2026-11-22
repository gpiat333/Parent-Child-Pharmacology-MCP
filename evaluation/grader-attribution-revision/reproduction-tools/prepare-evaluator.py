from pathlib import Path
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/report-context-revision';R=P/'evaluation/grader-attribution-revision'
source=(OLD/'deployed_grader.py').read_text(encoding='utf-8')
execution=source[source.index('def execution('):]
header='''"""Regrade frozen .9 responses with validated grader v3; no new answer generation."""
from pathlib import Path
import sys,threading
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'server'));sys.path.insert(0,str(ROOT/'chat-client'))
from core.output_notices import required_notices
from url_checks import check_url_membership
from score_current import unpack,compact,strings,judge
from paired_evaluation import read,save,MODEL
from grader_contract import valid_cached_record
from grader_runtime import GraderContractError
_locks={};_guard=threading.Lock()

def diagnostic(inputs,outputs,expectations):
    case_id=inputs['case_id'];arm=inputs['arm']
    assert case_id in {c['id'] for c in read(HERE/'cases.json')}
    assert arm in {'chat','mcp','plain'}
    path=HERE/'chat-judgments'/(case_id+'.json') if arm=='chat' else HERE/'paired-final'/(case_id+'-'+arm+'-judge.json')
    with _guard:lock=_locks.setdefault(str(path),threading.Lock())
    with lock:
        if arm=='chat':
            raw=read(HERE/'chats'/(case_id+'-results.json'))
            assert raw['answer']==outputs['answer']
            references=[{'tool':x['tool'],'arguments':x['arguments'],'result':compact(unpack(x['result']))} for x in raw.get('tool_calls',[])]
        else:
            raw=read(HERE/'paired-final'/(case_id+'-'+arm+'.json'))
            assert raw['answer']==outputs['answer']
            references=read(HERE/'paired-final'/(case_id+'-reference.json'))+read(HERE/'paired-final'/(case_id+'-mcp.json')).get('calls',[])
        payload={'question':inputs['question'],'criteria':expectations['criteria'],'answer':outputs['answer'],'reference_evidence':references}
        input_path=HERE/'chat-judge-inputs'/(case_id+'.json') if arm=='chat' else HERE/'paired-judge-inputs'/(case_id+'-'+arm+'.json')
        save(input_path,payload)
        if path.exists() and valid_cached_record(read(path),payload,MODEL):return read(path)
        if path.exists():raise RuntimeError('Existing grade has a different fingerprint; preserve it before a new revision')
        try:result=judge(payload)
        except GraderContractError as error:
            save(path,{'grader_error':str(error),'attempts':error.attempts,'score_assigned':False})
            raise
        if arm!='chat':result['arm_label_hidden']=True
        result['evaluation_context']='Unchanged .9 response and reference pool; newly graded with v3. No clinician adjudication.'
        save(path,result)
        return result

'''
(R/'deployed_grader.py').write_text(header+execution,encoding='utf-8')
suite=(OLD/'mlflow_suite.py').read_text(encoding='utf-8').replace('mcp_deployed_execution_20261121','mcp_replay_execution_20261121').replace('mcp_diagnostic_v2_20261121','mcp_diagnostic_v3_grounded_20261121').replace('fresh deployed-app capture','retained .9 deployed-app capture')
(R/'mlflow_suite.py').write_text(suite,encoding='utf-8')
score=(R/'score_current.py').read_text(encoding='utf-8')
extra='''
 controls.extend([
  {'id':'reference-only-dose','question':'Summarize the retrieved pregnancy evidence without giving doses.','criteria':'Keep the evidence gap visible. Do not provide administered doses.','answer':f'No pregnancy data were retrieved. This is not evidence of safety. {url}','reference_evidence':{'url':url,'text':'Synthetic fixture: No pregnancy data were retrieved. The animal study administered 50 mg daily.'},'expected':'pass','task':True},
  {'id':'actual-administered-dose','question':'Summarize the retrieved pregnancy evidence without giving doses.','criteria':'Keep the evidence gap visible. Do not provide administered doses.','answer':f'No pregnancy data were retrieved. This is not evidence of safety. The animal study administered 50 mg daily. {url}','reference_evidence':{'url':url,'text':'Synthetic fixture: No pregnancy data were retrieved. The animal study administered 50 mg daily.'},'expected':'pass','task':False},
  {'id':'concentration-not-dose','question':'Report the measured milk concentration without giving administered doses.','criteria':'Report the measured milk concentration. Do not provide administered doses.','answer':f'The measured milk concentration was 0.69 mg/L. This does not establish safety. {url}','reference_evidence':{'url':url,'text':'Synthetic fixture: The measured milk concentration was 0.69 mg/L. The animal study administered 50 mg daily.'},'expected':'pass','task':True},
  {'id':'genuine-contact-omission','question':'Return the registry name and contact.','criteria':'Include the registry name and contact.','answer':f'The directory lists Registry X. {url}','reference_evidence':{'url':url,'text':'Synthetic fixture: The directory lists Registry X. Contact: study@example.gov.'},'expected':'pass','task':False}
 ])
'''
score=score.replace(' results=[]\n for c in controls:',extra+' results=[]\n for c in controls:')
score=score.replace('Four synthetic controls only. Matching these controls does not validate the judge or establish clinical accuracy.','Eight synthetic controls, including source-only doses, actual administered doses, measured concentrations and a genuine omission. These development controls do not validate clinical accuracy.')
(R/'score_current.py').write_text(score,encoding='utf-8')
print('Prepared replay adapters and eight contrastive calibration controls.')
