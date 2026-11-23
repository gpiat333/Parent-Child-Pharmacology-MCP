"""Agent-facing lactation actions."""

import logging

import parent_child_pharmacology.clients as src
from parent_child_pharmacology.clients import (
    lakehouse as lh,
)
from parent_child_pharmacology.core import config as cfg
from parent_child_pharmacology.models.contracts import (
    BookID,
    EvidenceResponse,
    Limit20,
    OptionalQuery,
    Query,
    TextLimit,
)

from .common import _lakehouse_or_none

log = logging.getLogger("mc")


async def search_lactmed(drug: Query, max_results: Limit20 = 5) -> EvidenceResponse:
    """Find LactMed (Drugs and Lactation Database, NLM) records by drug name.
    Internal lookup used by get_lactmed_record and the evidence brief; not a registered tool."""
    max_results = max(1, min(max_results, 20))
    rows = await _lakehouse_or_none(
        lh.sql(
            f"SELECT book_id, title, accession FROM {cfg.table('lactmed_records')} "
            f"WHERE lower(title) LIKE :p ORDER BY length(title) LIMIT {max_results}",
            {"p": f"%{drug.lower()}%"},
        )
    )
    if rows:
        return {
            "source": "lakehouse",
            "results": [
                {
                    "id": r["book_id"],
                    "title": r["title"],
                    "url": f"https://www.ncbi.nlm.nih.gov/books/{r['accession']}/",
                }
                for r in rows
            ],
        }
    from parent_child_pharmacology.clients.lactmed import snapshot_title_match

    title = snapshot_title_match(drug)
    if title and title.lower() != drug.lower().strip():
        return {
            "source": "live:ncbi",
            "results": await src.lactmed_search(title, max_results),
            "matched_lactmed_title": title,
            "match_note": f"Searched the LactMed record title {title!r} for {drug!r}. LactMed groups vaccines by type.",
        }
    return {"source": "live:ncbi", "results": await src.lactmed_search(drug, max_results)}


async def get_lactmed_record(
    book_id: BookID | None = None, max_chars: TextLimit = 16000, drug: OptionalQuery = ""
) -> EvidenceResponse:
    """Read the LactMed (Drugs and Lactation Database, NLM) record for a medicine: use during lactation, drug levels, effects on
    breastfed infants and on lactation. Alternate Drugs to Consider is excluded from
    returned text and synthesis; this tool never recommends a substitution. Pass drug (a medicine or vaccine
    name) to find and read its record in one call; when several records match, the candidates are
    returned and you call again with the chosen book_id. Never invent a record ID.
    Separate measured exposure, observed infant outcomes, and source recommendations.
    A recommendation to monitor a symptom is NOT evidence that the symptom occurred.
    Conversely, a symptom monitored in a study is NOT a recommendation to monitor it.
    In every record summary, include a Measured exposure row using exposure_measurements:
    give retrieved milk concentration values AND units with source context, plus infant-level
    availability. A qualitative low/trace summary alone is incomplete when numerical measurements
    were returned. If omitting measurements, explicitly disclose the omission. Read compartment
    context; never label maternal-serum measurements as milk or infant serum.
    Concentrations are research findings, not administered doses. Omit administered regimens
    when doses are excluded, while retaining the requested exposure findings.
    Keep each study's exact comparator, co-exposures and specimen terminology separate.
    Do not narrow unspecified infant levels to blood or serum.
    Preserve separate case-report events and timing: do not merge exposure changes
    with outcome observations, infer unstated timing, or imply proven causation.
    Include only relevant supported details; explicitly identify unspecified timing.
    For partial chronology, group only explicitly linked events rather than a fully
    ordered sequence; name the specific ordering that remains unknown.
    If outcome text is truncated, retrieve more with max_chars (up to 20000) or
    state the limitation; do not infer outcomes from monitoring advice.
    Text comes from NCBI's official LactMed package (see data_freshness). Bracketed
    numbers such as [54] are LactMed citations: link reported findings to their studies
    using the returned references list."""
    if not book_id:
        if not drug:
            return {
                "source": "validation",
                "error": "drug_or_book_id_required",
                "note": "Provide a medicine name in drug, or a book_id from an earlier result.",
                "url": "https://www.ncbi.nlm.nih.gov/books/NBK501922/",
            }
        found = await search_lactmed(drug, 5)
        candidates = found.get("results", [])
        exact = [c for c in candidates if (c.get("title") or "").casefold() == drug.casefold()]
        matched = found.get("matched_lactmed_title")
        if matched:
            exact = [c for c in candidates if c.get("title") == matched] or exact
        chosen = exact[0] if len(exact) == 1 else candidates[0] if len(candidates) == 1 else None
        if not chosen:
            return {
                "source": found.get("source", "live:ncbi"),
                "results": candidates,
                "requires_record_selection": bool(candidates),
                "note": "Several LactMed records match. Call again with the book_id of the intended record."
                if candidates
                else "No LactMed record was found for this name. This is not evidence of safety.",
                **({k: found[k] for k in ("matched_lactmed_title", "match_note") if k in found}),
            }
        book_id = chosen["id"]
        selection = {
            "matched_record": chosen,
            "other_candidates": [c for c in candidates if c is not chosen],
            **({k: found[k] for k in ("matched_lactmed_title", "match_note") if k in found}),
        }
    else:
        selection = {}

    if not book_id.isascii() or not book_id.isdigit():
        return {
            "source": "validation",
            "error": "Invalid book_id. Pass the medicine name in drug, or a numeric id from an earlier result.",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK501922/",
        }
    max_chars = max(500, min(max_chars, 20000))
    # Legacy lakehouse text has no section-completeness/alternatives contract.
    # Retrieve the live structured extract rather than emitting unlabeled cached text.
    return {"source": "live:ncbi", **await src.lactmed_record(book_id, max_chars), **selection}
