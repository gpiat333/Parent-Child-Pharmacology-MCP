"""Agent-facing lactation actions."""
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

async def search_lactmed(drug: Query, max_results: Limit20 = 5) -> EvidenceResponse:
    """Find LactMed (Drugs and Lactation Database, NLM) records by drug name.
    Returns IDs to pass to get_lactmed_record."""
    max_results = max(1, min(max_results, 20))
    rows = await _lakehouse_or_none(lh.sql(
        f"SELECT book_id, title, accession FROM {cfg.table('lactmed_records')} "
        f"WHERE lower(title) LIKE :p ORDER BY length(title) LIMIT {max_results}",
        {"p": f"%{drug.lower()}%"}))
    if rows:
        return {"source": "lakehouse", "results": [
            {"id": r["book_id"], "title": r["title"],
             "url": f"https://www.ncbi.nlm.nih.gov/books/{r['accession']}/"} for r in rows]}
    return {"source": "live:ncbi", "results": await src.lactmed_search(drug, max_results)}

async def get_lactmed_record(book_id: BookID, max_chars: TextLimit = 6000) -> EvidenceResponse:
    """Get LactMed text for one record: use during lactation, drug levels, effects on
    breastfed infants and on lactation. Alternate Drugs to Consider is excluded from
    returned text and synthesis; this tool never recommends a substitution. First call search_lactmed and pass
    its numeric id as book_id. Never pass a drug name or invent a record ID.
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
    Preserve separate case-report events and timing: do not merge exposure changes
    with outcome observations, infer unstated timing, or imply proven causation.
    Include only relevant supported details; explicitly identify unspecified timing.
    For partial chronology, group only explicitly linked events rather than a fully
    ordered sequence; name the specific ordering that remains unknown.
    If outcome text is truncated, retrieve more with max_chars (up to 20000) or
    state the limitation; do not infer outcomes from monitoring advice."""
    if not book_id.isascii() or not book_id.isdigit():
        return {"source": "validation", "error": "Invalid book_id. Call search_lactmed and use its numeric id, not a drug name.",
                "url": "https://www.ncbi.nlm.nih.gov/books/NBK501922/"}
    max_chars = max(500, min(max_chars, 20000))
    # Legacy lakehouse text has no section-completeness/alternatives contract.
    # Retrieve the live structured extract rather than emitting unlabeled cached text.
    return {"source": "live:ncbi", **await src.lactmed_record(book_id, max_chars)}

async def semantic_search_lactmed(question: Question, max_results: Limit20 = 5) -> EvidenceResponse:
    """Natural-language search over lactation-only LactMed record identifiers.
    Requires the Vector Search index; otherwise explains how to fall back."""
    if not cfg.USE_LAKEHOUSE:
        return {"source":"none", "status":"not_enabled", "error":"not_enabled", "note":"Vector index is not configured. Use search_lactmed with a drug name."}
    rows = await lh.vector(cfg.index("lactmed_idx"), question, ["book_id", "title", "accession"],
                           max(1, min(max_results, 20)))
    return {"source": "lakehouse:vector", "results": [
        {"id": r["book_id"], "title": r["title"],
         "url": f"https://www.ncbi.nlm.nih.gov/books/{r['accession']}/"} for r in rows]}
