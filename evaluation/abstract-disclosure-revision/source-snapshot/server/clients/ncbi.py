"""ncbi public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def _ncbi(endpoint: str, **p):
    p.update(tool="mcp-mother-child", email=cfg.NCBI_EMAIL)
    if cfg.NCBI_API_KEY:
        p["api_key"] = cfg.NCBI_API_KEY
    return await http.request("GET", f"{EUTILS}/{endpoint}.fcgi", params=p, ttl=3600,
                              interval=cfg.NCBI_INTERVAL)
