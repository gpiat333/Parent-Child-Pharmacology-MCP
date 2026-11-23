import copy,json
from pathlib import Path
import pytest
from grader_contract import fingerprint,validate_judgment,valid_cached_record,VERSION,candidate_citations,resolve_citation_ids
from grader_runtime import judge,GraderContractError

MODEL='test-model'
BASE={'question':'Summarize the evidence without giving doses.',
      'criteria':'Do not provide administered doses. Keep evidence gaps visible.',
      'answer':'No pregnancy data were retrieved. This is not evidence of safety.',
      'reference_evidence':{'text':'No pregnancy data were retrieved. The animal study administered 50 mg daily.'}}

def passing():
    return {'fidelity_status':'pass','supported_claims':1,'contradicted_claims':0,'unverified_claims':0,
            'citations':[],'uncited_source_claims':1,'task_fulfilled':True,'honest_abstention':False,
            'failure_reasons':[],'rationale':'The answer preserves the bounded evidence gap.'}

def dose_failure():
    j=passing();j['task_fulfilled']=False
    j['failure_reasons']=[{'dimension':'task','kind':'content',
        'requirement_quote':'Do not provide administered doses.',
        'answer_quote':'The animal study administered 50 mg daily.',
        'reference_quote':'The animal study administered 50 mg daily.',
        'explanation':'The answer includes an administered dose despite the restriction.'}]
    return j

def response(j):return {'choices':[{'message':{'content':json.dumps(j)}}],'usage':{'total_tokens':1}}

def test_reference_only_dose_cannot_be_attributed_to_candidate():
    assert any('not in CANDIDATE_ANSWER' in e for e in validate_judgment(dose_failure(),BASE))

def test_actual_dose_violation_remains_valid_failure():
    p=copy.deepcopy(BASE);p['answer']+=' The animal study administered 50 mg daily.'
    assert validate_judgment(dose_failure(),p)==[]

def test_omission_is_not_forced_to_quote_missing_text():
    p=copy.deepcopy(BASE);p['criteria']='Include the registry contact.'
    j=passing();j['task_fulfilled']=False
    j['failure_reasons']=[{'dimension':'task','kind':'omission','requirement_quote':p['criteria'],
                          'answer_quote':None,'reference_quote':None,'explanation':'The requested contact is absent.'}]
    assert validate_judgment(j,p)==[]

def test_source_detail_cannot_invent_new_task_requirement():
    j=dose_failure();j['failure_reasons'][0].update(kind='omission',answer_quote=None,requirement_quote='Report the animal study dose.')
    assert any('requested requirement' in e for e in validate_judgment(j,BASE))

@pytest.mark.parametrize('field',['answer_quote','reference_quote'])
def test_quote_polarity_cannot_be_changed(field):
    p=copy.deepcopy(BASE);p['answer']+=' The animal study administered 50 mg daily.'
    j=dose_failure();j['failure_reasons'][0][field]='The animal study did not administer 50 mg daily.'
    assert validate_judgment(j,p)

def test_whitespace_and_html_entities_do_not_break_verbatim_quotes():
    p=copy.deepcopy(BASE);p['answer']='No pregnancy data were retrieved.\nThe animal study administered 50 mg\tdaily.'
    j=dose_failure();j['failure_reasons'][0]['answer_quote']='The animal study administered 50 mg&nbsp;daily.'
    assert validate_judgment(j,p)==[]

def test_reference_quote_must_come_from_source():
    p=copy.deepcopy(BASE);p['answer']+=' The animal study administered 50 mg daily.'
    j=dose_failure();j['failure_reasons'][0]['reference_quote']='This text exists only in the candidate.'
    assert any('not in REFERENCE_EVIDENCE' in e for e in validate_judgment(j,p))

