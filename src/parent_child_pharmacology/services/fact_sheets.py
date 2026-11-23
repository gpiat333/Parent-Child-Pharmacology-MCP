"""MotherToBaby fact sheet discovery: a labeled, non-federal consumer resource."""

import json
from typing import Literal

from parent_child_pharmacology.clients.mothertobaby import (
    COLLECTION_URL,
    SNAPSHOT,
    fact_sheet_search,
    snapshot_search,
    snapshot_sheet,
)
from parent_child_pharmacology.core.referrals import MOTHERTOBABY
from parent_child_pharmacology.models.contracts import EvidenceResponse, Limit20, Query, TextLimit

MANIFEST = SNAPSHOT.with_name("mothertobaby-manifest.json")
LICENSE = "CC BY-NC-ND 3.0 (https://creativecommons.org/licenses/by-nc-nd/3.0/)"


def _attach_text(sheets, budget):
    """Add verbatim Q&A text; whole answers only, never shortened (license: no derivatives)."""
    for sheet in sheets:
        record = snapshot_sheet(sheet.get("doc_id"))
        if not record:
            sheet["text"] = None
            sheet["text_note"] = "Not in the bundled package; open the link to read it."
            continue
        kept, omitted = [], []
        for qa in record["qa"]:
            size = len(qa["question"]) + len(qa["answer"])
            if size <= budget:
                kept.append(qa)
                budget -= size
            else:
                omitted.append(qa["question"])
        sheet["text"] = {
            "preamble": record.get("preamble"),
            "questions_and_answers": kept,
            "questions_omitted_by_length_limit": omitted,
            "attribution": f"{record.get('copyright') or 'Copyright OTIS'}. MotherToBaby fact sheet, {LICENSE}. Reproduced verbatim.",
        }
    return sheets


async def search_mothertobaby_fact_sheets(
    drug: Query,
    language: Literal["any", "en", "es"] = "any",
    max_results: Limit20 = 5,
    include_text: bool = True,
    max_chars: TextLimit = 8000,
) -> EvidenceResponse:
    """Find MotherToBaby fact sheets on a medicine or exposure in pregnancy and breastfeeding,
    in English or Spanish, and return their question-and-answer text verbatim from NCBI's
    official package. Answers are never shortened; when the length limit is reached, whole
    questions are omitted and listed. Quote or closely paraphrase only the returned text and
    keep the attribution. Fact sheets are consumer summaries from OTIS, a nonprofit,
    distributed by NLM: label them as nonprofit content, separate from federal evidence and
    from LactMed. No coverage of medicines given to children. For an individual question,
    offer the MotherToBaby referral."""
    try:
        sheets = await fact_sheet_search(drug, 20)
        search_mode = "live:ncbi-eutils"
    except Exception:
        sheets = snapshot_search(drug, 20)
        search_mode = "snapshot_fallback"
    if language != "any":
        sheets = [s for s in sheets if s["language"] == language]
    sheets = sheets[:max_results]
    if include_text:
        sheets = _attach_text(sheets, max_chars)
    package = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    return {
        "source": "live:ncbi-bookshelf:mothertobaby",
        "status": "ok" if sheets else "no_results",
        "fact_sheets": sheets,
        "publisher": "Organization of Teratology Information Specialists (OTIS), a nonprofit",
        "distributor": "National Library of Medicine, NCBI Bookshelf",
        "collection_url": COLLECTION_URL,
        "content_type": "nonprofit consumer fact sheet; not curated federal evidence",
        "license": LICENSE + ": noncommercial, attributed, verbatim.",
        "text_included": include_text,
        "text_source": f"NCBI official package published {package.get('package_published_utc', '')[:10]}"
        if include_text
        else None,
        "search_mode": search_mode,
        "scope": "Pregnancy and breastfeeding exposures. Does not cover medicines given to children.",
        "no_results_meaning": "No matching fact sheet title was found. This is not evidence of safety or harm.",
        "specialist_referral": MOTHERTOBABY,
        "source_urls": [COLLECTION_URL] + [s["url"] for s in sheets if s.get("url")],
    }
