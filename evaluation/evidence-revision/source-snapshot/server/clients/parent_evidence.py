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

def parse_parent_sections(xml):
    ns={'h':'urn:hl7-org:v3'};codes={'34084-4':'adverse_reactions','34071-1':'warnings','43685-7':'warnings_and_precautions','34066-1':'boxed_warning','34073-7':'drug_interactions'}
    titles={'adverse reactions':'adverse_reactions','warnings':'warnings','warnings and precautions':'warnings_and_precautions','boxed warning':'boxed_warning','drug interactions':'drug_interactions'}
    out={}
    for sec in ET.fromstring(xml).iterfind('.//h:section',ns):
        title=re.sub(r'^[\d.\s]+','',src.text_of(sec.find('h:title',ns))).lower()
        code=sec.find('h:code',ns);key=titles.get(title) or (codes.get(code.get('code')) if not title and code is not None else None)
        text=src.text_of(sec.find('h:text',ns))
        if key and text:out.setdefault(key,{'text':text[:4000],'truncated':len(text)>4000,'interpretation':'Product-label text; not a diagnosis or recommendation for this individual.'})
    return out

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
        data=(await http.request('GET',src.DAILYMED+'/spls.json',params={'drug_name':drug,'pagesize':1},ttl=3600)).json().get('data',[])
        if not data:return {'available':False,'url':'https://dailymed.nlm.nih.gov/','note':'No selected product label.'}
        r=data[0];xml=await http.request('GET',src.DAILYMED+'/spls/'+r['setid']+'.xml',ttl=3600)
        return {'product_title':r['title'],'setid':r['setid'],'sections':parse_parent_sections(xml.text),
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
                              'monitoring':'Source recommendations to monitor are not observations that a symptom occurred. Preserve this distinction explicitly.'},
            'questions_to_ask_clinician':__import__('core.evidence',fromlist=['clinician_questions']).clinician_questions('lactation'),
            'questions_for_pharmacist':['Does this label match my exact product and formulation?','Which effects are documented in the person taking it versus a breastfed infant?','Which symptoms should prompt professional assessment?'],
            'limitations':['Source text can contain historical doses or treatment directives; do not turn these into personal instructions.',
                            'No diagnosis, dosing, schedule, taper, missed-dose advice or personal safety clearance. Missing sections are not reassuring evidence.']}
