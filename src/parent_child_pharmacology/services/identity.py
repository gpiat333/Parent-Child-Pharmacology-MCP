"""Agent-facing identity actions."""

import logging

import parent_child_pharmacology.clients as src
from parent_child_pharmacology.models.contracts import EvidenceResponse, Query

log = logging.getLogger("mc")


async def normalize_drug(name: Query) -> EvidenceResponse:
    """Resolve a brand name, misspelling or combination product to standard generic
    ingredient(s) and an RxNorm ID (RxNorm, NLM). Call this first when unsure of the drug name.
    found=false means unverified. requires_confirmation=true means a tentative match:
    ask for confirmation; never silently substitute its ingredient as the intended drug."""
    return {"source": "live:rxnorm", **await src.rxnorm_normalize(name)}
