import asyncio,csv,io,json,sqlite3
from pathlib import Path
import pytest
from mc import mprint_data as m, sources
from mc.mprint_outcomes import parse_outcomes,normalize_pmid
from test_mprint_data import data

@pytest.mark.parametrize('value,expected',[('123.0','123'),('123','123'),('123.00','123'),('123.5',None),('1e3',None),('nan',None),('',None)])
def test_pmid_normalization(value,expected):assert normalize_pmid(value)==expected


def test_outcomes_keep_zero_units_null_and_context():
    header=['PMID','Outcomes','Value','Unit','_source_file','_source_folder','_row_index','Exposure','Interval low','Interval high']
    f=io.StringIO();w=csv.writer(f);w.writerow(header);w.writerow(['123.0','Event',0,'percent','workbook','curator',8,'exposed','',4])
    r=list(parse_outcomes(f.getvalue().encode(),'PE_CT'))[0]
    assert r['pmid']=='123' and r['source_fields']['Value']=='0'
    assert r['source_fields']['Unit']=='percent' and r['source_fields']['Interval low'] is None
    assert r['source_row']==2 and r['curation_workbook']=='workbook'


def test_outcome_schema_drift():
    with pytest.raises(ValueError,match='schema'):list(parse_outcomes(b'wrong\nvalue','PE_CT'))

@pytest.mark.parametrize('label,group,expected',[('Maternal','pregnancy',False),('Non-pregnant adults','pregnancy',False),('Maternal/lactation/infant','lactation',True),('Maternal/lactation/infant','pediatric',True),('Postpartum','pregnancy',False),('3rd trimester','pregnancy',True)])
def test_population_filters(label,group,expected):assert m.population_matches(label,group)==expected

@pytest.mark.parametrize('text,expected',[('PK/PD',['PK','PD']),('RCT',['CT','RCT']),('clinical trial / pharmacoepidemiology',['PE','CT']),('popPK modelling',['PK'])])
def test_type_labels(text,expected):assert m.study_codes(text)==expected


def test_gold_population_and_type_filter(data):
    assert m._gold('Drugone',10,'pregnancy')['matching_records']==0
    r=m._gold('Drugone',10,'maternal','PK');assert r['matching_records']==1
    assert r['results'][0]['study_type_labels']==['pharmacokinetics']


def test_brand_resolution_and_no_identifier_equivalence(data,monkeypatch):
    async def normalize(name):return {'found':True,'requires_confirmation':False,'ingredients':['drugone'],'rxcui':'999'}
    monkeypatch.setattr(sources,'rxnorm_normalize',normalize)
    r=asyncio.run(m.search_gold('Brand',resolve_names=True))
    assert r['matching_records']==1 and r['results'][0]['matched_names']==['drugone']
    assert 'NOT equated' in r['resolution']['mapping_method']


def test_ambiguous_identity_not_silently_expanded(data,monkeypatch):
    async def normalize(name):return {'found':True,'requires_confirmation':True,'ingredients':['drugone']}
    monkeypatch.setattr(sources,'rxnorm_normalize',normalize)
    r=asyncio.run(m.search_gold('Typo',resolve_names=True));assert r['requires_confirmation'] and not r['results']


def test_resolver_outage_literal_fallback(data,monkeypatch):
    async def normalize(name):raise RuntimeError('upstream details')
    monkeypatch.setattr(sources,'rxnorm_normalize',normalize)
    r=asyncio.run(m.search_gold('Drugone',resolve_names=True))
    assert r['matching_records']==1 and r['resolution']['status']=='lookup_unavailable'
    assert 'upstream details' not in json.dumps(r)


def test_outcome_join_requires_workbook_and_folder_and_paging(data,tmp_path,monkeypatch):
    con=sqlite3.connect(m.DATABASE);payload=json.loads(con.execute('select payload from gold').fetchone()[0]);payload.update(curation_workbook='correct',curation_folder='folder')
    con.execute('update gold set payload=?',(json.dumps(payload),));con.commit();con.close()
    monkeypatch.setattr(m,'OUTCOMES_DATABASE',tmp_path/'mprint-outcomes.sqlite')
    o=sqlite3.connect(tmp_path/'mprint-outcomes-1.sqlite');o.execute('CREATE TABLE outcomes(pmid TEXT,kind TEXT,source_file TEXT,source_row INTEGER,curation_workbook TEXT,curation_folder TEXT,payload TEXT)')
    o.executemany('INSERT INTO outcomes VALUES(?,?,?,?,?,?,?)',[('123','PE_CT','gold/PE/outcomes.csv',2,'correct','folder','{"Value":"0","Unit":"percent"}'),('123','PE_CT','gold/PE/outcomes.csv',3,'different','folder','{"Value":"7"}')]);o.commit();o.close()
    a=asyncio.run(m.gold_outcomes('123',max_results=1));b=asyncio.run(m.gold_outcomes('123',max_results=1,offset=a['next_offset']))
    assert a['matching_rows']==2 and a['results'][0]['study_context_matched']
    assert not b['results'][0]['study_context_matched'] and b['next_offset'] is None
    assert a['results'][0]['source_fields']['Value']=='0'
