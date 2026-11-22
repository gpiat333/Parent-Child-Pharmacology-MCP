import asyncio,json
import pytest,httpx
from pydantic import ValidationError
from models.inputs import INPUT_MODELS
from clients import reporter,pubmed,lactmed,dailymed,coverage,shortages,rxnorm,clinicaltrials
from core.source_context import evidence_base
from core.evidence import annotate
from core.evidence_axes import build_axes
from core.audit import audited

@pytest.mark.parametrize('name,valid,bad',[
 ('search_funded_research',{'topic':'pharmacology'},{'ic':'NICHD'}),
 ('search_funded_research',{'topic':'pharmacology'},{'ic':'ZZ'}),
 ('search_funded_research',{'topic':'pharmacology'},{'fiscal_years':[]}),
 ('search_funded_research',{'topic':'pharmacology'},{'fiscal_years':['2025']}),
 ('search_funded_research',{'topic':'pharmacology'},{'fiscal_years':[1800]}),
 ('search_funded_research',{'topic':'pharmacology'},{'activity_code':'K-series'}),
 ('summarize_research_portfolio',{'drug_or_topic':'epilepsy'},{'max_projects':0}),
 ('summarize_research_portfolio',{'drug_or_topic':'epilepsy'},{'max_projects':501}),
 ('search_literature',{'query':'lamotrigine'},{'publication_type':'trial OR anything'}),
 ('search_literature',{'query':'lamotrigine'},{'date_from':'2025-02-30'}),
 ('search_literature',{'query':'lamotrigine'},{'date_from':'2026-01-01','date_to':'2025-01-01'}),
 ('search_trials',{},{}),('search_trials',{'nct_id':'NCT12345678'},{'condition_or_drug':'epilepsy'}),
 ('search_trials',{}, {'nct_id':'https://example.org'}),
 ('find_products_containing_ingredient',{'ingredient':'acetaminophen'},{'max_results':-1}),
 ('check_evidence_coverage',{'drug':'acetaminophen'},{'population':'newbornish'}),
 ('search_drug_shortages',{'drug':'amoxicillin'},{'status':'safe'}),
])
def test_invalid_new_filters_rejected(name,valid,bad):
    with pytest.raises(ValidationError):INPUT_MODELS[name].model_validate({**valid,**bad})

def test_reporter_hd_mapping_exact_reproducible_criteria():
    c=reporter.reporter_criteria('epilepsy','HD',[2024,2025,2025],'R01','JOHNS HOPKINS')
    assert c['agencies']==['NICHD'] and c['is_agency_admin'] is True
    assert c['fiscal_years']==[2024,2025] and c['activity_codes']==['R01']
    assert c['org_names']==['JOHNS HOPKINS'] and c['exclude_subprojects']

def test_portfolio_dedup_and_unknown_amounts_are_not_zero():
    rows=[{'appl_id':1,'fiscal_year':2025,'ic_code':'HD','institute':'NICHD','activity_code':'K12','award_amount_usd':100,'direct_cost_usd':80,'indirect_cost_usd':20},
          {'appl_id':2,'fiscal_year':2025,'ic_code':'HD','institute':'NICHD','activity_code':'R01','award_amount_usd':None,'direct_cost_usd':None,'indirect_cost_usd':None},
          {'appl_id':3,'fiscal_year':2024,'ic_code':'NS','institute':'NINDS','award_amount_usd':None}]
    groups,duplicates=reporter.aggregate_projects(rows+[rows[0]])
    g=next(g for g in groups if g['ic_code']=='HD')
    assert duplicates==1 and g['project_records']==2
    assert g['totals_usd']['award_amount_usd']==100 and g['totals_usd']['direct_cost_usd']==80
    assert g['missing_amount_records']['award_amount_usd']==1
    assert next(g for g in groups if g['ic_code']=='NS')['totals_usd']['award_amount_usd'] is None

