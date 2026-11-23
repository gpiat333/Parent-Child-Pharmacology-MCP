"""MotherToBaby fact sheet discovery: a labeled, non-federal consumer resource."""

from typing import Literal

from parent_child_pharmacology.clients.mothertobaby import COLLECTION_URL, fact_sheet_search
from parent_child_pharmacology.core.referrals import MOTHERTOBABY
from parent_child_pharmacology.models.contracts import EvidenceResponse, Limit20, Query


async def search_mothertobaby_fact_sheets(
    drug: Query, language: Literal["any", "en", "es"] = "any", max_results: Limit20 = 5
) -> EvidenceResponse:
    """Find MotherToBaby fact sheets on a medicine or exposure in pregnancy and breastfeeding,
    in English or Spanish, via the NLM Bookshelf collection. Returns titles, links, dates and
    language only; page text is not retrieved, so never summarize a sheet you did not read.
    Fact sheets are consumer summaries from OTIS, a nonprofit, distributed by NLM: label them
    as nonprofit content, separate from federal evidence and from LactMed. No coverage of
    medicines given to children. For an individual question, offer the MotherToBaby referral."""
    sheets = await fact_sheet_search(drug, 20)
    if language != "any":
        sheets = [s for s in sheets if s["language"] == language]
    sheets = sheets[:max_results]
    return {
        "source": "live:ncbi-bookshelf:mothertobaby",
        "status": "ok" if sheets else "no_results",
        "fact_sheets": sheets,
        "publisher": "Organization of Teratology Information Specialists (OTIS), a nonprofit",
        "distributor": "National Library of Medicine, NCBI Bookshelf",
        "collection_url": COLLECTION_URL,
        "content_type": "nonprofit consumer fact sheet; not curated federal evidence",
        "license": "CC BY-NC-ND 3.0 (per the Bookshelf collection record)",
        "page_text_retrieved": False,
        "scope": "Pregnancy and breastfeeding exposures. Does not cover medicines given to children.",
        "no_results_meaning": "No matching fact sheet title was found. This is not evidence of safety or harm.",
        "specialist_referral": MOTHERTOBABY,
        "source_urls": [COLLECTION_URL] + [s["url"] for s in sheets],
    }
