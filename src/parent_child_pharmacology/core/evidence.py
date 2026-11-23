"""Machine-readable interpretation limits, distinct from source-authored evidence."""

import re

PREGNANCY_NOTICE = {
    "curated_federal_pregnancy_counterpart_to_lactmed": "not_identified_in_prototype_source_review",
    "evidence_sources": ["product labeling", "primary literature"],
    "message": "This prototype did not identify a curated federal pregnancy counterpart to LactMed. Pregnancy findings come from product labeling and primary literature; coverage is not exhaustive. LactMed is a lactation resource, not a pregnancy evidence substitute.",
    "basis_urls": [
        "https://www.ncbi.nlm.nih.gov/books/NBK501922/",
        "https://www.fda.gov/drugs/labeling/questions-and-answers-pregnancy-and-lactation-labeling-rule",
    ],
    "finding_scope": "Source-review finding, not proof that no such resource could exist.",
}


def clinician_questions(population):
    return [
        "Does this evidence apply to my exact medicine, formulation, and all active ingredients?",
        f"How closely do the study populations match the {population} context, including age and prematurity where relevant?",
        "Which findings measure exposure, and which measure clinical outcomes?",
        "What uncertainties or missing evidence should we discuss before making a treatment decision?",
        "What questions about benefits, risks, and follow-up should we address together?",
    ]


COLLECTIONS = (
    "results",
    "articles",
    "studies",
    "projects",
    "publications",
    "topics",
    "drug_info",
    "top_reactions",
    "outcomes",
    "classifications",
    "records",
    "candidates",
    "patient_education_links",
)
CHILDREN = (
    "lactmed",
    "label",
    "literature",
    "adverse_events",
    "trials",
    "patient_info",
    "medicine_taker_label_evidence",
    "breastfeeding_evidence",
    "product_label",
)


def evidence_state(out):
    if out.get("allow_research") is False or out.get("requires_confirmation"):
        state = "not_retrieved"
    elif out.get("status") == "not_applicable":
        state = "not_applicable"
    else:
        observations = []
        for key in COLLECTIONS:
            if isinstance(out.get(key), list):
                observations.append(bool(out[key]))
        for key in ("text", "sections", "abstract"):
            if key in out:
                observations.append(bool(out[key]))
        for key in CHILDREN:
            if isinstance(out.get(key), dict):
                observations.append(evidence_state(out[key])["state"] == "retrieved")
        for row in out.get("ingredient_evidence", []):
            observations.append(evidence_state(row)["state"] == "retrieved")
        if observations:
            state = "retrieved" if any(observations) else "none_retrieved"
        elif (
            out.get("error")
            or out.get("found") is False
            or out.get("available") is False
            or out.get("status") in {"no_results", "not_enabled"}
        ):
            state = "none_retrieved"
        else:
            state = "not_assessed"
    return {
        "state": state,
        "no_evidence_retrieved": state in {"none_retrieved", "not_retrieved"},
        "not_evidence_of_safety": True,
        "message": "No evidence retrieved; not evidence of safety."
        if state in {"none_retrieved", "not_retrieved"}
        else "Retrieved material is not a safety verdict; missing evidence is not evidence of safety.",
    }


DOSE = re.compile(
    r"\b(?:dos(?:e|es|ing|age)|administ(?:er|ered|ration)|taper|once daily|twice daily|every \d+ hours|(?:oral|intravenous|intramuscular|subcutaneous)\s+(?:use|route))\b|\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|μg|ml|milligrams?|micrograms?|units?)(?:\b|/)",
    re.I,
)
CATEGORY = re.compile(
    r"\bpregnancy\s*(?:risk\s*)?(?:category|categories)\s*[:\-]?\s*([ABCDX])\b|\bcategory\s+([ABCDX])\s+(?:in|for|during)\s+pregnancy\b",
    re.I,
)