def test_portfolio_cap_not_complete(monkeypatch):
    calls=[]
    async def page(c,offset,n):
        calls.append((offset,n));return [{'appl_id':i+offset,'fiscal_year':2025,'award_amount_usd':1} for i in range(n)],{'total':1000}
    monkeypatch.setattr(reporter,'reporter_page',page)
    out=asyncio.run(reporter.research_portfolio('epilepsy',max_projects=150))
    assert calls==[(0,100),(100,50)] and out['complete_result_set'] is False
    assert out['retrieved_project_records']==150 and out['total_matching_records']==1000

@pytest.mark.parametrize('kind,term',[('case_report','Case Reports'),('randomized_controlled_trial','Randomized Controlled Trial'),('systematic_review','Systematic Review'),('meta_analysis','Meta-Analysis'),('observational_study','Observational Study')])
def test_curated_pubmed_filter_keeps_population_and_dates(kind,term):
    p=pubmed.pubmed_search_params('lamotrigine','pregnancy',publication_type=kind,date_from='2020-01-01',date_to='2025-12-31')
    assert term+'"[Publication Type]' in p['term'] and 'Pregnancy' in p['term']
    assert p['mindate']=='2020/01/01' and p['maxdate']=='2025/12/31' and 'reldate' not in p

def test_pmc_identifier_does_not_imply_free_availability(monkeypatch):
    async def ncbi(*a,**kw):return httpx.Response(200,json={'esearchresult':{'idlist':[]}})
    async def request(*a,**kw):return httpx.Response(200,text='<OA><error>not in OA subset</error></OA>')
    monkeypatch.setattr(pubmed,'_ncbi',ncbi);monkeypatch.setattr(pubmed.http,'request',request)
    rows=[{'pmid':'123','pmc_id':'PMC123'}];asyncio.run(pubmed.annotate_availability(rows));a=rows[0]['full_text_availability']
    assert a['pmc_id']=='PMC123' and a['free_full_text_available'] is False
    assert a['open_access_flag'] is None and a['paywall_indicator']=='not_verified'

def test_availability_failure_is_unknown(monkeypatch):
    async def fail(*a,**kw):raise RuntimeError('offline')
    monkeypatch.setattr(pubmed,'_ncbi',fail)
    rows=[{'pmid':'123','pmc_id':None}];asyncio.run(pubmed.annotate_availability(rows))
    assert rows[0]['full_text_availability']['free_full_text_available'] is None

def test_lactmed_inverse_sections_truncation_and_excluded_alternatives():
    sections={'Summary of Use during Lactation':'Context.','Drug Levels':'X'*2000,'Effects in Breastfed Infants':'No adverse effects in three case reports.','Alternate Drugs to Consider':'REPLACEMENT-DRUG'}
    out=lactmed.lactmed_payload(sections,500)
    assert 'Effects on Lactation and Breastmilk' in out['sections_missing']
    assert out['truncated'] and 'Effects in Breastfed Infants' in out['sections_omitted_by_limit']
    assert out['section_status']['Drug Levels']['truncated']
    assert 'REPLACEMENT-DRUG' not in json.dumps(out)
    assert out['alternatives_policy']['handling']=='excluded'

def test_no_effects_does_not_become_well_studied():
    x=evidence_base('Three case reports described no adverse effects in infants.')
    assert x['no_effects_statement_detected'] and x['study_count'] is None
    assert 'case_report' in x['study_types_mentioned']

def test_label_version_effective_date_and_selection_basis():
    xml='<document xmlns="urn:hl7-org:v3"><versionNumber value="7"/><effectiveTime value="20251031"/><author><assignedEntity><representedOrganization><name>Labeler Inc</name></representedOrganization></assignedEntity></author></document>'
    x=dailymed.label_provenance(xml,{'published_date':'Nov 01, 2025'},position=2,fetched=5,total=90)
    assert x['spl_version']=='7' and x['effective_date']=='2025-10-31' and x['labeler']=='Labeler Inc'
    assert x['selection_basis']['total_matching_spls']==90 and not x['selection_basis']['most_recent_effective_date_claimed']
    assert 'in-use' in x['label_currency_notice']

