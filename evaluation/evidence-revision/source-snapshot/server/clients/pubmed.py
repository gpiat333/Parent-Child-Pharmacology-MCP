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
        })
    return out

def pubmed_search_params(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all') -> dict:
    curated=strategy(query,population,focus)
    term = curated['pubmed_query'] if curated else f"({query})" + (f" AND {POPULATION_FILTERS[population]}" if population in POPULATION_FILTERS else "")
    params=dict(db="pubmed", term=term, retmax=n, sort="relevance", retmode="json")
    if not curated: params.update(datetype='pdat',reldate=years*365)
    return params

def pubmed_search_url(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all') -> str:
    # Public query provenance only: never include API keys or other credentials.
    return EUTILS + '/esearch.fcgi?' + urlencode(pubmed_search_params(query,population,n,years,focus))

async def pubmed_search(query: str, population: str = "any", n: int = 10, years: int = 10, focus: str = 'all') -> list[dict]:
    r = await _ncbi("esearch", **pubmed_search_params(query,population,n,years,focus))
    data=r.json()['esearchresult']
    metadata={k:data.get(k) for k in ['count','querytranslation','warninglist','errorlist']}
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return SearchRows([],metadata)
    s = (await _ncbi("esummary", db="pubmed", id=",".join(ids), retmode="json")).json()["result"]
    return SearchRows([{"pmid": i, "title": s[i]["title"], "journal": s[i].get("source"),
             "year": s[i].get("pubdate"), "url": f"https://pubmed.ncbi.nlm.nih.gov/{i}/"}
            for i in ids if i in s],metadata)

async def pubmed_abstracts(pmids: list[str]) -> list[dict]:
    if not pmids or any(not re.fullmatch(r"[1-9][0-9]{0,9}", p) for p in pmids):
        raise ValueError("Invalid PMID list")
    r = await _ncbi("efetch", db="pubmed", id=",".join(pmids[:10]), retmode="xml")
    articles=parse_pubmed_xml(r.text)
    for article in articles:
        if re.fullmatch(r'[1-9][0-9]{0,9}',article.get('pmid') or ''):
            article['url']=f'https://pubmed.ncbi.nlm.nih.gov/{article["pmid"]}/'
    return articles
