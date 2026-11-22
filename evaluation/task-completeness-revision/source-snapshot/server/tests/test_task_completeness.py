"""Source-completeness regressions; no network or clinical correctness claims."""
import asyncio
import httpx
import pytest
from clients import lactmed, dailymed, reporter
from core.evidence_axes import build_axes
from core.output_notices import format_required_notices


@pytest.mark.parametrize('limit',[500,6000,16000,20000])
def test_long_exposure_section_does_not_crowd_out_other_lactmed_sections(limit):
    sections={h:(h+' source sentence. ')*1000 for h in lactmed.EXPECTED_CLINICAL_SECTIONS}
    out=lactmed.lactmed_payload(sections,limit)
    assert len(out['text'])<=limit
    assert set(out['sections_returned'])==set(sections)
    assert not out['sections_omitted_by_limit']
    assert all(v['truncated'] for v in out['section_status'].values())
    for h,piece in out['sections'].items():
        assert sections[h].startswith(piece) and piece
        assert out['section_status'][h]['characters_returned']==len(piece)


def test_short_sections_return_unused_budget_to_long_sections():
    sections={lactmed.EXPECTED_CLINICAL_SECTIONS[0]:'Brief summary.',lactmed.EXPECTED_CLINICAL_SECTIONS[1]:'X'*3000}
    out=lactmed.lactmed_payload(sections,500)
    assert len(out['text'])==500
    assert out['sections'][lactmed.EXPECTED_CLINICAL_SECTIONS[0]]=='Brief summary.'
    assert not out['section_status'][lactmed.EXPECTED_CLINICAL_SECTIONS[0]]['truncated']
    assert set(out['sections_missing'])==set(lactmed.EXPECTED_CLINICAL_SECTIONS[2:])


def test_too_small_budget_never_emits_a_partial_heading_or_invented_section():
    out=lactmed.lactmed_payload({h:'A source sentence.' for h in lactmed.EXPECTED_CLINICAL_SECTIONS},5)
    assert out['text']=='' and not out['sections']
    assert len(out['sections_omitted_by_limit'])==4


def test_lactation_axes_use_section_boundaries_not_long_exposure_text():
    row={'lactmed':lactmed.lactmed_payload({
        'Drug Levels':'Milk concentration was measured in breastfed infant exposure studies. '*500,
        'Effects on Lactation and Breastmilk':'Maternal prolactin increased.',
        'Effects in Breastfed Infants':'No adverse outcomes were reported.'},500)}
    axes,_=build_axes(row,'lactation');a={x['axis']:x for x in axes}
    assert a['maternal_effects']['items'][0]['text']=='Maternal prolactin increased.'
    assert all('Milk concentration' not in x['text'] for x in a['maternal_effects']['items'])
    assert a['fetal_infant_exposure']['items']


@pytest.mark.parametrize('text',[
    'Lactating women provided milk samples; infant serum concentrations were measured.',
    'Maternal treatment was associated with reported infant outcomes.',
])
def test_offspring_endpoints_do_not_become_maternal_effects(text):
    axes,_=build_axes({'literature':{'articles':[{'pmid':'1','abstract':text}]}},'lactation')
    maternal=next(x for x in axes if x['axis']=='maternal_effects')
    assert not maternal['items'] and maternal['empty_message']


def test_actual_maternal_pk_survives_shared_mother_infant_sentence():
    axes,pk=build_axes({'literature':{'articles':[{'pmid':'1','abstract':'Maternal plasma concentrations and infant serum concentrations were measured.'}]}},'pregnancy')
    assert axes[0]['items'] and pk['items']


def test_planned_trial_measurements_are_context_not_observed_exposure():
    axes,pk=build_axes({'literature':{'articles':[{'pmid':'1','publication_types':['Clinical Trial Protocol'],'abstract':'This study will measure maternal clearance and fetal concentrations.'}]}},'pregnancy')
    assert not axes[0]['items'] and not axes[1]['items']
    assert axes[1]['context_only'][0]['study_context']=='protocol_not_results'
    assert pk['no_data_found']


def test_label_tool_retains_adult_and_population_sections_from_same_spl(monkeypatch):
    xml='<document xmlns="urn:hl7-org:v3"><section><title>8.2 Lactation</title><text>Lactation warning.</text></section><section><title>6 Adverse reactions</title><text>Adult adverse finding.</text></section><section><title>5 Warnings and precautions</title><text>'+('W'*4100)+'</text></section></document>'
    async def request(method,url,**kwargs):
        return httpx.Response(200,text=xml) if url.endswith('.xml') else httpx.Response(200,json={'data':[{'setid':'same-source','title':'Selected product'}]})
    monkeypatch.setattr(dailymed.http,'request',request)
    out=asyncio.run(dailymed.dailymed_label('medicine'))
    assert out['sections']['lactation']=='Lactation warning.'
    assert out['medicine_taker_sections']['adverse_reactions']['text']=='Adult adverse finding.'
    assert out['medicine_taker_sections']['warnings_and_precautions']['truncated']
    assert 'boxed_warning' in out['medicine_taker_sections_missing']
    assert out['medicine_taker_sections_truncated']
    assert out['setid']=='same-source'


@pytest.mark.parametrize('complete',[True,False])
def test_absent_requested_year_count_is_explicit_and_portfolio_unknown_when_capped(monkeypatch,complete):
    async def page(criteria,offset,n):
        return [{'appl_id':1,'project_num':'P1','core_project_num':'P','fiscal_year':2025,'ic_code':'HD','institute':'NICHD','award_amount_usd':12,'direct_cost_usd':8}],{'total':1 if complete else 20}
    monkeypatch.setattr(reporter,'reporter_page',page)
    out=asyncio.run(reporter.research_portfolio('topic','HD',[2024,2025],max_projects=1))
    g=next(x for x in out['groups'] if x['fiscal_year']==2024)
    assert g['project_records']==0 and g['distinct_core_projects']==0
    assert all(x is None for x in g['totals_usd'].values())
    assert g['portfolio_project_records']==(0 if complete else None)
    assert len(out['requested_year_coverage'])==2 and out['retrieved_project_records']==1
    assert next(x for x in out['groups'] if x['fiscal_year']==2025)['totals_usd']['award_amount_usd']==12


def test_any_ic_does_not_invent_an_administering_institute_for_empty_year(monkeypatch):
    async def page(*args):return [],{'total':0}
    monkeypatch.setattr(reporter,'reporter_page',page)
    out=asyncio.run(reporter.research_portfolio('topic',fiscal_years=[2024,2024]))
    assert out['groups']==[] and len(out['requested_year_coverage'])==1
    assert out['requested_year_coverage'][0]['retrieved_project_records']==0


def test_faers_population_notice_survives_empty_model_caveats_but_not_policy_stop():
    answer,ids=format_required_notices('Captured report counts.',['get_adverse_event_signals'])
    assert 'faers_population_scope' in ids and 'cannot be generalized to all infants' in answer
    assert format_required_notices('Fixed stop.',['get_adverse_event_signals'],blocked=True)==('Fixed stop.',[])