def test_per_item_population_and_source_balance_are_visible():
    row={'lactmed':{'text':'Effects in Breastfed Infants: No adverse effects were reported.','url':'https://example.gov/lactmed','source_balance_context':{'text':'Source treatment context.'}}}
    axes,_=build_axes(row,'lactation');item=axes[2]['items'][0]
    assert item['population_context']['source_population']==['lactation']
    assert not item['population_context']['age_band_confirmed']
    assert item['evidence_base']['study_count'] is None
    assert item['source_balance_context']['text']=='Source treatment context.'
    out=annotate({'population':'neonate','articles':[{'pmid':'1','mesh_terms':['Adolescent']}]})
    context=out['articles'][0]['population_context']
    assert context['requested_population']=='neonate' and context['source_population']==['adolescent'] and not context['matches_requested_population_confirmed']
    assert 'Stopping or changing' in out['continuity_of_care_notice']

def test_coverage_source_failure_is_not_zero(monkeypatch):
    async def zero(*a):return {'count':0,'present':False}
    async def fail(*a):raise RuntimeError('offline')
    monkeypatch.setattr(coverage,'pubmed_count',zero);monkeypatch.setattr(coverage,'trial_count',fail)
    monkeypatch.setattr(coverage,'lactmed_count',zero);monkeypatch.setattr(coverage,'label_count',zero)
    monkeypatch.setattr(coverage,'mprint_count',lambda *a:{'count':0,'present':False})
    out=asyncio.run(coverage.evidence_coverage('drug','pregnancy'))
    assert out['sources'][1]['count'] is None and out['sources'][1]['status']=='unavailable'
    assert out['count_only'] and not out['clinical_triage_performed'] and not out['full_evidence_retrieved']

def test_trial_fetch_by_identifier_and_results_flag(monkeypatch):
    async def request(method,url,**kw):
        assert url.endswith('/NCT12345678')
        return httpx.Response(200,json={'hasResults':False,'protocolSection':{'identificationModule':{'nctId':'NCT12345678'},'statusModule':{'overallStatus':'COMPLETED'}}})
    monkeypatch.setattr(clinicaltrials.http,'request',request)
    row=asyncio.run(clinicaltrials.trial_by_nct('NCT12345678'))
    assert row['status']=='COMPLETED' and row['results_posted'] is False

def test_shortage_status_and_availability_not_conflated(monkeypatch):
    async def request(*a,**kw):return httpx.Response(200,json={'meta':{'last_updated':'2026-11-20'},'results':[{'status':'Current','availability':'Available','dosage_form':'Suspension'}]})
    monkeypatch.setattr(shortages.http,'request',request)
    out=asyncio.run(shortages.search_shortages('amoxicillin'))
    assert out['results'][0]['status']=='Current' and out['results'][0]['availability']=='Available'
    assert 'not local pharmacy stock' in out['caveat']

def test_ingredient_product_lookup_refuses_combination(monkeypatch):
    async def norm(x):return {'found':True,'requires_confirmation':False,'term_type':'MIN','ingredients':['a','b']}
    monkeypatch.setattr(rxnorm,'rxnorm_normalize',norm)
    out=asyncio.run(rxnorm.products_containing_ingredient('combination'))
    assert out['requires_confirmation'] and out['results']==[]

@pytest.mark.parametrize('field',['ingredient','drug_or_topic','drug'])
@pytest.mark.parametrize('question',['I feel hopeless postpartum','My baby swallowed my pills','Puedo tomar sertralina durante la lactancia'])
def test_new_lookup_fields_cannot_bypass_preflight(field,question):
    calls=[]
    namespace={}
    exec('async def lookup('+field+'):\n calls.append('+field+')\n return {"results":[]}',{'calls':calls},namespace)
    out=asyncio.run(audited(namespace['lookup'])(question))
    assert not calls and out['allow_research'] is False
