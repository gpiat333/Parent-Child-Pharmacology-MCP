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
from .dailymed import parse_medicine_taker_sections

def parse_parent_sections(xml):
    return parse_medicine_taker_sections(xml)

async def medication_info(drug):
    drug=term(drug)
    if identity_is_vague(drug):return {'source':'validation','requires_confirmation':True,'note':'Exact medicine name and formulation required; appearance is insufficient.'}
    identity=await src.rxnorm_normalize(drug)
    if not identity.get('found') or identity.get('requires_confirmation'):
        return {'source':'live:rxnorm','identity':identity,'requires_confirmation':True,'note':'Confirm the medicine before retrieving clinical evidence.'}
    # Do not silently reduce a combination product to its first ingredient.
    if len(identity.get('ingredients',[]))!=1:
        from tools.composite import medication_evidence_brief
        return await medication_evidence_brief(drug,'lactation')
    async def label():
        response=(await http.request('GET',src.DAILYMED+'/spls.json',params={'drug_name':drug,'pagesize':1},ttl=3600)).json()
        data=response.get('data',[])
        if not data:return {'available':False,'url':'https://dailymed.nlm.nih.gov/','note':'No selected product label.'}
        r=data[0];xml=await http.request('GET',src.DAILYMED+'/spls/'+r['setid']+'.xml',ttl=3600)
        from .dailymed import label_provenance,parse_dailymed_sections
        from .pllr import parse_pllr
        sections=parse_parent_sections(xml.text)
        pllr=parse_pllr(xml=xml.text)
        population_sections=parse_dailymed_sections(xml.text)
        full_population_sections=parse_dailymed_sections(xml.text,max_chars=len(xml.text)+1)
        return {'product_title':r['title'],'setid':r['setid'],'sections':sections,
                'population_sections':population_sections,
                'population_sections_missing':[k for k in ['pregnancy','lactation','pediatric_use'] if k not in population_sections],
                'population_sections_truncated':{k:len(full_population_sections.get(k,''))>len(v) for k,v in population_sections.items()},
                'population_section_scope':'Pregnancy/lactation/pediatric sections from this same label. A warning in lactation text is not an observed infant outcome.',
                **label_provenance(xml.text,r,total=response.get('metadata',{}).get('total_elements')),
                'sections_found':list(sections),'sections_expected':['adverse_reactions','warnings','warnings_and_precautions','boxed_warning','drug_interactions'],
                'sections_missing':[k for k in ['adverse_reactions','warnings','warnings_and_precautions','boxed_warning','drug_interactions'] if k not in sections],
                'missing_section_notice':'Some sections may not apply or may be absent in the source; extraction is not proof of absence.',
                'truncated':any(v['truncated'] for v in sections.values()),
                'source_balance_context':{'disease_associated_risk':pllr.get('clinical_consideration_topics',{}).get('disease_associated_risk'),
                    'notice':'Retain relevant source disease/treatment context when describing adverse findings. Missing context is unknown, not reassurance.'},
                'url':'https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid='+r['setid'],
                'product_match_confirmed':False,'note':'One matching label; confirm formulation and product. Listed effects apply to the label population, not automatically a breastfed infant.'}
    async def lactmed():
        rows=await src.lactmed_search(identity['ingredients'][0],3)
        if not rows:return {'available':False,'url':'https://www.ncbi.nlm.nih.gov/books/NBK501922/'}
        # Return candidates, not a guessed matching record when several are listed.
        if len(rows)!=1:return {'candidates':rows,'requires_record_selection':True,'note':'Select the matching ingredient record before summarizing infant effects.'}
        return await src.lactmed_record(str(rows[0]['id']),16000)
    results=await asyncio.gather(label(),lactmed(),src.medlineplus_drug(identity['rxcui']),return_exceptions=True)
    keys=['medicine_taker_label_evidence','breastfeeding_evidence','patient_education_links']
    evidence={k:({'available':False,'error':'source_unavailable'} if isinstance(v,Exception) else v) for k,v in zip(keys,results)}
    return {'source':'composite:parent-medication-information','identity':identity,**evidence,
            'interpretation':{'medicine_taker':'Label adverse reactions are not automatically infant effects.',
                              'infant':'Use observed infant findings from LactMed; milk concentration alone is not a clinical outcome.',
                              'monitoring':'Source recommendations to monitor are not observations that a symptom occurred. Conversely, a symptom monitored in a study is not a clinical monitoring recommendation. Attribute advice only when explicitly present in the source.',
                              'measurements':'Keep measured milk/infant-serum concentrations separate from observed outcomes and administered dose regimens.'},
            'questions_to_ask_clinician':__import__('core.evidence',fromlist=['clinician_questions']).clinician_questions('lactation'),
            'questions_for_pharmacist':['Does this label match my exact product and formulation?','Which effects are documented in the person taking it versus a breastfed infant?','Which symptoms should prompt professional assessment?'],
            'limitations':['Source text can contain historical doses or treatment directives; do not turn these into personal instructions.',
                            'No diagnosis, dosing, schedule, taper, missed-dose advice or personal safety clearance. Missing sections are not reassuring evidence.']}