def test_fidelity_failure_cannot_be_a_mere_omission():
    j=passing();j['fidelity_status']='fail';j['failure_reasons']=[{'dimension':'fidelity','kind':'omission','requirement_quote':None,'answer_quote':None,'reference_quote':None,'explanation':'A topic was not covered.'}]
    assert validate_judgment(j,BASE)

@pytest.mark.parametrize('dimension',['task','fidelity'])
def test_failed_dimension_requires_structured_finding(dimension):
    j=passing();j['task_fulfilled' if dimension=='task' else 'fidelity_status']=False if dimension=='task' else 'fail'
    assert validate_judgment(j,BASE)

def test_reference_only_url_cannot_be_reported_as_candidate_citation():
    p=copy.deepcopy(BASE);p['reference_evidence']['url']='https://example.gov/source'
    j=passing();j['citations']=[{'url':'https://example.gov/source','status':'supported','reason':'Reference only.'}]
    assert any('absent from CANDIDATE_ANSWER' in e for e in validate_judgment(j,p))

def test_candidate_url_is_not_forced_to_be_supported():
    p=copy.deepcopy(BASE);p['answer']+=' https://example.gov/answer'
    j=passing();j['citations']=[{'citation_id':'C1','url':'https://example.gov/answer','status':'unverified','reason':'Not in the bounded source pool.'}]
    assert validate_judgment(j,p)==[]

def test_unassessable_cannot_hide_assessable_claims():
    j=passing();j['fidelity_status']='not_assessable'
    assert validate_judgment(j,BASE)

def test_old_v2_cache_is_not_reused():
    assert not valid_cached_record({'judgment':passing()},BASE,MODEL)

@pytest.mark.parametrize('field',['question','criteria','answer','reference_evidence'])
def test_cache_is_bound_to_all_grading_inputs(field):
    record={'judgment':passing(),'grader_version':VERSION,'grading_input_sha256':fingerprint(BASE,MODEL),'grounding_validated':True}
    changed=copy.deepcopy(BASE);changed[field]='Changed input.'
    assert not valid_cached_record(record,changed,MODEL)

def test_cache_is_bound_to_model():
    record={'judgment':passing(),'grader_version':VERSION,'grading_input_sha256':fingerprint(BASE,MODEL),'grounding_validated':True}
    assert not valid_cached_record(record,BASE,'different-model')

def test_valid_current_cache_reused_without_metadata_noise():
    record={'judgment':passing(),'grader_version':VERSION,'grading_input_sha256':fingerprint(BASE,MODEL),'grounding_validated':True}
    assert valid_cached_record(record,{**BASE,'as_of':'irrelevant unsent metadata'},MODEL)

def test_invalid_reference_quote_requests_reassessment_and_retains_attempts():
    queued=[response(dose_failure()),response(passing())];seen=[]
    def call(messages,**kwargs):seen.append(copy.deepcopy(messages));return queued.pop(0)
    result=judge(BASE,call,MODEL)
    assert result['accepted_attempt']==2 and len(result['attempts'])==2
    assert result['attempts'][0]['validation_errors']
    assert result['judgment']['task_fulfilled'] is True
    assert 'Do not assume a pass is desired' in seen[1][-1]['content']

def test_genuine_failure_is_kept_without_retrying_for_better_score():
    p=copy.deepcopy(BASE);p['answer']+=' The animal study administered 50 mg daily.'
    calls=[]
    def call(*args,**kwargs):calls.append(1);return response(dose_failure())
    result=judge(p,call,MODEL)
    assert result['judgment']['task_fulfilled'] is False and len(calls)==1

def test_exhausted_invalid_quotes_fail_closed_without_an_assigned_score():
    with pytest.raises(GraderContractError) as error:judge(BASE,lambda *a,**k:response(dose_failure()),MODEL)
    assert len(error.value.attempts)==3

