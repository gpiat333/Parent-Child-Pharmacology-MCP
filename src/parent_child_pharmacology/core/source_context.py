"""Visible interpretation limits; no automated claim of clinical adjudication."""

import re

CONTINUITY_NOTICE = "Stopping or changing a medication can also carry risks. Discuss changes with the prescribing clinician. This tool cannot advise starting, stopping, or changing treatment."
NO_EFFECT = re.compile(
    r"no (?:adverse |side |untoward )?effects|no adverse reactions|none.{0,30}(?:adverse|effects)|not.{0,35}(?:adversely affected|adverse effects)",
    re.I,
)


def evidence_base(text, publication_types=None):
    mentioned = []
    for name, pattern in [
        (
            "case_report",
            r"case report|one (?:mother|infant|woman)|a (?:mother|woman|breastfed infant)",
        ),
        ("observational", r"observational|cohort"),
        ("randomized_trial", r"randomi[sz]ed"),
        ("systematic_review", r"systematic review"),
        ("meta_analysis", r"meta.analysis"),
    ]:
        if re.search(pattern, text or "", re.I):
            mentioned.append(name)
    return {
        "study_count": None,
        "study_count_status": "not_established_from_this_extract",
        "source_publication_types": publication_types or [],
        "study_types_mentioned": mentioned,
        "type_detection": "Source metadata where supplied; text mentions otherwise heuristic, not adjudicated.",
        "reference_markers": list(dict.fromkeys(re.findall(r"\[(\d+(?:[-, ]\d+)*)\]", text or ""))),
        "reference_count_is_not_study_count": True,
        "no_effects_statement_detected": bool(NO_EFFECT.search(text or "")),
        "interpretation": "A no-effects statement does not establish safety or a well-studied population. Study counts and designs need source/clinical review; missing counts are unknown, not zero.",
    }


def population_context(requested, source_population, source_basis, confirmed=False):
    return {
        "requested_population": requested,
        "source_population": source_population,
        "source_basis": source_basis,
        "matches_requested_population_confirmed": confirmed,
        "age_band_confirmed": False,
        "notice": "Search filters and broad population labels do not confirm applicability. Preserve actual age, prematurity, gestational stage and study population.",
    }


def item_population(item, requested=None):
    tags = []
    mesh = item.get("mesh_terms") or []
    for term, tag in [
        ("Pregnancy", "pregnancy"),
        ("Lactation", "lactation"),
        ("Breast Feeding", "lactation"),
        ("Infant, Newborn", "neonate"),
        ("Infant", "infant"),
        ("Child", "child"),
        ("Adolescent", "adolescent"),
    ]:
        if term in mesh:
            tags.append(tag)
    source = item.get("source", "")
    if "LactMed" in source:
        tags = ["lactation"]
    elif "DailyMed 8.1" in source:
        tags = ["pregnancy"]
    raw = item.get("population")
    return population_context(
        requested,
        list(dict.fromkeys(tags)) or raw or "not_established",
        "Source MeSH/label section or original population field; missing stays unknown.",
    )
