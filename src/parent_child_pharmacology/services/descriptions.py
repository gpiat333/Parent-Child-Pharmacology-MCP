"""Consistent selection guidance while retaining source-specific limitations."""

WORKFLOW_TOOLS = {
    "route_parent_question",
    "get_parent_medication_info",
    "medication_evidence_brief",
    "check_evidence_coverage",
    "summarize_research_portfolio",
}
GUIDANCE = {
    "search_mothertobaby_fact_sheets": (
        "Consumer fact sheets on a medicine or exposure in pregnancy or breastfeeding, including Spanish.",
        "Medicines given to children, clinical evidence synthesis, or summarizing sheet text not retrieved.",
    ),
    "search_funded_research": (
        "Who funds or what NIH funds on a topic: projects, institutes, investigators, awards.",
        "Evidence about a medicine's effects. Covers NIH only; say so when asked about funders generally.",
    ),
    "summarize_research_portfolio": (
        "Which NIH institutes fund a topic and how much, by fiscal year.",
        "Evidence about a medicine's effects. Covers NIH only; FDA, CDC, PCORI, foundations and industry are not included.",
    ),
    "search_trials": (
        "Research discovery across trial statuses.",
        "Participation matching; use find_recruiting_studies.",
    ),
    "find_recruiting_studies": (
        "Finding participation candidates.",
        "Eligibility decisions or broad trial discovery; use search_trials for the latter.",
    ),
    "find_mprint_records": (
        "Finding curated Gold snapshot metadata by drug or PMID.",
        "Outcome values; use get_mprint_details.",
    ),
    "get_mprint_details": (
        "Gold outcomes or Silver classifications by PMID and table enum.",
        "Individual patient data or automatic clinical conclusions.",
    ),
    "get_lactmed_record": (
        "Reading the lactation-only LactMed record for a medicine or vaccine, by name.",
        "Pregnancy or pediatric-use evidence; LactMed covers breastfeeding only.",
    ),
    "search_fda_drug_notices": (
        "FDA recalls, safety communications, shortages, or where to report a medication problem.",
        "Evidence about a medicine's effects, or clearing a specific bottle or lot.",
    ),
    "search_nichd_resources": (
        "Finding NICHD BPCA/PTN study summaries or public DASH study descriptions.",
        "Study results or participant-level data; these are index and metadata records.",
    ),
    "find_pregnancy_exposure_registries": (
        "Finding FDA-listed pregnancy exposure registries for a confirmed medicine.",
        "Eligibility, enrollment or any recommendation to join.",
    ),
    "get_parent_medication_info": (
        "Focused parent evidence about side effects and infant exposure versus outcomes.",
        "Broad research scans; use medication_evidence_brief.",
    ),
    "medication_evidence_brief": (
        "A broader cross-source research brief.",
        "Focused parent questions; use get_parent_medication_info.",
    ),
}


def description(name, original, domain):
    from parent_child_pharmacology.core.participation import TOOLS as PARTICIPATION_TOOLS

    use, avoid = GUIDANCE.get(
        name,
        (
            f"{domain.replace('_', ' ')} evidence requests within the scope below.",
            "Personal treatment, dosing, diagnosis, or a safety verdict.",
        ),
    )
    first = "After route_parent_question allows research; confirm an unclear medicine with normalize_drug."
    if name == "route_parent_question":
        first = (
            "Call first. If allow_research is false, honor the route and do not continue research."
        )
    tier = (
        "participation"
        if name in PARTICIPATION_TOOLS
        else "workflow"
        if name in WORKFLOW_TOOLS
        else "building block"
    )
    return (
        f"Does: {(original or name).strip()}\nUse when: {use}\nNot for: {avoid}\n"
        f"First/next: {first}\nReturns: The shared evidence envelope described in the server "
        f"instructions. Missing evidence never means safe. Tier: {tier}."
    )
