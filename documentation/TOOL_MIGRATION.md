> Historical feature/design note. Current .11 status, metrics and runtime boundaries are in [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md).

# Tool migration

Current local protocol: 30 tools, four prompts, four resources. No deployment.

| Former name | Current interface |
|---|---|
| medication_safety_brief | medication_evidence_brief |
| search_mprint_gold | find_mprint_records with drug or pmid |
| get_mprint_gold_outcomes | get_mprint_details with pmid and table=gold_outcomes, gold_PE_CT or gold_PK_summary |
| get_mprint_silver_classifications | get_mprint_details with one pmid and table=silver_classifications; iterate for multiple IDs |
| search_mprint | Removed keyword proxy; use search_funded_research or search_literature, labeling inferred relevance explicitly |

Old names are not registered aliases. Gold and Silver are not silently substituted. Current traces in `evaluation/program-safety-revision/` use current names. Historical raw traces are intentionally unchanged: renaming an executed call would misrepresent the record. The previous comparison used 27 tools. Public-input notices remain registered; the new clinician-question prompt supplements the three prior prompts.

`find_pregnancy_exposure_registries(drug)` is added for the FDA directory. The existing `search_pregnancy_registries` remains compatible. These two registry interfaces, recruiting studies and public-input notices are participation tools, unranked and never recommended. `search_literature` adds a focus enum and curated pregnancy/lactation strategies. The brief adds three axes, PLLR subsections and maternal PK fields.

## November 21 additions

Four tools were added: `summarize_research_portfolio`, `check_evidence_coverage`, `find_products_containing_ingredient`, and `search_drug_shortages`. RePORTER filters, literature type/date filters and NCT fetch are parameters on existing tools. LactMed alternatives are explicitly excluded. See [contracts and limits](PROGRAM_AND_SAFETY_REVISION.md).

## Required brief routing

No tool was added in the 473-test revision. Explicit brief requests now require `medication_evidence_brief` first after an allowed preflight. See [workflow correction](BRIEF_WORKFLOW_REVISION.md).

## Required output notices and citation checks

No tool was added in the 508-test revision. Allowed tool payloads now expose `required_display_notices`; the companion and paired MCP arm render the corresponding fixed policy text. The deterministic URL checker now separates adjacent Markdown citations. See [correction and limits](NOTICE_CITATION_REVISION.md).
