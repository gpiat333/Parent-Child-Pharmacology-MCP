"""Agent-facing labels_safety actions."""

import logging
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlencode

import parent_child_pharmacology.clients as src
from parent_child_pharmacology.clients import (
    lakehouse as lh,
)
from parent_child_pharmacology.clients import (
    pediatric_labels,
)
from parent_child_pharmacology.core import config as cfg
from parent_child_pharmacology.models.contracts import (
    EvidenceResponse,
    Limit20,
    Limit25,
    Query,
    RxCUI,
)

from .common import _lakehouse_or_none

log = logging.getLogger("mc")


async def get_label_sections(drug: Query) -> EvidenceResponse:
    """FDA label (via DailyMed, NLM) pregnancy, lactation and pediatric-use sections,
    plus medicine_taker_sections for adult adverse reactions and warnings from the same label.
    Also returns product_description (label section 11 or OTC ingredient lists): chemical name,
    molecular formula and weight, and active and inactive ingredients, for questions about what a
    medicine contains. Cite it; do not add chemistry from memory. approved_use_sections returns
    indications and clinical studies (mostly adults) for "where has it been studied or approved"
    questions; uses not listed there are off-label and are not a recommendation for children.
    Inspect both groups for adult-versus-breastfed-infant comparisons, with LactMed for infant findings.
    Returns pllr_8_1 with Risk Summary, Clinical Considerations, Data and a source-only maternal_dose_adjustment field, including explicit nulls.
    OTC labels may return pregnancy_lactation as one combined warning.
    Identify the returned product title; do not generalize across formulations.
    Report returned source warnings and missing_standalone_sections. A combined
    warning does not provide pediatric-use evidence. Missing sections are retrieval limitations;
    do not fill them with uncited medical claims or infer safety."""
    rows = await _lakehouse_or_none(
        lh.sql(
            f"SELECT setid, title, pregnancy, lactation FROM {cfg.table('dailymed_labels')} "
            "WHERE lower(title) LIKE :p LIMIT 1",
            {"p": f"%{drug.lower()}%"},
        )
    )
    if rows:
        r = rows[0]
        from parent_child_pharmacology.clients.pllr import parse_pllr

        return {
            "source": "lakehouse",
            "setid": r["setid"],
            "title": r["title"],
            "spl_version": None,
            "effective_date": None,
            "labeler": None,
            "selection_basis": {
                "rule": "First cached title match; source version and exact product match were not verified."
            },
            "label_currency_notice": "Cached label version/date are unknown. DailyMed in-use labeling can differ from the latest FDA-approved version; verify the linked source.",
            "pllr_8_1": parse_pllr(pregnancy_text=r.get("pregnancy")),
            "sections": {k: r[k] for k in ("pregnancy", "lactation") if r.get(k)},
            "medicine_taker_sections": {},
            "medicine_taker_sections_status": "not_available_in_cached_extract",
            "section_scope_notice": "Cached extract has no medicine-taker sections. Use the live label for adult adverse reactions and warnings before attempting an adult/infant comparison.",
            "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={r['setid']}",
        }
    label = await src.dailymed_label(drug)
    return {
        "source": "live:dailymed",
        **(label or {"sections": {}, "note": f"No label sections found for {drug}"}),
    }


async def search_pediatric_labeling_changes(
    drug: Query, legislation: Literal["any", "BPCA", "PREA"] = "any", max_results: Limit20 = 10
) -> EvidenceResponse:
    """Search FDA historical pediatric labeling changes by generic or trade name.
    Returns dates, product/indication scope, BPCA/PREA category and FDA summaries.
    BPCA/PREA filters include rows listing both. Match names, not full questions;
    try generic or brand separately if no match. Preserve age, indication and
    formulation limits in source text. A labeling change is not automatically an
    approval or proof of safety. BPCA designation does not imply NIH funding.
    Cite the FDA source and workbook row; do not turn historical dose text into
    dosing advice. Use get_label_sections separately for current product labeling.
    Empty results do not establish absence of pediatric evidence."""
    return await pediatric_labels.search(drug, legislation, max_results)


async def get_adverse_event_signals(
    drug: Query, cohort: Literal["any", "pregnancy", "infant"] = "any", max_results: Limit25 = 10
) -> EvidenceResponse:
    """Most frequently reported reactions in FDA FAERS (openFDA) for a drug, optionally for
    pregnancy-exposure or infant reports. Counts are spontaneous reports, NOT incidence or proof of causation.
    Preserve the returned query scope and denominator limitations. Do not add uncited
    alternative causes or research-prioritization claims absent from retrieved material."""
    return {
        "source": "live:openfda",
        "cohort": cohort,
        "cohort_scope": "Infant filter includes only ages coded in months from 0 through 12; other age-unit encodings are excluded."
        if cohort == "infant"
        else "Reports matching the stated query; not a complete exposed population.",
        "url": src.OPENFDA_EVENT
        + "?"
        + urlencode(src.faers_query_params(drug, cohort, max(1, min(max_results, 25)))),
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "cache_note": "Upstream response may be cached for up to one hour; timestamp is query time.",
        "top_reactions": await src.faers_top_reactions(drug, cohort, max(1, min(max_results, 25))),
        "caveat": "FAERS counts reflect reporting volume, not risk; reports do not establish causation and lack exposure denominators.",
        "report_count_interpretation": {
            "establishes_causation": False,
            "exposure_denominator_available": False,
            "generalizable_to_all_infants": False,
            "generalizable_to_exposed_population": False,
            "population_scope_notice": "These FAERS results cover only the queried report subset. They cannot be generalized to all infants or all people exposed to the medicine.",
            "incidence_or_risk_calculable": False,
            "message": "Spontaneous report counts do not establish causation. Exposure denominators are absent; counts cannot estimate incidence or individual risk.",
            "source_url": "https://open.fda.gov/apis/drug/event/",
        },
    }


async def get_patient_education(
    topic: Query, rxcui: RxCUI | None = None, language: Literal["en", "es"] = "en"
) -> EvidenceResponse:
    """MedlinePlus education links. Spanish is a structured drug-code lookup only:
    use language=es with an already confirmed RxNorm ID and English drug name in topic.
    This does not enable Spanish free-form chat or clinical interpretation."""
    if language == "es":
        if not rxcui:
            return {
                "source": "validation",
                "error": "spanish_requires_rxcui",
                "language": "es",
                "note": "Confirm the medicine and supply its exact RxNorm ID for Spanish drug education.",
            }
        return {
            "source": "live:medlineplus",
            "language": "es",
            "topics": [],
            "drug_info": await src.medlineplus_drug(rxcui, language="es"),
            "coverage_notice": "Spanish drug-code lookup only; an English match does not guarantee a Spanish match.",
        }
    topics = await src.medlineplus_topics(topic)
    drug = await src.medlineplus_drug(rxcui) if rxcui else []
    return {"source": "live:medlineplus", "language": "en", "topics": topics, "drug_info": drug}
