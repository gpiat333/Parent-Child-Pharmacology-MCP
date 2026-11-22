"""Consistent selection guidance while retaining source-specific limitations."""
WORKFLOW_TOOLS = {'route_parent_question', 'get_parent_medication_info', 'medication_evidence_brief','check_evidence_coverage','summarize_research_portfolio'}
GUIDANCE = {
 'search_trials': ('Research discovery across trial statuses.', 'Participation matching; use find_recruiting_studies.'),
 'find_recruiting_studies': ('Finding participation candidates.', 'Eligibility decisions or broad trial discovery; use search_trials for the latter.'),
 'find_mprint_records': ('Finding curated Gold snapshot metadata by drug or PMID.', 'Outcome values; use get_mprint_details.'),
 'get_mprint_details': ('Gold outcomes or Silver classifications by PMID and table enum.', 'Individual patient data or automatic clinical conclusions.'),
 'search_lactmed': ('Finding lactation-only LactMed record IDs for a drug.', 'Reading full evidence; follow with get_lactmed_record.'),
 'get_lactmed_record': ('Reading a known lactation-only LactMed record; not pregnancy evidence.', 'Searching by drug name; first use search_lactmed.'),
 'get_parent_medication_info': ('Focused parent evidence about side effects and infant exposure versus outcomes.', 'Broad research scans; use medication_evidence_brief.'),
 'medication_evidence_brief': ('A broader cross-source research brief.', 'Focused parent questions; use get_parent_medication_info.'),
 'semantic_search_lactmed': ('Vector retrieval only when the optional index is configured.', 'Default live-only deployment; use search_lactmed instead.'),
}

def description(name, original, domain):
    use, avoid = GUIDANCE.get(name, (f'{domain.replace("_", " ")} evidence requests within the scope below.', 'Personal treatment, dosing, diagnosis, or a safety verdict.'))
    first = 'Call route_parent_question on the actual question; confirm ambiguous medication identity with normalize_drug before evidence lookup.'
    if name == 'route_parent_question': first = 'Call first. If allow_research is false, honor the route and do not continue research.'
    return (f'Does: {(original or name).strip()}\nUse when: {use}\nNot for: {avoid}\n'
            f'First/next: {first}\nReturns: A structured evidence envelope with status, results, source_urls, '
            'coverage_limits, missing_fields, provenance, untrusted evidence, error and disclaimer. '
            'Missing evidence never means safe. Tier: '+('participation' if name in __import__('core.participation',fromlist=['TOOLS']).TOOLS else 'workflow' if name in WORKFLOW_TOOLS else 'building block')+'.')