def content_flags(out):
    dose_paths = []
    categories = []
    skip = {
        "safety",
        "disclaimer",
        "interpretation",
        "limitations",
        "rules",
        "note",
        "warning",
        "coverage_notice",
        "evidence_status",
        "content_flags",
        "pregnancy_coverage_notice",
        "questions_to_ask_clinician",
        "dose_content",
        "deprecated_pregnancy_categories",
        "evidence",
        "retrieval_provenance",
    }

    def walk(v, path):
        if isinstance(v, dict):
            for k, x in v.items():
                if k not in skip:
                    walk(x, path + "/" + str(k).replace("~", "~0").replace("/", "~1"))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, path + "/" + str(i))
        elif isinstance(v, str):
            if DOSE.search(v):
                dose_paths.append(path)
            for match in CATEGORY.finditer(v):
                categories.append({"path": path, "category": (match[1] or match[2]).upper()})

    walk(out, "")
    return {
        "dose_or_administration": {
            "detected": bool(dose_paths),
            "field_paths": dose_paths,
            "path_format": "JSON Pointer relative to this payload",
            "client_action": "Suppress flagged fields or visibly caveat them as historical source content, never personal instructions.",
            "detection_limit": "Heuristic; an unflagged field is not certified free of dosing content.",
        },
        "removed_pregnancy_letter_categories": {
            "detected": bool(categories),
            "matches": categories,
            "classification_current": False if categories else None,
            "instruction": "A/B/C/D/X pregnancy letter categories were removed by FDA PLLR. Preserve as historical source text only; never present as the current classification.",
            "source_url": "https://www.fda.gov/drugs/labeling/questions-and-answers-pregnancy-and-lactation-labeling-rule"
            if categories
            else None,
        },
    }


SOURCE_ATTRIBUTION_RULE = (
    "Report a source's warnings and recommendations as that source's statements (\"The label states "
    'that..."), never in your own voice as an instruction to the reader. When saying whom to check with, '
    "name only the contacts the results name."
)


def annotate(out, requested_population=None):
    out = dict(out)
    from .source_context import (
        CONTINUITY_NOTICE,
        item_population,
        population_context,
    )

    requested_population = requested_population or out.get("population")
    # A summary brief was annotated in full before it was condensed. Annotating its sources
    # again would restore the per-source notices it left out, and would judge evidence
    # status from the condensed copy instead of from what was actually retrieved.
    condensed = out.get("detail") == "summary" and "evidence_status" in out
    retrieved_status = out.get("evidence_status") if condensed else None
    for key in CHILDREN:
        if isinstance(out.get(key), dict) and not condensed:
            out[key] = annotate(out[key], requested_population)
    if "ingredient_evidence" in out and not condensed:
        out["ingredient_evidence"] = [
            annotate(row, requested_population) for row in out["ingredient_evidence"]
        ]
    for key in COLLECTIONS:
        if isinstance(out.get(key), list):
            out[key] = [
                {
                    **row,
                    "population_context": row.get("population_context")
                    or item_population(row, requested_population),
                }
                if isinstance(row, dict)
                else row
                for row in out[key]
            ]
    if out.get("sections"):
        out["section_population_context"] = {
            k: population_context(
                requested_population,
                {
                    "pregnancy": "pregnancy",
                    "lactation": "lactation",
                    "pediatric_use": "pediatric",
                    "pregnancy_lactation": ["pregnancy", "lactation"],
                }.get(k, "medicine_taker_label_population"),
                "Explicit source section; confirm the exact product and actual population.",
            )
            for k in out["sections"]
        }
    if out.get("allow_research") is not False and not out.get("requires_confirmation"):
        out["continuity_of_care_notice"] = CONTINUITY_NOTICE
        out["framing_contract"] = {
            "preserve_source_balance_context": True,
            "clinical_framing_review_performed": False,
            "instruction": "When reporting adverse findings, retain relevant source context on treatment benefits, underlying disease and consequences of changing treatment if available. Disclose missing context; do not invent reassurance. Accurate facts can still induce inappropriate stopping. Clinical review remains necessary.",
            "source_attribution": SOURCE_ATTRIBUTION_RULE,
        }
    out["evidence_status"] = retrieved_status or evidence_state(out)
    out["content_flags"] = content_flags(out)
    if out.get("allow_research") is False or out.get("requires_confirmation"):
        from .participation import tier

        out["participation"] = tier(
            suppressed=True, reason=out.get("route") or "unconfirmed_identity"
        )
    if out.get("population") == "pregnancy" or any(
        k in (out.get("sections") or {}) for k in ("pregnancy", "pregnancy_lactation")
    ):
        out["pregnancy_coverage_notice"] = dict(PREGNANCY_NOTICE)
    return out