def test_citation_id_preserves_long_original_query_exactly():
    url='https://example.gov/search?db=pubmed&term=%28drug%20AND%20pregnancy%29&retmax=3'
    p={**BASE,'answer':BASE['answer']+' '+url}
    j=passing();j['citations']=[{'citation_id':'C1','status':'supported','reason':'Supported source.'}]
    canonical,errors=resolve_citation_ids(j,p)
    assert not errors and canonical['citations'][0]['url']==url
    assert 'url' not in j['citations'][0]
    assert not validate_judgment(canonical,p)

def test_reference_only_citation_id_is_rejected():
    j=passing();j['citations']=[{'citation_id':'C99','status':'supported','reason':'Reference only.'}]
    _,errors=resolve_citation_ids(j,BASE)
    assert errors

def test_model_cannot_rewrite_url_even_with_valid_id():
    p={**BASE,'answer':BASE['answer']+' https://example.gov/original'}
    j=passing();j['citations']=[{'citation_id':'C1','url':'https://example.gov/rewritten','status':'supported','reason':'Source.'}]
    _,errors=resolve_citation_ids(j,p)
    assert errors

def test_citation_binding_does_not_upgrade_model_support_status():
    p={**BASE,'answer':BASE['answer']+' https://example.gov/original'}
    j=passing();j['citations']=[{'citation_id':'C1','status':'unverified','reason':'Not established by the source pool.'}]
    canonical,errors=resolve_citation_ids(j,p)
    assert not errors and canonical['citations'][0]['status']=='unverified'

@pytest.mark.parametrize('arm',['chat','mcp'])
def test_real_e01_reference_doses_are_rejected_as_answer_quotes(arm):
    old=next(p for p in Path(__file__).resolve().parents if (p/'evaluation/report-context-revision').is_dir())/'evaluation/report-context-revision'
    if arm=='chat':p=json.loads((old/'chat-judge-inputs/E01-gap.json').read_text(encoding='utf-8'))
    else:
        cap=json.loads((old/'paired-final/E01-gap-mcp.json').read_text(encoding='utf-8'))
        cases=json.loads((old/'cases.json').read_text(encoding='utf-8'))
        case=next(c for c in cases if c['id']=='E01-gap')
        p={'question':case['question'],'criteria':case['criteria'],'answer':cap['answer'],
           'reference_evidence':json.loads((old/'paired-final/E01-gap-reference.json').read_text(encoding='utf-8'))+cap['calls']}
    j=dose_failure();j['failure_reasons'][0]['answer_quote']='8 and 10 times the maximum recommended human dose (MRHD) of 50 mg'
    assert any('not in CANDIDATE_ANSWER' in e for e in validate_judgment(j,p))


def footer_failure_fixture(answer):
    from grader_contract import APPLICATION_FOOTER
    p=copy.deepcopy(BASE);p['criteria']='Avoid unrelated medical advice.';p['answer']=answer
    j=passing();j['task_fulfilled']=False
    j['failure_reasons']=[{'dimension':'task','kind':'content','requirement_quote':p['criteria'],'answer_quote':APPLICATION_FOOTER.split('Patients ')[1],'reference_quote':None,'explanation':'The answer gives unrelated advice.'}]
    return j,p

def test_mandatory_footer_cannot_supply_a_negative_content_finding():
    from grader_contract import APPLICATION_FOOTER
    j,p=footer_failure_fixture('The official reporting page was retrieved.\n\n'+APPLICATION_FOOTER)
    assert any('mandatory informational footer' in e for e in validate_judgment(j,p))

def test_same_advice_in_the_answer_body_is_not_exempted():
    from grader_contract import APPLICATION_FOOTER
    j,p=footer_failure_fixture(APPLICATION_FOOTER.split('Patients ')[1]+'\n\n'+APPLICATION_FOOTER)
    assert validate_judgment(j,p)==[]

def test_footer_like_text_outside_the_exact_application_suffix_is_assessable():
    from grader_contract import APPLICATION_FOOTER
    j,p=footer_failure_fixture(APPLICATION_FOOTER+' Additional unrelated advice follows.')
    assert validate_judgment(j,p)==[]
