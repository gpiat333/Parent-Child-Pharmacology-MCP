"""dailymed public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http
from .parsing import text_of
from .pllr import parse_pllr

DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
LOINC_SECTIONS = {"42228-7": "pregnancy", "77290-5": "lactation", "34081-0": "pediatric_use"}
SECTION_TITLES = {"pregnancy": "pregnancy", "lactation": "lactation",
                  "nursing mothers": "lactation", "pediatric use": "pediatric_use",
                  "geriatric use": "geriatric_use"}

def parse_dailymed_sections(xml: str, max_chars: int = 4000) -> dict[str, str]:
    ns = {"h": "urn:hl7-org:v3"}
    found = {}
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        c = sec.find("h:code", ns)
        title = re.sub(r"^[\d.\s]+", "", text_of(sec.find("h:title", ns))).strip().lower()
        key = SECTION_TITLES.get(title)
        # Some source SPLs miscode adjacent sections. Never call explicit
        # geriatric text pediatric merely because its code says pediatric.
        if key is None and not title and c is not None:
            key = LOINC_SECTIONS.get(c.get("code"))
        # OTC labels use one combined section (LOINC 53414-9). Preserve
        # its scope rather than duplicating it into two independent sections.
        if key is None and c is not None and c.get("code") == "53414-9" and title in {
            "", "if pregnant or breast-feeding", "if pregnant or breast-feeding:",
            "pregnancy or breast feeding", "pregnancy or breast-feeding",
        }:
            key = "pregnancy_lactation"
        if key in {"pregnancy", "lactation", "pediatric_use", "pregnancy_lactation"}:
            content = text_of(sec.find("h:text", ns))
            if content:
                found.setdefault(key, content[:max_chars])
    return found

def dailymed_section_warnings(xml: str) -> list[dict]:
    ns = {"h": "urn:hl7-org:v3"}
    warnings = []
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        title = text_of(sec.find("h:title", ns))
        normalized = re.sub(r"^[\d.\s]+", "", title).strip().lower()
        code = sec.find("h:code", ns)
        if normalized in SECTION_TITLES and code is not None:
            key = SECTION_TITLES[normalized]
            expected = {"pregnancy": "42228-7", "lactation": "77290-5",
                        "pediatric_use": "34081-0", "geriatric_use": "34082-8"}[key]
            if normalized == "nursing mothers":
                expected = "34080-2"  # Valid older SPL heading/code, not a mismatch.
            if code.get("code") != expected:
                warnings.append({"title": title, "code": code.get("code"),
                                 "note": "Source title/code mismatch; classified by explicit title. Verify the linked label."})
    return warnings

async def dailymed_label(drug: str) -> dict:
    r = await http.request("GET", f"{DAILYMED}/spls.json",
                           params={"drug_name": drug, "pagesize": 5}, ttl=86400)
    for item in r.json().get("data", []):
        x = await http.request("GET", f"{DAILYMED}/spls/{item['setid']}.xml", ttl=86400)
        secs = parse_dailymed_sections(x.text)
        if secs:
            return {"setid": item["setid"], "title": item["title"], "sections": secs,
                    "missing_standalone_sections": [k for k in ("pregnancy", "lactation", "pediatric_use") if k not in secs],
                    "selection_note": "One matching product label, not all formulations. A combined OTC pregnancy_lactation warning is not a standalone pediatric-use section. Missing sections do not establish safety or absence of information elsewhere in the label.",
                    "warnings": dailymed_section_warnings(x.text),
                    "pllr_8_1": parse_pllr(xml=x.text),
                    "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={item['setid']}"}
    return {}
