import asyncio
import json
from urllib.parse import parse_qs,urlsplit
import httpx
import pytest
from mc import sources, mprint_data as m
from test_mprint_data import data


def test_gold_exact_pmid_does_not_need_drug_resolution(data,monkeypatch):
    async def forbidden(*args):raise AssertionError('PMID lookup must not call RxNorm')
    monkeypatch.setattr(sources,'rxnorm_normalize',forbidden)
    out=asyncio.run(m.search_gold(pmid='123',resolve_names=True))
    assert out['source']=='snapshot:mprint:gold'
    assert out['matching_records']==1
    assert out['results'][0]['population']=='Maternal'
    assert out['results'][0]['source_fields']['PMID']=='123'
    assert out['applied_filters']['pmid']=='123'
    assert asyncio.run(m.search_gold(pmid='12'))['matching_records']==0


def test_gold_pmid_and_drug_filters_intersect(data):
    assert asyncio.run(m.search_gold('Drugone',pmid='123'))['matching_records']==1
    assert asyncio.run(m.search_gold('unknown',pmid='123'))['matching_records']==0
    assert asyncio.run(m.search_gold(pmid='123',population='pregnancy'))['matching_records']==0


@pytest.mark.parametrize('pmid',['0','123 OR 1=1','123.0','https://pubmed.ncbi.nlm.nih.gov/123/','12345678901'])
def test_gold_bad_pmid_rejected_before_network(data,monkeypatch,pmid):
    async def forbidden(*args):raise AssertionError('Invalid PMID must not resolve a drug')
    monkeypatch.setattr(sources,'rxnorm_normalize',forbidden)
    assert asyncio.run(m.search_gold('Drugone',pmid=pmid,resolve_names=True))['error']=='invalid_pmid'


def test_pubmed_query_link_preserves_exact_public_request(monkeypatch):
    calls=[]
    async def ncbi(which,**params):
        calls.append((which,params))
        return httpx.Response(200,json={'esearchresult':{'idlist':[]}})
    monkeypatch.setattr(sources,'_ncbi',ncbi)
    query='drug A & B "quoted"'
    assert asyncio.run(sources.pubmed_search(query,'lactation',3))==[]
    url=sources.pubmed_search_url(query,'lactation',3)
    parsed={k:v[0] for k,v in parse_qs(urlsplit(url).query).items()}
    assert parsed=={k:str(v) for k,v in calls[0][1].items()}
    assert 'api_key' not in parsed and 'token' not in url


def test_pubmed_abstract_url_without_inventing_missing_records(monkeypatch):
    xml='<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Study</ArticleTitle><Abstract><AbstractText>Finding.</AbstractText></Abstract></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
    async def ncbi(*args,**kwargs):return httpx.Response(200,text=xml)
    monkeypatch.setattr(sources,'_ncbi',ncbi)
    out=asyncio.run(sources.pubmed_abstracts(['123','456']))
    assert len(out)==1 and out[0]['url']=='https://pubmed.ncbi.nlm.nih.gov/123/'
    assert out[0]['abstract']=='Finding.'


def test_empty_server_pubmed_search_still_cites_query(monkeypatch):
    import server
    async def empty(*args):return []
    monkeypatch.setattr(sources,'pubmed_search',empty)
    out=asyncio.run(server.search_literature.__wrapped__('no-such-drug',mode='keyword',max_results=30))
    assert out['results']==[] and out['source']=='live:pubmed'
    assert parse_qs(urlsplit(out['url']).query)['retmax']==['20']


@pytest.mark.parametrize('original,expected',[
    ('Metformin Hcl 850Mg Tab','Metformin Hcl Tab'),
    ('40 mg MSB11022','MSB11022'),
    ('Empagliflozin 10 MG','Empagliflozin'),
    ('Drug 0.5–1 mg/kg','Drug'),
    ('IL-2 antibody MSB11022','IL-2 antibody MSB11022'),
    ('Placebo oral tablet','Placebo oral tablet'),
])
def test_dose_free_label_does_not_strip_drug_identifiers(original,expected):
    assert sources.intervention_name_without_strength(original)==expected


def test_trial_original_label_retained_with_display_variant(monkeypatch):
    async def request(*args,**kwargs):
        return httpx.Response(200,json={'studies':[{'protocolSection':{
            'identificationModule':{'nctId':'NCT12345678','briefTitle':'Study'},
            'statusModule':{'overallStatus':'COMPLETED'},
            'armsInterventionsModule':{'interventions':[{'name':'40 mg MSB11022','type':'DRUG'}]}
        }}]})
    monkeypatch.setattr(sources.http,'request',request)
    out=asyncio.run(sources.trials_search('trial'))
    assert out[0]['interventions'][0]['name']=='40 mg MSB11022'
    assert out[0]['interventions'][0]['name_without_strength']=='MSB11022'
