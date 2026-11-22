"""lactmed public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http
from .ncbi import _ncbi

LACTMED_HEADINGS = [
    "Summary of Use during Lactation", "Drug Levels", "Effects in Breastfed Infants",
    "Effects on Lactation and Breastmilk", "Alternate Drugs to Consider", "References",
]
EXPECTED_CLINICAL_SECTIONS=LACTMED_HEADINGS[:4]

def lactmed_payload(sections,max_chars=6000):
    from core.source_context import evidence_base,CONTINUITY_NOTICE
    clinical={h:sections[h] for h in EXPECTED_CLINICAL_SECTIONS if sections.get(h)}
    text='';status={}
    for heading,content in clinical.items():
        prefix=('\n\n' if text else '')+heading+': '
        space=max(0,max_chars-len(text)-len(prefix));piece=content[:space]
        if piece:text+=prefix+piece
        status[heading]={'found':True,'characters_in_source_extract':len(content),'characters_returned':len(piece),
            'returned':bool(piece),'truncated':len(piece)<len(content)}
    missing=[h for h in EXPECTED_CLINICAL_SECTIONS if h not in clinical]
    out={'text':text,'sections_found':list(clinical),'sections_expected':EXPECTED_CLINICAL_SECTIONS,
        'sections_missing':missing,'sections_returned':[h for h,v in status.items() if v['returned']],
        'sections_omitted_by_limit':[h for h,v in status.items() if not v['returned']],
        'section_status':status,'truncated':any(v['truncated'] for v in status.values()),
        'section_completeness_notice':'Missing sections can reflect source coverage or parser failure; truncated sections are incomplete. Do not present this extract as a complete record.',
        'evidence_base':evidence_base(' '.join(clinical.values())),
        'source_balance_context':{'text':clinical.get('Summary of Use during Lactation','')[:4000] or None,
            'truncated':len(clinical.get('Summary of Use during Lactation',''))>4000,'source_section':'Summary of Use during Lactation',
            'notice':'Preserve relevant source context when describing adverse findings; this is source text, not a personal treatment plan.'},
        'alternatives_policy':{'handling':'excluded','present_in_parsed_source':bool(sections.get('Alternate Drugs to Consider')),
            'notice':'Alternate Drugs to Consider is excluded from returned text and synthesis. Consult the linked LactMed source; this tool does not recommend substitutions.'},
        'population_context':{'source_population':'lactation','pregnancy_evidence':False},
        'continuity_of_care_notice':CONTINUITY_NOTICE}
    if not clinical:out.update(error='clinical_sections_unavailable',clinical_sections_unavailable=True)
    return out

async def lactmed_search(drug: str, n: int = 5) -> list[dict]:
    drug = drug.replace('"', "").strip()
    ids: list[str] = []
    for term in (f'"{drug}"[Title] AND lactmed[Book]', f"{drug} AND lactmed[Book]"):
        r = await _ncbi("esearch", db="books", term=term, retmax=n, retmode="json")
        ids = r.json()["esearchresult"]["idlist"]
        if ids:
            break
    if not ids:
        return []
    s = (await _ncbi("esummary", db="books", id=",".join(ids), retmode="json")).json()["result"]
    return [{"id": i, "title": s[i].get("title"),
             "url": f"https://www.ncbi.nlm.nih.gov/books/{s[i].get('accessionid', '')}/"}
            for i in ids if i in s]

class _PageText(html.parser.HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in ("p", "div", "h1", "h2", "h3", "h4", "li", "br", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in ("p", "div", "h1", "h2", "h3", "h4", "li", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

def parse_lactmed_html(page: str) -> dict[str, str]:
    p = _PageText()
    p.feed(page)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in "".join(p.parts).split("\n")]
    lookup = {h.lower(): h for h in LACTMED_HEADINGS}
    sections: dict[str, list[str]] = {}
    current = None
    for ln in filter(None, lines):
        key = ln.lower().rstrip(":")
        if current and (key == "references" or key.startswith((
            "references ", "substance identification", "administrative information",
            "copyright notice", "disclaimer:", "bookshelf id:", "related information"))):
            break
        if key in lookup:
            current = lookup[key]
            sections.setdefault(current, [])
        elif current:
            sections[current].append(ln)
    return {h: " ".join(t) for h, t in sections.items() if t and h != "References"}

async def lactmed_record(book_id: str, max_chars: int = 6000) -> dict:
    if not re.fullmatch(r"[0-9]+", book_id):
        return {"book_id": book_id, "text": "", "error": "Invalid book_id. Call search_lactmed first and pass its numeric id, not a drug name.",
                "url": "https://www.ncbi.nlm.nih.gov/books/NBK501922/"}
    s = (await _ncbi("esummary", db="books", id=book_id, retmode="json")).json()["result"].get(book_id, {})
    acc = s.get("accessionid")
    if not acc:
        return {"book_id": book_id, "text": "", "note": "No accession found for this ID"}
    url = f"https://www.ncbi.nlm.nih.gov/books/{acc}/"
    r = await http.request("GET", url, ttl=86400, interval=0.4)
    sections = parse_lactmed_html(r.text)
    return {"book_id": book_id, "title": s.get("title"), "url": url,
            **lactmed_payload(sections,max_chars)}
