"""Agent-facing nichd actions."""
import asyncio
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import Literal
from core import config as cfg, safety as parent_safety
from clients import lakehouse as lh, pediatric_labels, mprint_data, nichd, parent_resources as parents
import clients as src
from models.contracts import *
from .common import _lakehouse_or_none
from models.inputs import Population
log = logging.getLogger('mc')

async def search_bpca_evidence(query: OptionalQuery = "", max_results: Limit25 = 10) -> EvidenceResponse:
    """Discover NICHD BPCA/PTN study-summary links by drug/title words. Returns index titles and links, NOT PDF contents or clinical conclusions. Empty query lists summaries."""
    return await nichd.search_bpca(query, max_results)

async def search_nichd_studies(query: OptionalQuery = "", network: Literal["any", "mfmu", "neonatal"] = "any", max_results: Limit25 = 10, page: Page = 0) -> EvidenceResponse:
    """Search public NICHD DASH study descriptions and publications, optionally MFMU or Neonatal Research Network. Zero-based pages. Controlled underlying datasets are NOT retrieved; access process is required."""
    return await nichd.search_dash(query, network, max_results, page)
