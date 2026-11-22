from pathlib import Path
import sys
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/brief-routing-revision'
sys.path.insert(0,str(R))
from paired_evaluation import MCP,read,save
m=MCP()
try:
    case=next(x for x in read(R/'cases.json') if x['id']=='E01-gap')
    probes=[('brief',case['question']),('declined','Do not use the evidence brief tool. Please find a pregnancy registry for topiramate.'),('identity','Prepare an evidence brief for my little white pill.')]
    for key,q in probes:
        result=m.call('route_parent_question',{'question':q})
        save(R/'workflow-probes'/(key+'.json'),result)
        if key=='brief':assert result['result']['requested_workflow']['required_tool']=='medication_evidence_brief'
        else:assert 'requested_workflow' not in result['result']
        if key=='identity':assert not result['result']['allow_research']
        print(key,'verified',flush=True)
finally:m.close()
