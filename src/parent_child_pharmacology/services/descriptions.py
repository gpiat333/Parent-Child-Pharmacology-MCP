"""Consistent selection guidance while retaining source-specific limitations."""

WORKFLOW_TOOLS = {
    "route_parent_question",
    "medication_evidence_brief",
    "check_evidence_coverage",
    "summarize_research_portfolio",
}
GUIDANCE = {
    "search_trials": (
        "The research landscape of trials on a medicine or condition, or studies recruiting now.",
        "Eligibility decisions, enrollment, or evidence that a treatment works.",
    ),
    "medication_evidence_brief": (
        "A cross-source brief for pregnancy, breastfeeding or a child, including focused parent questions.",
        "A single-source lookup, where the specific source tool is smaller and faster.",
    ),
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
}


# What each tool does, for choosing between tools. How to write the answer from a result is
# not repeated here: each result carries the tool's full answer_rules.
SUMMARY = {
    "route_parent_question": "Safety and scope check for a user's question. Call it first, on the question as written. Returns allow_research plus a fixed message and referrals for emergencies, crisis, dosing or treatment decisions, unclear medicine identity, privacy and non-English text. Rule-based, not clinical triage.",
    "normalize_drug": "Resolve a brand name, misspelling or combination product to its generic ingredients and RxNorm ID. found=false or requires_confirmation=true means the identity is unconfirmed: ask the user, never substitute.",
    "find_products_containing_ingredient": "List RxNorm products that contain one confirmed ingredient, to spot the same ingredient across products. Identity information only; not a dose or safety check.",
    "get_patient_education": "MedlinePlus patient education links for a health topic or medicine. Spanish needs a confirmed RxNorm ID.",
    "get_lactmed_record": "Read the LactMed (NLM) breastfeeding record for a medicine or vaccine by name: drug levels in milk, effects in breastfed infants and on lactation, with links to the cited studies. Lactation only. When several records match, returns candidates to choose by book_id.",
    "search_mothertobaby_fact_sheets": "Find MotherToBaby consumer fact sheets on a medicine or exposure in pregnancy and breastfeeding, in English or Spanish, with word-for-word question-and-answer text. Nonprofit content distributed by NLM, not federal evidence.",
    "get_label_sections": "FDA product label (DailyMed): pregnancy, lactation and pediatric-use sections, adult adverse reactions and warnings, ingredients and approved uses, from one matching label.",
    "search_pediatric_labeling_changes": "FDA's history of pediatric labeling changes under BPCA and PREA, by generic or trade name.",
    "find_pregnancy_exposure_registries": "FDA-listed pregnancy exposure registries for a confirmed medicine, or the directory listing. Unranked participation information, never a recommendation.",
    "search_literature": "Search PubMed for a medicine, with curated pregnancy and lactation strategies and optional focus, publication-type and date filters. Returns citations, not findings: fetch abstracts before describing results.",
    "get_abstracts": "Abstracts and PubMed links for up to 10 PMIDs, with a report of which abstracts were missing.",
    "search_trials": "Search ClinicalTrials.gov: the research landscape across all statuses (default), one study by NCT ID, or studies recruiting now with eligibility and contacts (recruiting_only=true), listed unranked and never recommended.",
    "find_mprint_records": "Find curated MPRINT pharmacology studies by drug or PMID in a dated snapshot. With check_for_updates=true, checks live whether MPRINT has published newer data.",
    "get_mprint_details": "Aggregate outcome rows, or automated study-type labels, for one MPRINT study by PMID. No individual-patient data.",
    "search_funded_research": "Search NIH RePORTER for funded projects on a topic, across institutes or one institute (HD is NICHD), with fiscal-year, activity-code and organization filters. NIH only.",
    "summarize_research_portfolio": "Aggregate NIH RePORTER projects on a topic by institute and fiscal year: counts and award totals. NIH only; check complete_result_set before calling totals complete.",
    "search_nichd_resources": "Search NICHD resources: BPCA and Pediatric Trials Network study-summary links, or public DASH study descriptions. Index and metadata, not study results.",
    "get_adverse_event_signals": "Most-reported reactions in FDA adverse-event reports (FAERS) for a medicine, optionally for pregnancy-exposure or infant reports. Counts of spontaneous reports, not rates or proof of causation.",
    "search_fda_drug_notices": "FDA notices about a medicine: recalls, safety communications, shortages, or where to report a problem (MedWatch). Choose one kind.",
    "medication_evidence_brief": "Build a cross-source evidence brief for a medicine in pregnancy, breastfeeding or a child: three evidence axes with gaps shown, plus label, LactMed, literature, trial and adverse-event context. Also for focused parent questions about side effects versus infant findings. Summary by default; detail='full' returns all text.",
    "check_evidence_coverage": "Count how much each source has for a medicine and population before a full search. Counts only; not evidence quality or safety.",
}


def answer_rules(original):
    """The tool's full guidance for writing an answer, returned with each result."""
    return " ".join((original or "").split())


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
        f"Does: {SUMMARY[name]}\nUse when: {use}\nNot for: {avoid}\n"
        f"First/next: {first}\nReturns: The shared evidence envelope described in the server "
        "instructions, with answer_rules to follow when writing from the result. "
        f"Missing evidence never means safe. Tier: {tier}."
    )
