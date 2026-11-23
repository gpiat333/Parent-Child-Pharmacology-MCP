"""Summary view of an evidence brief: the same findings, sized for a model's context.

The full brief repeats long source text for every passage. The summary keeps every axis,
every count and every gap statement, shows the first few passages per list, and says exactly
what was left out and how to get it. Nothing is reworded and no passage is merged.
"""

PASSAGES_PER_LIST = 5
ROWS_PER_SOURCE = 5
LISTS = ("items", "context_only", "reported_gaps")
PASSAGE_FIELDS = (
    "text",
    "source",
    "url",
    "pmid",
    "evidence_kind",
    "study_context",
    "contains_dose_text",
)
PASSAGE_NOTICE = (
    "Passages are source text grouped heuristically, not adjudicated clinical findings. Search "
    "filters and broad population labels do not confirm that a passage applies to the requested "
    "population; preserve actual ages, prematurity and gestational stage. Study counts and designs "
    "are not established from these extracts. Source context for each passage is available with "
    "detail='full'."
)
# Per source: long text fields to leave out, and the fields kept for each listed record.
DROPPED_TEXT = {
    "lactmed": (
        "text",
        "sections",
        "references",
        "section_population_context",
        "source_balance_context",
        "content_flags",
    ),
    "label": (
        "sections",
        "pllr_8_1",
        "section_population_context",
        "product_description",
        "approved_use_sections",
        "content_flags",
    ),
    "literature": ("articles", "searches", "query_strategy", "search_metadata", "content_flags"),
    "adverse_events": ("content_flags",),
    "trials": ("content_flags",),
    "patient_info": ("content_flags",),
}
# Notices that annotation repeats on every source; the brief states each once at the top.
REPEATED_NOTICES = (
    "framing_contract",
    "continuity_of_care_notice",
    "pregnancy_coverage_notice",
    "evidence_status",
)
ROW_FIELDS = {
    ("literature", "results"): ("pmid", "title", "journal", "year", "publication_types", "url"),
    ("trials", "studies"): ("nct", "title", "status", "results_posted", "url"),
    ("adverse_events", "top_reactions"): ("reaction", "reports"),
    ("patient_info", "topics"): ("title", "url"),
    ("patient_info", "drug_info"): ("title", "url"),
    ("pediatric_labeling_changes", "results"): (
        "labeling_change_date",
        "trade_name",
        "legislation",
        "indication",
        "url",
    ),
    ("bpca_study_summaries", "results"): ("title", "url"),
}


def _passage(item):
    slim = {k: item[k] for k in PASSAGE_FIELDS if item.get(k) is not None}
    population = (item.get("population_context") or {}).get("source_population")
    if population:
        slim["source_population"] = population
    return slim


def _axis(axis):
    out = {k: v for k, v in axis.items() if k not in LISTS}
    omitted = {}
    for name in LISTS:
        passages = axis.get(name) or []
        out[name] = [_passage(p) for p in passages[:PASSAGES_PER_LIST]]
        out[name + "_total"] = len(passages)
        if len(passages) > PASSAGES_PER_LIST:
            omitted[name] = len(passages) - PASSAGES_PER_LIST
    out["omitted_in_summary"] = omitted
    return out


def _source(name, payload):
    if not isinstance(payload, dict):
        return payload
    dropped = [k for k in DROPPED_TEXT.get(name, ()) if k in payload]
    out = {k: v for k, v in payload.items() if k not in dropped and k not in REPEATED_NOTICES}
    for (source, key), fields in ROW_FIELDS.items():
        rows = out.get(key)
        if source != name or not isinstance(rows, list):
            continue
        out[key] = [
            {f: row.get(f) for f in fields if f in row} if isinstance(row, dict) else row
            for row in rows[:ROWS_PER_SOURCE]
        ]
        out[key + "_total"] = len(rows)
    measurements = out.get("exposure_measurements")
    if isinstance(measurements, dict):
        passages = measurements.get("concentration_passages") or []
        out["exposure_measurements"] = {
            **measurements,
            "concentration_passages": passages[:PASSAGES_PER_LIST],
            "concentration_passages_total": len(passages),
        }
    if dropped:
        out["omitted_in_summary"] = dropped
    return out


def summarize(brief):
    """Return the summary view of an annotated brief. Stops and refusals pass through."""
    if "ingredient_evidence" not in brief:
        return brief
    out = dict(brief)
    out["evidence_axes"] = [
        {**axis, "by_ingredient": [_axis(row) for row in axis.get("by_ingredient", [])]}
        for axis in brief.get("evidence_axes", [])
    ]
    rows = []
    for row in brief["ingredient_evidence"]:
        slim = {k: _source(k, v) for k, v in row.items() if k != "content_flags"}
        participation = slim.get("participation")
        if isinstance(participation, dict) and isinstance(
            participation.get("recruiting_studies"), dict
        ):
            slim["participation"] = {
                **participation,
                "recruiting_studies": _source("trials", participation["recruiting_studies"]),
            }
        rows.append(slim)
    out["ingredient_evidence"] = rows
    priorities = out.get("research_priorities_context")
    if isinstance(priorities, dict):
        # Keep why the gap matters and where to read it; the 15 recommendations are in the full view.
        out["research_priorities_context"] = {
            k: priorities[k] for k in ("framework", "why_shown", "links") if k in priorities
        } | {"recommendations": "Listed with detail='full'."}
    out["detail"] = "summary"
    out["passage_notice"] = PASSAGE_NOTICE
    out["coverage_notice"] = (
        f"Summary view: at most {PASSAGES_PER_LIST} passages per axis list and {ROWS_PER_SOURCE} "
        "records per source, with source text left out. Each list reports its total and "
        "omitted_in_summary names what was left out. This is not the complete retrieved "
        "evidence: call again with detail='full', or use the single-source tools, before "
        "describing findings as complete."
    )
    return out
