> Current status (November 21, 2026): the existing Databricks sandbox was updated; no GitHub push. See [current validation](DATABRICKS_VALIDATION.md). Prior counts and “no deployment” statements below describe earlier runs.

# Current local architecture

The client preflights the actual question before the model selects tools. `server.py` creates FastMCP and registers domain modules. Strict contracts live in `models/`, public-source adapters in `clients/`, and policy, language, evidence axes, MeSH strategy, content flags, provenance and audit in `core/`. Local evaluation uses loopback MCP, live public sources and versioned MPRINT snapshots. Nothing deployed or hosted.

After an allowed preflight, an explicit evidence-brief request returns a required workflow. The companion and MCP comparison arm require `medication_evidence_brief` first, then release optional source lookups. Safety, identity, privacy and language stops take priority. A missing required tool or a bypass attempt stops execution. Other requests retain automatic selection. Third-party clients must enforce this contract; see [workflow correction and limits](BRIEF_WORKFLOW_REVISION.md).

30 tools, four prompts and four resources. [Contracts](SAFETY_AND_EVIDENCE.md) describe mandatory client responsibilities. The participation tier contains both registry interfaces, recruiting studies and public-input notices. These are suppressed on stop routes and never ranked or recommended. RePORTER supports program-staff public portfolio discovery. LactMed is lactation-only.

The discovery tools add bounded portfolio summaries, count-only coverage, ingredient-product identity and FDA shortage records.

| Tool | Description |
|---|---|
| `normalize_drug` | Does: Resolve a brand name, misspelling or combination product to standard generic |
| `search_lactmed` | Does: Find LactMed (Drugs and Lactation Database, NLM) records by drug name. |
| `get_lactmed_record` | Does: Get LactMed text for one record: use during lactation, drug levels, effects on |
| `semantic_search_lactmed` | Does: Natural-language search over lactation-only LactMed record identifiers. |
| `search_literature` | Does: Search PubMed literature. Pregnancy/lactation use curated, versioned MeSH strategies with optional focus; no default date restriction. publication_type maps a small enum to PubMed types; date_from/date_to are inclusive publication-date bounds. These filters force live PubMed. Results retain source publication types, PMC IDs and availability-derived free/full-text fields; an ID alone is not proof of access. Pass a medicine name, not PubMed syntax. For other populations, 'keyword' hits live PubMed; |
| `get_abstracts` | Does: Get abstracts and canonical PubMed source URLs for up to 10 PubMed IDs. |
| `search_trials` | Does: Research landscape across trial statuses, including historical studies. Supply nct_id alone for a direct single-record fetch. Each record includes exact status and results_posted/has_results; completed does not mean results posted, and neither establishes benefit. |
| `search_funded_research` | Does: Search NIH RePORTER for funded projects (newest first) on a maternal/child topic. Optional IC enum (HD maps to NICHD), fiscal_years, exact activity_code and organization-name filters become reproducible query_criteria. Fiscal-year award obligations and direct costs remain separate; neither is lifetime project value. |
| `summarize_research_portfolio` | Does: Aggregate a bounded public RePORTER portfolio by administering IC and fiscal year. Return exact query criteria, counts, separate total-award/direct-cost sums and missing amounts. HD means NICHD. Subprojects are excluded. These are fiscal-year obligations, not lifetime project value or proof of performance; check complete_result_set before describing totals as complete. |
| `get_label_sections` | Does: FDA label (via DailyMed, NLM) pregnancy, lactation and pediatric-use sections. Returns pllr_8_1 with Risk Summary, Clinical Considerations, Data and a source-only maternal_dose_adjustment field, including explicit nulls. |
| `search_pediatric_labeling_changes` | Does: Search FDA historical pediatric labeling changes by generic or trade name. |
| `get_adverse_event_signals` | Does: Most frequently reported reactions in FDA FAERS (openFDA) for a drug, optionally for |
| `get_patient_education` | Does: MedlinePlus education links. Spanish is a structured drug-code lookup only: |
| `find_mprint_records` | Does: Find curated Gold study metadata by drug or exact PMID; one selector is required. |
| `get_mprint_details` | Does: Get aggregate curated Gold outcomes OR automated Silver classifications by PMID. |
| `search_bpca_evidence` | Does: Discover NICHD BPCA/PTN study-summary links by drug/title words. Returns index titles and links, NOT PDF contents or clinical conclusions. Empty query lists summaries. |
| `search_nichd_studies` | Does: Search public NICHD DASH study descriptions and publications, optionally MFMU or Neonatal Research Network. Zero-based pages. Controlled underlying datasets are NOT retrieved; access process is required. |
| `route_parent_question` | Does: Call FIRST for parent-facing requests, before evidence retrieval. Returns fixed |
| `get_parent_medication_info` | Does: Preferred for parent questions about side effects and breastfeeding infant findings. |
| `search_medication_recalls` | Does: FDA drug enforcement recall candidates, including historical records. Show |
| `search_drug_safety_alerts` | Does: Search titles on the current FDA Drug Safety Communications index. Returns |
| `find_recruiting_studies` | Does: Preferred for participation questions ("can I join a study?"). Use search_trials |
| `search_pregnancy_registries` | Does: FDA-listed pregnancy exposure registries: medicine/condition, registry, public |
| `find_pregnancy_exposure_registries` | Does: Participation tier: find FDA-directory pregnancy exposure registries for a confirmed |
| `search_parent_input_opportunities` | Does: Discover NIH/FDA Federal Register notices plus public-engagement directories. |
| `get_reporting_resources` | Does: Official navigation links for FDA MedWatch and NIH/FDA public involvement. |
| `medication_evidence_brief` | Does: Compile public evidence and questions to ask a clinician, never a safety verdict. |
| `check_evidence_coverage` | Does: Count-only source-presence/gap navigation before full evidence retrieval. Probe PubMed, trial registrations, lactation-only LactMed, labels and MPRINT row counts, with snapshot dates and caveats. No abstracts or clinical payloads. Counts cannot establish evidence quality or safety; unavailable is not zero. This is not clinical triage. Preflight the actual question first. |
| `find_products_containing_ingredient` | Does: Find RxNorm branded/clinical products containing one confirmed ingredient to help recognize possible duplicate-ingredient exposure across products used for children. Identity information only, not a dose calculation, dosing/safety check, substitution recommendation or verification of the package in hand. Confirm the ingredient first; lists are bounded and alphabetical. |
| `search_drug_shortages` | Does: Search FDA's public drug-shortage records by medicine and optional dosage form/status. Preserve presentation, availability and update dates: Current shortage status can include an Available presentation. No local pharmacy-stock, pediatric suitability, substitution, dosing or safety inference. |

Final-answer rendering appends applicable activity-code and clinical-review notices from trusted local policy, independently of generated prose. Stops receive no additions. The server exposes matching `required_display_notices`; third-party clients must enforce this contract. See [notice/citation correction](NOTICE_CITATION_REVISION.md).
