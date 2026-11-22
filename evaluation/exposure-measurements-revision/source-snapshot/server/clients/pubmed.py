"""pubmed public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http
from .ncbi import _ncbi
from .parsing import text_of
from core.literature_strategy import strategy
from core.research_filters import literature_filters

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

class SearchRows(list):
    def __init__(self,rows,metadata):
        super().__init__(rows)
        self.search_metadata=metadata
POPULATION_FILTERS = {
    "neonate": '("Infant, Newborn"[MeSH] OR neonat*[tiab] OR preterm[tiab])',
    "infant": '("Infant"[MeSH:noexp] OR infant*[tiab])',
    "child": '("Child"[MeSH] OR "Child, Preschool"[MeSH])',
    "adolescent": '("Adolescent"[MeSH] OR adolescen*[tiab])',
    "pregnancy": '("Pregnancy"[MeSH] OR pregnan*[tiab])',
    "lactation": '("Lactation"[MeSH] OR "Breast Feeding"[MeSH] OR breastfeed*[tiab])',
    "pediatric": '("Child"[MeSH] OR "Infant"[MeSH] OR pediatric*[tiab])',
}

def parse_pubmed_xml(xml: str) -> list[dict]:
    out = []
    for a in ET.fromstring(xml).iter("PubmedArticle"):
        out.append({
            "pmid": a.findtext(".//PMID"),
            "title": text_of(a.find(".//ArticleTitle")),
            "journal": a.findtext(".//Journal/Title"),
            "year": a.findtext(".//PubDate/Year"),
            "abstract": " ".join(text_of(b) for b in a.iterfind(".//AbstractText")),
            "publication_types": [text_of(b) for b in a.iterfind('.//PublicationType')],
            "mesh_terms": [text_of(b) for b in a.iterfind('.//MeshHeading/DescriptorName')],
            "pmc_id": next((b.text for b in a.iterfind('.//ArticleId') if b.get('IdType')=='pmc'),None),
        })
    return out

def pubmed_search_params(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all', publication_type='any', date_from=None, date_to=None) -> dict:
    curated=strategy(query,population,focus)
    term = curated['pubmed_query'] if curated else f"({query})" + (f" AND {POPULATION_FILTERS[population]}" if population in POPULATION_FILTERS else "")
    params=dict(db="pubmed", term=term, retmax=n, sort="relevance", retmode="json")
    if not curated: params.update(datetype='pdat',reldate=years*365)
    return literature_filters(params,publication_type,date_from,date_to)

def pubmed_search_url(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all', **filters) -> str:
    # Public query provenance only: never include API keys or other credentials.
    return EUTILS + '/esearch.fcgi?' + urlencode(pubmed_search_params(query,population,n,years,focus,**filters))

async def pubmed_search(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all', **filters) -> list[dict]:
    r = await _ncbi("esearch", **pubmed_search_params(query,population,n,years,focus,**filters))
    data=r.json()['esearchresult']
    metadata={k:data.get(k) for k in ['count','querytranslation','warninglist','errorlist']}
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return SearchRows([],metadata)
    s = (await _ncbi("esummary", db="pubmed", id=",".join(ids), retmode="json")).json()["result"]
    rows=[{"pmid": i, "title": s[i]["title"], "journal": s[i].get("source"),
             "year": s[i].get("pubdate"), "publication_types":s[i].get('pubtype',[]),
             "pmc_id":next((a.get('value') for a in s[i].get('articleids',[]) if a.get('idtype')=='pmc'),None),
             "url": f"https://pubmed.ncbi.nlm.nih.gov/{i}/"} for i in ids if i in s]
    await annotate_availability(rows)
    return SearchRows(rows,metadata)

async def annotate_availability(rows):
    """Free-readability comes from PubMed's filter, never merely a PMC identifier."""
    ids=[str(r['pmid']) for r in rows if re.fullmatch(r'[1-9][0-9]{0,9}',str(r.get('pmid','')))]
    free=None
    if ids:
        try:
            term='('+' OR '.join(i+'[PMID]' for i in ids)+') AND free full text[sb]'
            data=(await _ncbi('esearch',db='pubmed',term=term,retmax=len(ids),retmode='json')).json()['esearchresult']
            free=set(data['idlist'])
        except Exception:pass
    for row in rows:
        pmc=row.get('pmc_id');license_name=None;oa=None
        if pmc and re.fullmatch(r'PMC[1-9][0-9]*',pmc):
            try:
                data=await http.request('GET','https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi',params={'id':pmc},ttl=86400,interval=.35)
                record=ET.fromstring(data.text).find('.//record')
                if record is not None and record.get('license'):
                    license_name=record.get('license');oa=True
            except Exception:pass
        available=str(row['pmid']) in free if free is not None else None
        row['full_text_availability']={'pmc_id':pmc,'pmc_url':f'https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/' if pmc else None,'free_full_text_available':available,
            'open_access_flag':oa,'open_access_license':license_name,
            'paywall_indicator':'free_full_text_listed' if available else 'not_verified',
            'availability_basis':'PubMed free full text subset; PMC OA service confirms licenses when listed.',
            'notice':'PMC ID alone does not establish current access; embargoes can apply. No free link confirmed does not prove a paywall. Free reading does not establish an open reuse license. Full text was not retrieved.'}

async def pubmed_abstracts(pmids: list[str]) -> list[dict]:
    if not pmids or any(not re.fullmatch(r"[1-9][0-9]{0,9}", p) for p in pmids):
        raise ValueError("Invalid PMID list")
    r = await _ncbi("efetch", db="pubmed", id=",".join(pmids[:10]), retmode="xml")
    articles=parse_pubmed_xml(r.text)
    for article in articles:
        if re.fullmatch(r'[1-9][0-9]{0,9}',article.get('pmid') or ''):
            article['url']=f'https://pubmed.ncbi.nlm.nih.gov/{article["pmid"]}/'
    await annotate_availability(articles)
    return articles
