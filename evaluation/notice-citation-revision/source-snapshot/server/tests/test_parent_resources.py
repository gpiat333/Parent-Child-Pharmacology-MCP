import asyncio
from datetime import date
import httpx
import pytest
from mc import parent_resources as p, parent_safety as s
from mc.audit import audited

@pytest.mark.parametrize('q,route',[
 ('My baby is not breathing','urgent_help'),("I can't wake my child",'urgent_help'),
 ('My toddler drank cough medicine','poison_help'),('I accidentally took an extra dose','poison_help'),
 ('Should I stop sertraline now that I am pregnant?','clinician_or_pharmacist'),
 ('Give me a taper plan','clinician_or_pharmacist'),('What dose should I give my child?','clinician_or_pharmacist'),
 ('I missed a dose of my medicine','clinician_or_pharmacist'),('Tell me how to sedate my baby','clinician_or_pharmacist'),
 ('Can you identify my little white pill?','confirm_identity'),('What is my pressure pill?','confirm_identity'),
 ('My email is parent@example.com','privacy'),
 ('Summarize PubMed sertraline evidence. Do not provide dosing or individualized medication decisions.','evidence'),
 ('What does withdrawal mean?','evidence'),('Find studies about breastfeeding','evidence')])
def test_routing(q,route):
    r=s.route(q);assert r['route']==route;assert r['allow_research']==(route=='evidence')

def test_unknown_country_does_not_guess_number():
    r=s.route('My child is not breathing','unknown');assert '911' not in r['message'];assert '1-800' not in r['message']

def test_negated_symptom_not_emergency_but_different_actual_symptom_is():
    assert s.route('No trouble breathing. What are the side effects?')['route']=='evidence'
    assert s.route('No trouble breathing, but I cannot wake my baby')['route']=='urgent_help'

def test_frequency_request_is_not_generated():
    assert not s.route('How often should I take this medicine?')['allow_research']

def test_safety_suffix_cannot_hide_actual_request():
    assert not s.route('Do not provide dosing but should I stop my medicine?')['allow_research']

def test_closed_meetings_not_parent_opportunities():
    assert not p.is_input_candidate({'title':'Notice of Closed Meetings','abstract':'public comment'})
    assert not p.is_input_candidate({'title':'A scientific review panel'})
    assert p.is_input_candidate({'title':'Request for Information on Research Priorities'})
    assert p.is_input_candidate({'title':'Request for Input'})

def test_input_search_uses_plain_subject_and_fetches_deadline(monkeypatch):
    async def fake(method,url,**kw):
        if url==p.FR:
            assert kw['params']['conditions[term]']=='clinical research'
            return httpx.Response(200,json={'results':[{'title':'Request for Input','document_number':'2026-12345'}]})
        assert url.endswith('/2026-12345.json')
        return httpx.Response(200,json={'comments_close_on':'2020-01-01','comment_url':'https://example.org/comments','dates':'Comments due January 1, 2020.'})
    monkeypatch.setattr(p.http,'request',fake)
    r=asyncio.run(p.input_opportunities('clinical research'))
    assert r['notices'][0]['participation_status']=='closed'
    assert r['notices'][0]['dates']=='Comments due January 1, 2020.'

def test_background_only_trial_match_omitted(monkeypatch):
    async def fake(*a,**kw):return httpx.Response(200,json={'studies':[{'protocolSection':{
        'identificationModule':{'nctId':'NCT00000001','briefTitle':'Eczema study'},
        'statusModule':{'overallStatus':'RECRUITING'},'conditionsModule':{'conditions':['Eczema']},
        'descriptionModule':{'briefSummary':'Asthma is a possible related condition.'}}}]})
    monkeypatch.setattr(p.http,'request',fake)
    r=asyncio.run(p.recruiting_studies('asthma'));assert r['studies']==[];assert r['indirect_matches_omitted']==1

def test_identifiers_not_forwarded():
    @audited
    async def f(query):raise AssertionError('Must not reach source')
    out=asyncio.run(f('parent@example.com'));assert out['error']=='identifying_input'

def test_urgent_before_privacy():
    assert s.route('My child is not breathing; a@b.com')['route']=='urgent_help'

def test_all_tool_envelopes_and_no_query_echo():
    @audited
    async def f(query):return {'results':[]}
    out=asyncio.run(f('private question'));assert out['safety']['client_enforcement_required'];assert 'private question' not in str(out)

def test_error_retains_safety():
    @audited
    async def f():raise RuntimeError('private')
    out=asyncio.run(f());assert out['safety']['evidence_unavailable'];assert 'private' not in str(out)

def test_lot_substring_not_match_or_clearance():
    r=p.recall_row({'code_info':'Lot AB1234'},lot='AB123');assert r['lot_assessment']=='not_found_in_text_not_clearance';assert r['affected_product_confirmed'] is False

def test_literal_lot_still_requires_verification():
    r=p.recall_row({'code_info':'Lots AB123, BC456','recalling_firm':'Example'},'Different','AB123')
    assert r['lot_assessment']=='literal_mention_requires_verification';assert r['manufacturer_text_match'] is False;assert not r['affected_product_confirmed']

