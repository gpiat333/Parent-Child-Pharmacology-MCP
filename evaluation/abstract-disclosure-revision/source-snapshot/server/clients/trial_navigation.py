from core.population import registry_band_matches, BANDS
"""Bounded public-source discovery for parents; no submissions or patient records."""
import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from urllib.parse import urlencode, urljoin, urlsplit
import httpx
from core.http import http
import clients as src
from .nichd import Tree
from core.safety import identity_is_vague, contains_identifiers

RECALLS='https://api.fda.gov/drug/enforcement.json'
RECALL_HELP='https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls'
ALERTS='https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications'
REGISTRIES='https://www.fda.gov/consumers/pregnancy-exposure-registries/list-pregnancy-exposure-registries'
FR='https://www.federalregister.gov/api/v1/documents.json'
DIRECTORIES=[
 {'title':'NIH public involvement','url':'https://www.nih.gov/about-nih/get-involved-nih/public-involvement-nih'},
 {'title':'FDA patient-focused drug development','url':'https://www.fda.gov/drugs/development-approval-process-drugs/cder-patient-focused-drug-development'}]

from .parent_common import now, term, limit, links

def participation_fields(p):
    status=p.get('statusModule',{});elig=p.get('eligibilityModule',{});cl=p.get('contactsLocationsModule',{})
    locations=cl.get('locations',[]);text=elig.get('eligibilityCriteria','')
    return {'eligibility':{k:elig.get(k) for k in ['minimumAge','maximumAge','stdAges','sex','healthyVolunteers']},
            'pediatric_population':pediatric_population(elig),
            'eligibility_text':text[:6000],'eligibility_truncated':len(text)>6000,
            'last_update_posted':status.get('lastUpdatePostDateStruct',{}).get('date'),
            'central_contacts':cl.get('centralContacts',[])[:3],
            'locations':[{k:l.get(k) for k in ['facility','status','city','state','country','contacts']} for l in locations[:20]],
            'locations_truncated':len(locations)>20,'eligibility_confirmed':False,
            'participation_note':'Study team must confirm site recruitment and eligibility; registry status can be stale. No enrollment or recommendation is performed.'}

def age_year_bounds(value):
    """Conservative calendar bounds; unknown strings never mean zero/no limit."""
    m=re.fullmatch(r'(\d{1,6})\s+(years?|months?|weeks?|days?|hours?|minutes?)',str(value or ''),re.I)
    if not m:return None
    number=int(m[1]);unit=m[2].lower().rstrip('s')
    if unit=='year':return (number,number)
    if unit=='month':return (number/12,number/12)
    days=number*{'week':7,'day':1,'hour':1/24,'minute':1/1440}[unit]
    return (days/366,days/365)

def pediatric_population(elig):
    """Population support in registry fields, never eligibility for an individual."""
    minimum=age_year_bounds(elig.get('minimumAge'));maximum=age_year_bounds(elig.get('maximumAge'))
    groups=elig.get('stdAges') or []
    if not isinstance(groups,list):groups=[]
    child='CHILD' in groups;adult=bool(groups) and not child and all(x in ['ADULT','OLDER_ADULT'] for x in groups)
    status='unverified';basis='No conclusive pediatric age metadata'
    if minimum and maximum and minimum[0]>maximum[1]:
        basis='Conflicting minimum and maximum age metadata'
    elif minimum and minimum[0]>=18:
        status='unverified' if child else 'adult_only';basis='Minimum age is at least 18; CHILD flag conflicts' if child else 'Minimum age is at least 18'
    elif (minimum and minimum[1]<18) or (maximum and maximum[1]<18):
        status='unverified' if adult else 'pediatric_included';basis='Adult-only age groups conflict with numeric ages' if adult else 'Numeric age range includes ages below 18'
    elif child:
        basis='CHILD category is present, but numeric pediatric age support is missing or inconclusive'
    elif adult:
        status='adult_only';basis='Registry standard age groups are adult-only'
    return {'status':status,'basis':basis,'individual_eligibility_confirmed':False,
            'scope':'Registry age-field screening, not clinical suitability or enrollment confirmation.'}

