> Historical feature/design note. Current .11 status, metrics and runtime boundaries are in [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md).

# Tool migration

Current local protocol (0.22.0): 21 tools, four prompts, five resources. Not deployed; the hosted App still runs the 31-tool .27 build. See [November 23 consolidation](#november-23-consolidation-0200).

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

## November 23 consolidation (0.20.0)

Nine tools were merged into goal-level tools, taking the catalog from 31 to 24. Old names are not registered aliases. Historical traces and evaluation reports keep the names that were actually called.

| Former tool | Current interface |
|---|---|
| search_lactmed, then get_lactmed_record | get_lactmed_record with `drug`; when several records match it returns candidates and is called again with `book_id` |
| semantic_search_lactmed | Removed; it returned `not_enabled` in every tested deployment |
| search_medication_recalls | search_fda_drug_notices with `kind="recalls"` |
| search_drug_safety_alerts | search_fda_drug_notices with `kind="safety_communications"` |
| search_drug_shortages | search_fda_drug_notices with `kind="shortages"` |
| get_reporting_resources | search_fda_drug_notices with `kind="reporting_links"`, and the `parent-child://reporting-resources` resource |
| search_pregnancy_registries | find_pregnancy_exposure_registries; `drug` is optional and an empty value lists the directory |
| search_bpca_evidence | search_nichd_resources with `source="bpca_summaries"` |
| search_nichd_studies | search_nichd_resources with `source="dash_studies"` |

`medication_evidence_brief` gains `detail`. The default `summary` returns every evidence axis with totals, the first five passages per list and compact source records, and names what it left out; `full` returns every passage and the source text. Both companion clients count `*_total` fields so the three-axis inventory reports all retrieved passages. The `evidence` field now lists the top-level field names instead of repeating them, and per-ingredient axes are returned once, under top-level `evidence_axes`.

Not changed: `get_parent_medication_info` and `search_parent_input_opportunities` stay registered because evaluation cases D01, R03 and R08 depend on them. The 0.20.0 source has not been re-run through the chat, paired or benchmark evaluations.

## November 23 second consolidation (0.21.0)

Three more tools were folded in or removed, taking the catalog from 24 to 21. This supersedes the "Not changed" note above.

| Former tool | Current interface |
|---|---|
| get_parent_medication_info | medication_evidence_brief; the summary keeps the label's `medicine_taker_sections` beside the LactMed infant findings |
| find_recruiting_studies | search_trials with `recruiting_only=true` and optional `location`; results are an unranked participation listing |
| search_parent_input_opportunities | Removed with its Federal Register client; `www.federalregister.gov` is no longer on the outbound allowlist |

Tool descriptions now say only what a tool does and when to choose it. The longer guidance on how to write an answer from a result is returned with each non-stop result as `answer_rules`. Evaluation case R08 (public-input notices) is retired, leaving 27 cases: 20 research and 7 stops. `search_trials` takes an optional `population`; when omitted it is pregnancy for the research landscape and any for recruiting studies. The study-team confirmation notice now attaches to every `search_trials` result.

## Typed results and trials default (0.22.0)

No tool was added or removed. Seven tools now advertise their own result fields on top of the shared envelope: `route_parent_question`, `normalize_drug`, `get_lactmed_record`, `search_literature`, `get_abstracts`, `search_trials` and `medication_evidence_brief`. Every tool-specific field is optional, because safety stops, identity stops and source failures return the envelope without them; fields a result did not set are left out instead of being returned as nulls. Source records keep any extra fields their source provides. The other 14 tools still share the plain envelope.

`search_trials` no longer applies a pregnancy filter when `population` is omitted, which supersedes the note in the previous section. The default is `any` in both modes; set `population` to limit the search.
