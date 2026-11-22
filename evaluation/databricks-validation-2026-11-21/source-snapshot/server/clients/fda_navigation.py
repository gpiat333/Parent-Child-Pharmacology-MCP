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

def parse_registry_table(page):
    root=Tree(page).root
    for table in (n for n in root.walk() if n.tag=='table'):
        rows=[n for n in table.walk() if n.tag=='tr']
        if not rows: continue
        headers=[n.text().lower() for n in rows[0].children if getattr(n,'tag',None) in ('td','th')]
        if not {'medicine','registry','status'}.issubset(headers): continue
        out=[]
        for row in rows[1:]:
            cells=[n for n in row.children if getattr(n,'tag',None) in ('td','th')]
            if len(cells)!=len(headers): raise ValueError('Registry table shape changed')
            d=dict(zip(headers,[c.text() for c in cells]))
            out.append({'medicine':d['medicine'],'condition':d.get('medical condition'),
                        'registry':d['registry'],'contact_text':d.get('how to contact'),
                        'status_as_listed':d['status'],'links':links(row,REGISTRIES),'url':REGISTRIES})
        return out
    raise ValueError('Expected FDA registry table unavailable')

async def pregnancy_registries(drug='',max_results=10):
    drug=term(drug,True)
    page=await http.request('GET',REGISTRIES,ttl=3600)
    rows=parse_registry_table(page.text)
    tokens=re.findall(r'\w+',drug.lower())
    found=[r for r in rows if all(t in (r['medicine']+' '+(r['condition'] or '')+' '+r['registry']).lower() for t in tokens)]
    return {'source':'live:fda-registry-directory','url':REGISTRIES,'queried_at_utc':now(),
            'cache_max_age_seconds':3600,'results':found[:limit(max_results)],'matches_on_page':len(found),
            'limitations':['FDA lists but does not operate or endorse these registries. The list is not comprehensive.',
              'Status is reproduced from the directory; verify current enrollment directly with the registry. No eligibility determination or automatic contact.']}

def parse_alerts(page):
    rows=[]
    for row in (n for n in Tree(page).root.walk() if n.tag=='tr'):
        cells=[n for n in row.children if getattr(n,'tag',None) in ('td','th')]
        if len(cells)<2 or not re.search(r'\d{1,2}-\d{1,2}-\d{4}',cells[0].text()):continue
        for a in links(cells[1],ALERTS):
            if urlsplit(a['url']).hostname=='www.fda.gov':rows.append({'date_as_listed':cells[0].text(),**a})
    if not rows: raise ValueError('Expected FDA safety communication rows unavailable')
    return rows

async def safety_alerts(drug='',max_results=10):
    drug=term(drug,True);page=await http.request('GET',ALERTS,ttl=900)
    tokens=re.findall(r'\w+',drug.lower());rows=parse_alerts(page.text)
    matches=[r for r in rows if all(t in r['title'].lower() for t in tokens)]
    return {'source':'live:fda-safety-communications','url':ALERTS,'queried_at_utc':now(),
            'cache_max_age_seconds':900,'results':matches[:limit(max_results)],
            'limitations':['Title search of the current FDA index only; does not search full notices or all historical alerts.',
              'Links are notices, not personalized treatment instructions. Open the official notice and consult a pharmacist about your product. No match does not establish safety.']}

def recall_params(drug,n):
    # Remove Lucene operators by allowing only name-like tokens inside a quoted phrase.
    cleaned=re.sub(r"['’]s\b",'',term(drug))
    tokens=re.findall(r'[\w-]+',cleaned)
    if not tokens: raise ValueError('Medicine name required')
    # Match each word, preserving product qualifiers without requiring adjacency.
    search=' AND '.join(f'product_description:"{t}"' for t in tokens)
    return {'search':search,'sort':'report_date:desc','limit':limit(n)}

def recall_row(row,manufacturer='',lot=''):
    code=' '.join(filter(None,[row.get('code_info'),row.get('more_code_info')]))
    match=bool(lot and re.search(r'(?<![\w-])'+re.escape(lot)+r'(?![\w-])',code,re.I))
    fields=['recall_number','recalling_firm','product_description','code_info','more_code_info','reason_for_recall',
            'classification','status','report_date','recall_initiation_date','termination_date','distribution_pattern']
    result={k:row.get(k) for k in fields}
    result.update(lot_assessment='literal_mention_requires_verification' if match else ('not_found_in_text_not_clearance' if lot else 'lot_not_provided'),
                  manufacturer_text_match=manufacturer.casefold() in (row.get('recalling_firm') or '').casefold() if manufacturer else None,
                  affected_product_confirmed=False,
                  instructions='Consumer instructions are not supplied by this enforcement record. Consult the official recall notice or pharmacist; do not infer medication changes.',
                  official_recall_guidance_url=RECALL_HELP)
    identifier=row.get('recall_number')
    if identifier and re.fullmatch(r'[\w-]+',identifier):result['url']=RECALLS+'?'+urlencode({'search':f'recall_number:"{identifier}"'})
    return result

async def recalls(drug,manufacturer='',lot='',max_results=10):
    manufacturer=term(manufacturer,True);lot=term(lot,True)
    params=recall_params(drug,max_results)
    try: data=(await http.request('GET',RECALLS,params=params,ttl=300)).json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code!=404: raise
        data={'results':[]}
    return {'source':'live:openfda-enforcement','url':RECALLS+'?'+urlencode(params),
            'queried_at_utc':now(),'cache_max_age_seconds':300,'dataset_last_updated':data.get('meta',{}).get('last_updated'),
            'results':[recall_row(r,manufacturer,lot) for r in data.get('results',[])],
            'total_matches':data.get('meta',{}).get('results',{}).get('total'),
            'limitations':['Candidate product-name matches only, not bottle-level clearance. Verify formulation, manufacturer, lot and expiration against the official notice.',
              'No match, a different lot, or a terminated recall does not prove your product safe. Lot ranges and all-lot notices require human interpretation.',
              'Enforcement records can lag announcements and do not contain all consumer instructions. Includes historical records.']}

def reporting_resources():
    return {'source':'curated:official-directories','resources':[
      {'title':'FDA MedWatch: report a suspected medicine problem','url':'https://www.fda.gov/safety/medwatch-fda-safety-information-and-adverse-event-reporting-program','purpose':'Official reporting instructions; a report does not establish causation and is not emergency care.'},
      {'title':'Poison Help','url':'https://poisonhelp.hrsa.gov/what-you-can-do','purpose':'Immediate suspected poisoning guidance.'},*DIRECTORIES],
      'submission_performed':False,'limitations':['Navigation links only, not a live search or completed report. Do not enter private medical details in this MCP.']}
