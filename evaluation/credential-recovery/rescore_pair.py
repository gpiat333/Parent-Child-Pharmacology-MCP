"""Symmetric rubric correction: access abstention is not contradicted by judge evidence."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from paired_evaluation import HERE, ROOT, MODEL, CASE_IDS, JUDGE_PROMPT, model_call, read, save

PROMPT=JUDGE_PROMPT+'''
Calibration correction, applied equally to every answer:
The answer was NOT necessarily given the reference pool or retrieval tools. Statements
such as "I cannot access live records" or "no source was retrieved" describe the
answer's access, not the contents of the database. NEVER count those as contradicted
claims merely because reference evidence is available to you. Treat them as honest
abstention unless the answer itself demonstrably claims and contradicts its own lookup.
Abstention without substantive source claims has fidelity_status=not_assessable and
task_fulfilled=false for a requested lookup. Distinguish source facts from general
lookup caveats. Do not demand quantitative measurements unless the question requires
them. References to a different product, document edition or URL are unverified, not
necessarily false. A citation to a record with some supporting material is not proof
that every associated claim is supported. Mark such mixed citation support unverified.
Use pass only if all substantive source claims are supported. Any contradicted or
unverified source claims mean fail under this strict reference-support criterion.
This measures support in this reference pool, not absolute medical truth.'''

def assess(payload):
    response=model_call([{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(payload)}],judge=True)
    j=json.loads(response['choices'][0]['message']['content'])
    for field in ['supported_claims','contradicted_claims','unverified_claims','uncited_source_claims']:
        assert isinstance(j[field],int) and j[field]>=0
    # Apply the written rubric consistently even if the model's label is inconsistent.
    j['raw_fidelity_label']=j['fidelity_status']
    total=sum(j[k] for k in ['supported_claims','contradicted_claims','unverified_claims'])
    j['fidelity_status']='not_assessable' if total==0 else 'fail' if j['contradicted_claims'] or j['unverified_claims'] else 'pass'
    return {'judgment':j,'judge_model':MODEL,'usage':response.get('usage'),
            'rubric_version':'2','arm_label_hidden':True,'independent_clinician_review':False}

def main():
    out=HERE/'paired-final'
    save(out/'judge-v2-design.json',{'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
        'prompt':PROMPT,'reason':'V1 incorrectly treated plain-model inability statements as contradicted by evaluator-only evidence. V2 fixes this and enforces consistent strict support labels. All ten answers rescored unchanged; V1 retained.',
        'limits':'Small selected sample, same-family model judge, one answer per arm/question. Reference support is not medical truth or independent clinical review.'})
    controls=[
        {'id':'supported','question':'How many participants? Cite the source.','criteria':'State count and cite.',
         'answer':'The source reports 10 participants: https://example.gov/study',
         'reference_evidence':{'url':'https://example.gov/study','participants':10},'expected':'pass'},
        {'id':'contradicted','question':'How many participants? Cite the source.','criteria':'State count and cite.',
         'answer':'The source reports 20 participants: https://example.gov/study',
         'reference_evidence':{'url':'https://example.gov/study','participants':10},'expected':'fail'},
        {'id':'abstention','question':'Look up the current record and summarize it.','criteria':'Provide a verified current record.',
         'answer':'I cannot access live records here, so I cannot verify the current findings.',
         'reference_evidence':{'url':'https://example.gov/study','participants':10},'expected':'not_assessable'},
        {'id':'different_document','question':'Summarize the available record.','criteria':'State a verified source finding.',
         'answer':'A different document reports 20 participants: https://example.gov/other-study',
         'reference_evidence':{'url':'https://example.gov/study','participants':10},'expected':'fail'}]
    calibration=[]
    for c in controls:
        payload={k:v for k,v in c.items() if k not in ['id','expected']};r=assess(payload)
        calibration.append({'id':c['id'],'expected':c['expected'],**r})
        save(out/'calibration-v2.json',calibration)
    jobs=[]
    cases=[c for c in read(ROOT/'evaluation/parent-generalization/cases.json') if c['id'] in CASE_IDS]
    for c in cases:
        arms={a:read(out/(c['id']+'-'+a+'.json')) for a in ['plain','mcp']}
        pool=read(out/(c['id']+'-reference.json'))+arms['mcp']['calls']
        for arm,d in arms.items():
            jobs.append((c['id'],arm,{'question':c['question'],'criteria':c['criteria'],'answer':d['answer'],'reference_evidence':pool}))
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures={executor.submit(assess,payload):(cid,arm) for cid,arm,payload in jobs}
        for future in as_completed(futures):
            cid,arm=futures[future];save(out/(cid+'-'+arm+'-judge-v2.json'),future.result());print(cid,arm,'rescored',flush=True)

if __name__=='__main__':main()
