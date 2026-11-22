"""Count/presence probes only; never clinical triage or a safety score."""
import asyncio,re
from datetime import datetime,timezone
from core.http import http
from .ncbi import _ncbi
from .pubmed import pubmed_search_params
from .lactmed import EXPECTED_CLINICAL_SECTIONS
from .dailymed import DAILYMED
from .clinicaltrials import CTGOV
from .mprint_data import _connection,_base,population_matches

async def pubmed_count(drug,population):
    params=pubmed_search_params(drug,population,0)
    d=(await _ncbi('esearch',**params)).json()['esearchresult']
    return {'source':'PubMed','count':int(d['count']),'present':int(d['count'])>0,'query':params['term'],
        'warnings':d.get('warninglist'),'url':'https://pubmed.ncbi.nlm.nih.gov/',
        'caveat':'Search matches, not verified human outcomes, distinct studies or evidence quality.'}

async def trial_count(drug,population):
    extra={'pregnancy':'pregnancy','lactation':'lactation OR breastfeeding','neonate':'neonate OR newborn','infant':'infant','child':'child','adolescent':'adolescent','pediatric':'children OR infant'}.get(population)
    q=drug+(' AND ('+extra+')' if extra else '')
    p={'query.term':q,'pageSize':1,'countTotal':'true','fields':'NCTId','format':'json'}
    d=(await http.request('GET',CTGOV,params=p,ttl=3600)).json();n=d.get('totalCount')
    return {'source':'ClinicalTrials.gov','count':n,'present':n>0 if n is not None else None,'query':q,'url':'https://clinicaltrials.gov/',
        'caveat':'Registration matches; count does not establish posted results, enrollment, outcomes or confirmed age-band applicability.'}

async def lactmed_count(drug,population):
    if population not in {'lactation','any'}:return {'source':'LactMed','count':None,'present':None,'status':'not_applicable','caveat':'LactMed is lactation-only; it is not pregnancy or general pediatric evidence.'}
    term='"'+drug.replace('"','')+'"[Title] AND lactmed[Book]'
    d=(await _ncbi('esearch',db='books',term=term,retmax=0,retmode='json')).json()['esearchresult'];n=int(d['count'])
    return {'source':'LactMed','count':n,'present':n>0,'query':term,'url':'https://www.ncbi.nlm.nih.gov/books/NBK501922/',
        'caveat':'Title matches only; does not establish clinical section completeness or adequate study evidence.'}

async def label_count(drug):
    d=(await http.request('GET',DAILYMED+'/spls.json',params={'drug_name':drug,'pagesize':1},ttl=86400)).json()
    value=d.get('metadata',{}).get('total_elements');n=int(value) if value is not None else None
    return {'source':'DailyMed','count':n,'present':n>0 if n is not None else bool(d.get('data')),
        'url':'https://dailymed.nlm.nih.gov/','caveat':'Name-matched product labels; count does not establish population-specific sections, current FDA approval or independent evidence.'}

def mprint_count(drug,population):
    tokens=re.findall(r'[^\W_]+',drug.casefold());broad='pediatric' if population in {'neonate','infant','child','adolescent'} else population
    base=_base('gold');count=0;pmids=set();con=_connection()
    try:
        for row in con.execute('SELECT drug,population,pmid FROM gold'):
            words=set(re.findall(r'[^\W_]+',row['drug'].casefold()))
            if tokens and all(t in words for t in tokens) and population_matches(row['population'],broad):count+=1;pmids.add(row['pmid'])
    finally:con.close()
    return {'source':'MPRINT Gold snapshot','count':count,'distinct_pmids':len(pmids),'present':count>0,'snapshot_date':base['retrieved_at_utc'],
        'snapshot_revision':base['dataset_revision'],'url':base['repository_url'],
        'caveat':'Literal drug-name row matches in selected snapshot tables; no name resolution or full portals. Pediatric broad matches do not confirm a narrower requested age band. Rows are not distinct studies.'}

async def evidence_coverage(drug,population):
    names=['PubMed','ClinicalTrials.gov','LactMed','DailyMed','MPRINT Gold snapshot']
    results=await asyncio.gather(pubmed_count(drug,population),trial_count(drug,population),lactmed_count(drug,population),label_count(drug),asyncio.to_thread(mprint_count,drug,population),return_exceptions=True)
    rows=[{'source':name,'count':None,'present':None,'status':'unavailable','error_type':type(value).__name__,'caveat':'Probe failed; not a zero count.'} if isinstance(value,Exception) else value for name,value in zip(names,results)]
    return {'source':'coverage:count_only','drug':drug,'population':population,'sources':rows,'queried_at_utc':datetime.now(timezone.utc).isoformat(),
        'count_only':True,'clinical_triage_performed':False,'full_evidence_retrieved':False,'not_evidence_of_safety':True,
        'notice':'Presence/count navigation only. Counts are not comparable across sources and cannot establish evidence quality, clinical safety or what the studies found. Zero matches may reflect query, indexing, snapshot or population limits.'}
