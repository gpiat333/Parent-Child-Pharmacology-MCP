"""Agent-facing identity actions."""
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

async def normalize_drug(name: Query) -> EvidenceResponse:
    """Resolve a brand name, misspelling or combination product to standard generic
    ingredient(s) and an RxNorm ID (RxNorm, NLM). Call this first when unsure of the drug name.
    found=false means unverified. requires_confirmation=true means a tentative match:
    ask for confirmation; never silently substitute its ingredient as the intended drug."""
    return {"source": "live:rxnorm", **await src.rxnorm_normalize(name)}
