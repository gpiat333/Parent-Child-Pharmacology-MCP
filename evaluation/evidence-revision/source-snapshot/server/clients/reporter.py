"""reporter public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http

REPORTER = "https://api.reporter.nih.gov/v2/projects/search"

async def reporter_search(text: str, n: int = 10) -> list[dict]:
    body = {"criteria": {"advanced_text_search": {"operator": "and", "search_field": "all",
                                                  "search_text": text}},
            "include_fields": ["ProjectNum", "ProjectTitle", "FiscalYear", "AgencyIcAdmin",
                               "Organization", "ProjectDetailUrl", "AbstractText"],
            "offset": 0, "limit": n, "sort_field": "fiscal_year", "sort_order": "desc"}
    r = await http.request("POST", REPORTER, json=body, interval=1.0)
    return [{"project_num": p.get("project_num"), "title": p.get("project_title"),
             "fiscal_year": p.get("fiscal_year"),
             "institute": (p.get("agency_ic_admin") or {}).get("abbreviation"),
             "organization": (p.get("organization") or {}).get("org_name"),
             "abstract": (p.get("abstract_text") or "")[:2000],
             "abstract_truncated": len(p.get("abstract_text") or "") > 2000,
             "url": p.get("project_detail_url")} for p in r.json().get("results", [])]
