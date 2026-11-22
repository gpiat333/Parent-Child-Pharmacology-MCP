"""openfda public-source adapter; no MCP registration."""
import re
import html.parser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import httpx
from core import config as cfg
from core.http import http

OPENFDA_EVENT = "https://api.fda.gov/drug/event.json"

def faers_query_params(drug: str, cohort: str = "any", n: int = 10) -> dict:
    drug = drug.replace('"', '').replace('\\', '').strip()
    clauses = [f'patient.drug.openfda.generic_name:"{drug}"']
    if cohort == "pregnancy":
        clauses.append('patient.reaction.reactionmeddrapt:"foetal exposure during pregnancy"')
    elif cohort == "infant":  # patientonsetageunit 802 = month
        clauses.append("patient.patientonsetageunit:802 AND patient.patientonsetage:[0 TO 12]")
    return {"search": " AND ".join(clauses), "count": "patient.reaction.reactionmeddrapt.exact", "limit": n}

async def faers_top_reactions(drug: str, cohort: str = "any", n: int = 10) -> list[dict]:
    try:
        r = await http.request("GET", OPENFDA_EVENT, ttl=3600, params=faers_query_params(drug, cohort, n))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:  # openFDA: 404 == no matches
            return []
        raise
    return [{"reaction": x["term"], "reports": x["count"]} for x in r.json().get("results", [])]