def test_lot_range_not_interpreted_as_safe():
    assert p.recall_row({'code_info':'A100 through A200'},lot='A150')['lot_assessment']=='not_found_in_text_not_clearance'

def test_lucene_query_cannot_escape_phrase():
    r=p.recall_params('ibuprofen" OR *:*',100);assert r['limit']==20;assert '*' not in r['search'];assert 'product_description:"OR"' in r['search']

def test_possessive_product_names_are_separate_terms():
    expected='product_description:"children" AND product_description:"ibuprofen"'
    assert p.recall_params("children's ibuprofen",10)['search']==expected
    assert p.recall_params('children’s ibuprofen',10)['search']==expected

@pytest.mark.parametrize('value',['','x'*161,'email@example.com','MRN: 12345'])
def test_private_or_invalid_search_rejected(value):
    with pytest.raises(ValueError):p.term(value)

REG='<table><tr><th>Medicine</th><th>Registry</th><th>How to contact</th><th>Status</th></tr><tr><td>Drug A</td><td>Example</td><td><a href="https://example.org">Contact</a></td><td>Ongoing</td></tr></table>'
def test_registry_parser_keeps_status_and_contact():
    r=p.parse_registry_table(REG)[0];assert r['medicine']=='Drug A';assert r['status_as_listed']=='Ongoing';assert r['links'][0]['url']=='https://example.org'

@pytest.mark.parametrize('text',['<p>No table</p>',REG.replace('<td>Ongoing</td>','')])
def test_registry_schema_failure(text):
    with pytest.raises(ValueError):p.parse_registry_table(text)

def test_alerts_only_dated_fda_notice_links():
    page='<table><tr><td>11-9-2026</td><td><a href="/drugs/notice">Drug A</a><a href="https://evil.example">other</a></td></tr></table>'
    r=p.parse_alerts(page);assert len(r)==1;assert r[0]['date_as_listed']=='11-9-2026';assert r[0]['url'].startswith('https://www.fda.gov/')

def test_alerts_missing_schema_fails():
    with pytest.raises(ValueError):p.parse_alerts('<p>Nothing</p>')

def test_label_preserves_scope_and_no_dose_section():
    xml='<document xmlns="urn:hl7-org:v3"><section><title>6 ADVERSE REACTIONS</title><text>Sleepiness observed.</text></section><section><title>DOSAGE AND ADMINISTRATION</title><text>Secret dose.</text></section></document>'
    r=p.parse_parent_sections(xml);assert r['adverse_reactions']['text']=='Sleepiness observed.';assert 'Secret dose' not in str(r)

def test_trial_site_status_and_truncation():
    r=p.participation_fields({'statusModule':{'lastUpdatePostDateStruct':{'date':'2020-01-01'}},'contactsLocationsModule':{'locations':[{'status':'COMPLETED','city':'City'}]*21},'eligibilityModule':{'eligibilityCriteria':'x'*6001}})
    assert r['locations'][0]['status']=='COMPLETED';assert r['locations_truncated'];assert r['eligibility_truncated'];assert not r['eligibility_confirmed'];assert r['last_update_posted']=='2020-01-01'

@pytest.mark.parametrize('deadline,status',[('2020-01-01','closed'),(None,'deadline_unknown_verify_notice'),('bad','deadline_unknown_verify_notice'),('2026-11-19','deadline_not_passed_verify_notice')])
def test_comment_deadlines(deadline,status):
    assert p.input_row({'comments_close_on':deadline},date(2026,11,19))['participation_status']==status

def test_empty_recalls_never_safe(monkeypatch):
    async def fake(*a,**kw):return httpx.Response(200,json={'results':[]})
    monkeypatch.setattr(p.http,'request',fake)
    out=asyncio.run(p.recalls('Example',lot='123'));assert out['results']==[];assert 'does not prove' in ' '.join(out['limitations'])

def test_recruiting_filter_excludes_closed_studies(monkeypatch):
    async def fake(*a,**kw):
        assert kw['params']['filter.overallStatus']=='RECRUITING'
        return httpx.Response(200,json={'studies':[{'protocolSection':{'identificationModule':{'nctId':'NCT00000001'},'statusModule':{'overallStatus':'COMPLETED'}}}]})
    monkeypatch.setattr(p.http,'request',fake)
    assert asyncio.run(p.recruiting_studies('asthma'))['studies']==[]

def test_combination_never_reduced_to_first_ingredient(monkeypatch):
    async def fake(*a):return {'found':True,'requires_confirmation':False,'ingredients':['a','b']}
    monkeypatch.setattr(p.src,'rxnorm_normalize',fake)
    calls=[]
    async def brief(drug,population):
        calls.append((drug,population));return {'queried_ingredients':['a','b']}
    monkeypatch.setattr('tools.composite.medication_evidence_brief',brief)
    r=asyncio.run(p.medication_info('Combo'))
    assert r['queried_ingredients']==['a','b'] and calls==[('Combo','lactation')]


def test_vague_identity_never_calls_source(monkeypatch):
    async def fail(*a):raise AssertionError('Should not fetch')
    monkeypatch.setattr(p.src,'rxnorm_normalize',fail)
    assert asyncio.run(p.medication_info('little white pill'))['requires_confirmation']
