"""One-file-per-tool registration catalog."""

from importlib import import_module

DOMAINS = {
    "identity": ["normalize_drug"],
    "lactation": ["get_lactmed_record"],
    "literature": [
        "search_literature",
        "get_abstracts",
        "search_trials",
        "search_funded_research",
        "summarize_research_portfolio",
    ],
    "labels_safety": [
        "get_label_sections",
        "search_pediatric_labeling_changes",
        "get_adverse_event_signals",
        "get_patient_education",
    ],
    "mprint": ["find_mprint_records", "get_mprint_details"],
    "nichd": ["search_nichd_resources"],
    "parent_resources": [
        "route_parent_question",
        "search_fda_drug_notices",
        "find_pregnancy_exposure_registries",
        "search_mothertobaby_fact_sheets",
    ],
    "composite": ["medication_evidence_brief"],
    "discovery": [
        "check_evidence_coverage",
        "find_products_containing_ingredient",
    ],
}


def register_tools(mcp):
    return {
        name: import_module(__name__ + "." + name).register(mcp)
        for names in DOMAINS.values()
        for name in names
    }
