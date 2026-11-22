"""Bounded repair of invalid attribution; never turn a failed grade into a pass in code."""
import json
from grader_contract import VERSION,JUDGE_PROMPT,fingerprint,validate_judgment,candidate_citations,resolve_citation_ids

class GraderContractError(RuntimeError):
    def __init__(self,attempts):
        super().__init__('Grader did not produce a valid grounded assessment within three attempts')
        self.attempts=attempts

def judge(payload,model_call,model):
    wire={'REQUEST':{'question':payload['question'],'criteria':payload['criteria']},
          'REFERENCE_EVIDENCE':payload['reference_evidence'],'CANDIDATE_ANSWER':payload['answer'],
          'CANDIDATE_CITATIONS':candidate_citations(payload['answer'])}
    messages=[{'role':'system','content':JUDGE_PROMPT},{'role':'user','content':json.dumps(wire,ensure_ascii=False)}]
    attempts=[]
    for index in range(3):
        response=model_call(messages,judge=True)
        raw=response['choices'][0]['message']['content']
        try:
            result,binding_errors=resolve_citation_ids(json.loads(raw),payload)
            errors=binding_errors+validate_judgment(result,payload)
        except (json.JSONDecodeError,TypeError):
            result=None;errors=['response must be complete valid JSON']
        attempts.append({'attempt':index+1,'raw_model_text':raw,'validation_errors':errors,'usage':response.get('usage')})
        if not errors:
            return {'judgment':result,'judge_model':model,'grader_version':VERSION,
                    'grading_input_sha256':fingerprint(payload,model),'grounding_validated':True,
                    'attempts':attempts,'accepted_attempt':index+1,'usage':response.get('usage'),
                    'independent_clinician_review':False}
        messages.extend([{'role':'assistant','content':raw},
                         {'role':'user','content':json.dumps({'VALIDATION_ERRORS':errors,
                          'instruction':'Re-read the original candidate and references. Return a complete corrected JSON assessment. Only fix invalid structure/attribution; keep any genuine failure supported by valid quotes or a requested omission. Do not assume a pass is desired.'})}])
    raise GraderContractError(attempts)
