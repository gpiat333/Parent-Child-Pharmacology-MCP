"""One-file-per-tool registration catalog."""

from importlib import import_module

DOMAINS = {
    "identity": ["normalize_drug"],
    "lactation": ["search_lactmed", "get_lactmed_record", "semantic_search_lactmed"],
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
    "nichd": ["search_bpca_evidence", "search_nichd_studies"],
    "parent_resources": [
        "route_parent_question",
        "get_parent_medication_info",
        "search_medication_recalls",
        "search_drug_safety_alerts",
        "find_recruiting_studies",
        "search_pregnancy_registries",
        "find_pregnancy_exposure_registries",
        "search_parent_input_opportunities",
        "get_reporting_resources",
    ],
    "composite": ["medication_evidence_brief"],
    "discovery": [
        "check_evidence_coverage",
        "find_products_containing_ingredient",
        "search_drug_shortages",
    ],
}


def register_tools(mcp):
    return {
        name: import_module(__name__ + "." + name).register(mcp)
        for names in DOMAINS.values()
        for name in names
    }
