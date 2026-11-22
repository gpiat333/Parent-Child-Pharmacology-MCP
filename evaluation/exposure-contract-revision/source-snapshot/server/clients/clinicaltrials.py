from core.population import registry_band_matches, BANDS
"""clinicaltrials public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http

CTGOV = "https://clinicaltrials.gov/api/v2/studies"

def intervention_name_without_strength(name: str) -> str:
    """Conservative display formatting; not ingredient normalization or dose advice."""
    pattern=r'(?<![\w.])\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?\s*(?:mcg|µg|μg|mg|g|ml|iu|units)(?:\s*/\s*(?:kg|ml|day))?(?![a-zA-Z])'
    return re.sub(r'\s+',' ',re.sub(pattern,'',name,flags=re.I)).strip()

async def trials_search(term: str, population: str = "pregnancy", n: int = 10) -> list[dict]:
    from .parent_resources import participation_fields, pediatric_population
    extra = {"neonate":"neonate OR newborn", "infant":"infant", "child":"child", "adolescent":"adolescent", "pregnancy": "pregnancy", "lactation": "lactation OR breastfeeding",
             "pediatric": "children OR infant"}.get(population, "")
    q = f"{term} AND ({extra})" if extra else term
    r = await http.request("GET", CTGOV, params={"query.term": q, "pageSize": n, "format": "json"}, ttl=3600)
    out = []
    for s in r.json().get("studies", []):
        p = s["protocolSection"]
        if not registry_band_matches(p.get('eligibilityModule', {}), population):
            continue
        nct = p["identificationModule"]["nctId"]
        out.append({"nct": nct, "title": p["identificationModule"].get("briefTitle"),
                    "status": p["statusModule"].get("overallStatus"),
                    "has_results": s.get('hasResults'),
                    "results_posted": s.get('hasResults'),
                    "results_interpretation": 'Posted results do not establish benefit or clinical suitability; registration alone is not a finding.',
                    "conditions": p.get("conditionsModule", {}).get("conditions", []),
                    "interventions": [{"name": i.get("name"), "type": i.get("type"),
                                       "name_without_strength": intervention_name_without_strength(i.get("name") or '')}
                                      for i in p.get("armsInterventionsModule", {}).get("interventions", [])],
                    "summary": p.get("descriptionModule", {}).get("briefSummary", "")[:1500],
                    "url": f"https://clinicaltrials.gov/study/{nct}", **participation_fields(p)})
    return out

async def trial_by_nct(nct_id,population='any'):
    if not re.fullmatch(r'NCT[0-9]{8}',nct_id):raise ValueError('Invalid NCT identifier')
    from .parent_resources import participation_fields
    s=(await http.request('GET',CTGOV+'/'+nct_id,params={'format':'json'},ttl=3600)).json()
    p=s.get('protocolSection',{});ident=p.get('identificationModule',{});status=p.get('statusModule',{})
    return {'nct':ident.get('nctId',nct_id),'title':ident.get('briefTitle'),'status':status.get('overallStatus'),
        'has_results':s.get('hasResults'),'results_posted':s.get('hasResults'),
        'results_interpretation':'The results_posted flag states whether results are posted. Registration and posted results do not establish benefit or clinical suitability.',
        'conditions':p.get('conditionsModule',{}).get('conditions',[]),'summary':p.get('descriptionModule',{}).get('briefSummary','')[:1500],
        'summary_truncated':len(p.get('descriptionModule',{}).get('briefSummary',''))>1500,
        'requested_population':population,'requested_age_band_overlap':registry_band_matches(p.get('eligibilityModule',{}),population),
        'population_scope':'An age-range overlap is not evidence specific to that age band. Preserve actual source eligibility.',
        'url':'https://clinicaltrials.gov/study/'+nct_id,**participation_fields(p)}
