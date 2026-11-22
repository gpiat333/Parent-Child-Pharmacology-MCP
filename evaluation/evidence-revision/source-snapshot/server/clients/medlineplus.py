"""medlineplus public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http
from .parsing import text_of

MEDLINEPLUS_SEARCH = "https://wsearch.nlm.nih.gov/ws/query"
MEDLINEPLUS_CONNECT = "https://connect.medlineplus.gov/service"

def parse_medlineplus_search(xml: str, limit: int = 5) -> list[dict]:
    out = []
    for doc in ET.fromstring(xml).iter("document"):
        item = {"url": doc.get("url")}
        for c in doc.iterfind("content"):
            if c.get("name") == "title":
                item["title"] = text_of(c)
            elif c.get("name") == "FullSummary":
                item["summary"] = text_of(c)[:1200]
        out.append(item)
    return out[:limit]

async def medlineplus_topics(term: str, n: int = 3) -> list[dict]:
    r = await http.request("GET", MEDLINEPLUS_SEARCH, ttl=86400,
                           params={"db": "healthTopics", "term": term, "retmax": n})
    return parse_medlineplus_search(r.text, n)

async def medlineplus_drug(rxcui: str, language: str = 'en') -> list[dict]:
    r = await http.request("GET", MEDLINEPLUS_CONNECT, ttl=86400, params={
        "mainSearchCriteria.v.c": rxcui, "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.88",
        "knowledgeResponseType": "application/json", "informationRecipient.languageCode.c": language})
    entries = r.json().get("feed", {}).get("entry", [])
    return [{"title": e.get("title", {}).get("_value"),
             "url": (e.get("link") or [{}])[0].get("href"),
             "summary": (e.get("summary", {}).get("_value") or "")[:1200]} for e in entries]