def topic_support(topic, fields):
    """Literal retrieval evidence only; deliberately not a semantic suitability score."""
    words=re.findall(r'\w+',topic.lower())
    matches={name:[w for w in words if re.search(r'\b'+re.escape(w)+r'\b',(text or '').lower())]
             for name,text in fields.items()}
    found=set(w for values in matches.values() for w in values)
    return {'method':'literal topic words; synonyms and clinical meaning not assessed',
            'matched_words_by_field':matches,'missing_words':[w for w in words if w not in found],
            'assessment':'literal_topic_support' if words and all(w in found for w in words) else 'indirect_or_unverified',
            'clinical_suitability_confirmed':False}

async def recruiting_studies(topic,population='any',location='',max_results=10):
    topic=term(topic);location=term(location,True)
    extra={'neonate':'neonate OR newborn','infant':'infant','child':'child','adolescent':'adolescent','pregnancy':'pregnancy','lactation':'lactation OR breastfeeding','pediatric':'child OR infant'}.get(population,'')
    params={'query.term':f'{topic} AND ({extra})' if extra else topic,'filter.overallStatus':'RECRUITING','pageSize':20,'format':'json'}
    if location:params['query.locn']=location
    data=(await http.request('GET',src.CTGOV,params=params,ttl=900)).json();rows=[];indirect=0
    excluded_population={'adult_only':0,'unverified':0}
    for study in data.get('studies',[]):
        p=study.get('protocolSection',{});status=p.get('statusModule',{}).get('overallStatus')
        if status!='RECRUITING':continue
        nct=p.get('identificationModule',{}).get('nctId','')
        if not re.fullmatch(r'NCT\d{8}',nct):continue
        conditions=p.get('conditionsModule',{}).get('conditions',[])
        interventions=[i.get('name','') for i in p.get('armsInterventionsModule',{}).get('interventions',[])]
        direct=' '.join([p['identificationModule'].get('briefTitle',''),*conditions,*interventions]).lower()
        if not all(t in direct for t in re.findall(r'\w+',topic.lower())):
            indirect+=1;continue
        if population=='pediatric' or population in BANDS:
            age_match=pediatric_population(p.get('eligibilityModule',{}))
            if not registry_band_matches(p.get('eligibilityModule',{}),population):
                excluded_population[age_match['status'] if age_match['status'] in excluded_population else 'unverified']+=1;continue
        rows.append({'nct':nct,'title':p['identificationModule'].get('briefTitle'),'status':status,
                     'conditions':conditions,'topic_match':'literal words in title, conditions or interventions; not clinical suitability',
                     'study_type':p.get('designModule',{}).get('studyType'),
                     'has_results':study.get('hasResults'),'results_posted':study.get('hasResults'),
                     'results_notice':'Registration or recruitment status does not establish posted results or demonstrated benefit. A missing results flag stays unknown.',
                     'relevance':topic_support(topic,{'title':p['identificationModule'].get('briefTitle',''),'conditions':' '.join(conditions),'interventions':' '.join(interventions)}),
                     'relevance_note':'A condition keyword may describe an outcome or prevention topic rather than treatment of established disease. Review the summary and eligibility; do not imply the study is specifically for the requested condition from a keyword alone.',
                     'summary':p.get('descriptionModule',{}).get('briefSummary','')[:1500],
                     'url':'https://clinicaltrials.gov/study/'+nct,**participation_fields(p)})
    return {'source':'live:clinicaltrials.gov','url':src.CTGOV+'?'+urlencode(params),'queried_at_utc':now(),
            'cache_max_age_seconds':900,'studies':rows[:limit(max_results)],'indirect_matches_omitted':indirect,
            'excluded_population_counts':excluded_population,
            'population_screening':('Only records with explicit numeric pediatric age support are listed; CHILD-only categories without numeric support are withheld and may include eligible studies; adult-only and unverified-age records withheld. Empty results mean no verified pediatric match in this bounded search, not no studies exist.' if population=='pediatric' else 'Numeric source ages must overlap the requested band; missing age bounds are withheld. This is not individual eligibility.' if population in BANDS else 'No pediatric population filter requested.'),
            'more_results_available':bool(data.get('nextPageToken')) or len(rows)>limit(max_results),
            'limitations':['Potential matches, not confirmed eligibility or nearby-site availability. Location search is not distance calculation.',
              'Overall recruitment does not imply that every location recruits. Check each site status and contact the study team. No result does not rule out other studies.',
              'Only first 20 API matches screened; main list requires literal topic words in title, conditions or interventions. Synonyms may be missed.']}
