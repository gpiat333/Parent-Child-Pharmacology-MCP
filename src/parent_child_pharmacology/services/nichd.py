"""Agent-facing nichd actions."""

import logging
from typing import Literal

from parent_child_pharmacology.clients import (
    nichd,
)
from parent_child_pharmacology.models.contracts import (
    EvidenceResponse,
    Limit25,
    OptionalQuery,
    Page,
)

log = logging.getLogger("mc")


async def search_bpca_evidence(
    query: OptionalQuery = "", max_results: Limit25 = 10
) -> EvidenceResponse:
    """Discover NICHD BPCA/PTN study-summary links by drug/title words. Returns index titles and links, NOT PDF contents or clinical conclusions. Empty query lists summaries."""
    return await nichd.search_bpca(query, max_results)


async def search_nichd_studies(
    query: OptionalQuery = "",
    network: Literal["any", "mfmu", "neonatal"] = "any",
    max_results: Limit25 = 10,
    page: Page = 0,
) -> EvidenceResponse:
    """Search public NICHD DASH study descriptions and publications, optionally MFMU or Neonatal Research Network. Zero-based pages. Controlled underlying datasets are NOT retrieved; access process is required."""
    return await nichd.search_dash(query, network, max_results, page)
