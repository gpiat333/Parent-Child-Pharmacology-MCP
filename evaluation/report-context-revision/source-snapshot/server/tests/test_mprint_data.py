import asyncio,json,sqlite3
import pytest
from mc import mprint_data as m

@pytest.fixture
def data(tmp_path,monkeypatch):
    con=sqlite3.connect(tmp_path/'mprint.sqlite')
    con.executescript('CREATE TABLE gold(pmid TEXT, drug TEXT, population TEXT, study_type TEXT, payload TEXT); CREATE TABLE silver(pmid TEXT,study_type TEXT,source_row INTEGER);')
    con.execute('INSERT INTO gold VALUES(?,?,?,?,?)',('123','Drugone / drugtwo','Maternal','PK',json.dumps({'source_file':'gold/PK/example.csv','source_row':2,'PMID':'123','Population':'Maternal'})))
    con.executemany('INSERT INTO silver VALUES(?,?,?)',[('123','PK',2),('123','CT',3),('456','Biomarker',4)])
    con.commit();con.close()
    (tmp_path/'mprint-manifest.json').write_text(json.dumps({'revision':'abc123','repository':'https://github.com/langli-lab/mprint-kp-data','retrieved_at_utc':'2026-11-17','scope':'Test subset'}))
    monkeypatch.setattr(m,'DATA',tmp_path);monkeypatch.setattr(m,'DATABASE',tmp_path/'mprint.sqlite')


def test_gold_source_and_combination(data):
    r=asyncio.run(m.search_gold('DRUGONE'))
    assert r['curation']=='expert-curated study metadata'
    assert r['results'][0]['drug_names']=='Drugone / drugtwo'
    assert r['results'][0]['url']=='https://pubmed.ncbi.nlm.nih.gov/123/'
    assert 'abc123' in r['results'][0]['dataset_url']
    assert r['results'][0]['source_row']==2
    item=r['results'][0]
    assert len({k.casefold() for k in item})==len(item)
    assert item['source_fields']['PMID']=='123'

@pytest.mark.parametrize('query',['drug','Maternal','unknown'])
def test_gold_no_false_substring_or_population_match(data,query):
    assert asyncio.run(m.search_gold(query))['matching_records']==0

@pytest.mark.parametrize('query',['','!!!','x'*201])
def test_gold_invalid_input(data,query):
    assert asyncio.run(m.search_gold(query))['error']=='invalid_drug'


def test_silver_multiple_labels_missing_and_dedup(data):
    r=asyncio.run(m.silver_classifications(['123','123','999']))
    assert len(r['results'])==2
    assert [x['study_type'] for x in r['results'][0]['classifications']]==['CT','PK']
    assert r['results'][1]['found'] is False
    assert r['curation']=='automated publication classification'

@pytest.mark.parametrize('ids',[[],['drug'],['0'],['123 OR 1=1'],['123']*21])
def test_silver_validation(data,ids):
    assert asyncio.run(m.silver_classifications(ids))['error']=='invalid_pmids'


def test_database_is_read_only(data):
    con=m._connection()
    try:
        with pytest.raises(sqlite3.OperationalError):con.execute('DELETE FROM gold')
    finally:con.close()


def test_empty_results_still_supply_unambiguous_labels_and_guidance_origin(data):
    result=asyncio.run(m.search_gold('unknown'))
    assert result['matching_records']==0
    assert result['classification_legend']['PE']=='pharmacoepidemiology'
    assert result['classification_legend']['PK']=='pharmacokinetics'
    assert result['classification_legend']['CT']=='clinical trial'
    assert 'MCP implementation' in result['guidance_origin']
