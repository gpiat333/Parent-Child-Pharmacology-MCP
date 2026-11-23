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


async def search_nichd_resources(
    query: OptionalQuery = "",
    source: Literal["bpca_summaries", "dash_studies"] = "bpca_summaries",
    network: Literal["any", "mfmu", "neonatal"] = "any",
    max_results: Limit25 = 10,
    page: Page = 0,
) -> EvidenceResponse:
    """Search NICHD's public research resources. Choose one source:
    bpca_summaries: NICHD BPCA and Pediatric Trials Network study-summary links by drug or
    title words. Returns index titles and links, NOT PDF contents or clinical conclusions.
    An empty query lists summaries.
    dash_studies: public study descriptions and publications in the NICHD Data and Specimen
    Hub (DASH), optionally limited to the Maternal-Fetal Medicine Units (mfmu) or Neonatal
    Research Network. Zero-based pages. Controlled underlying datasets are NOT retrieved; an
    access process is required.
    network and page apply to dash_studies only."""
    if source == "bpca_summaries":
        return {**await search_bpca_evidence(query, max_results), "nichd_source": source}
    return {**await nichd.search_dash(query, network, max_results, page), "nichd_source": source}
