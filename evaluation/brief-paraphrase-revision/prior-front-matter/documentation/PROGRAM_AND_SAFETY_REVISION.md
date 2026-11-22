> Current status (November 21, 2026): the existing Databricks sandbox was updated; no GitHub push. See [current validation](DATABRICKS_VALIDATION.md). Prior counts and “no deployment” statements below describe earlier runs.

> Historical implementation milestone at 445 tests. The research features and safety fields below remain active. Current 508-test results: [notice/citation correction](NOTICE_CITATION_REVISION.md).

# Program discovery and safety revision

Local GSA hackathon prototype, November 21, 2026. Not an official NIH MCP tool. No production-readiness claim or deployment.

The final source adds a regression for the English selector `lamotrigine maternal serum cord blood pregnancy` and removes a legacy unreviewed Spanish sentence from the language-stop message. Whole-question preflight and conservative non-English handling remain active. The earlier 443-test run is historical in `evaluation/program-safety-initial`; the final suite has 445 tests and is evaluated again on a fresh source freeze.

## Build items

| Item | Implementation | Scope or limit |
|---|---|---|
| RePORTER filters | Existing `search_funded_research` accepts IC enum, fiscal-year array, activity code and organization | Input `HD` maps to upstream `NICHD`; live API requests using `HD` directly returned no matches |
| 38 | `summarize_research_portfolio` groups by administering IC and fiscal year, with counts and separate award/direct/indirect sums | Exact criteria, missing values, application IDs, total matches and boundedness retained; fiscal-year amounts, not lifetime value; source money fields need not reconcile |
| 39 | Publication-type enum and date-range filters on literature search | Native PubMed publication types; valid calendar dates and ordering required; source indexing is not quality assessment |
| 40 | PMC ID/link, free-full-text flag, OA license flag and paywall indicator | Availability derives from PubMed's free-text subset; OA license from PMC service. PMC ID alone is not proof of free access. No verified free link does not prove a paywall |
| 41 | `search_trials` accepts either a query or an NCT ID; records carry overall status and results-posted flag | Missing flag stays unknown. Completion/recruitment is not proof of results or benefit |
| 42 | SPL version, effective date, labeler, set ID and selection basis | First extractable label among at most five API-ordered matches; not a newest-label or exact-product claim. In-use labeling caveat retained |
| 43 | LactMed alternatives explicitly excluded | Parser recognizes Alternate Drugs to Consider, but returned clinical text and synthesis omit it; tool description states this |
| 44 | `check_evidence_coverage` returns count/presence metadata across five sources | No clinical payload or triage. Failed source is unknown, not zero. MPRINT Gold counts include snapshot revision/date. Counts are not comparable units |
| 45 | `find_products_containing_ingredient` returns RxNorm related SCD/SBD products for a confirmed single ingredient | Duplicate-ingredient identity navigation, not a dose or safety check; bounded, not every marketed product |
| 46 | `search_drug_shortages` uses verified federal openFDA endpoint | Status and presentation availability are separate. No local stock, pediatric suitability or substitution inference |
| 47 | Conservative language detection and fail-closed research remain active; existing code-based Spanish MedlinePlus education retained | No translated labels, LactMed or abstracts. New Spanish safety/referral strings held |
| 48 | Human-review gate honored | No human Spanish review supplied. New Spanish safety strings remain disabled. Review is the top language next step |

Activity codes describe funding mechanisms. They do not by themselves establish sustained investment, research success or program performance. RePORTER organization matching uses the upstream partial-name behavior. Aggregation excludes subprojects and deduplicates application/fiscal-year records; it cannot reconcile all accounting differences or establish a complete portfolio when capped.

## Six clinical safety risks

| Risk | Implemented payload/client controls | Remaining limitation |
|---|---|---|
| S1 Partial retrieval presented as complete | Expected/found/missing/returned/omitted sections, per-section truncation, label selection, confirmed-ingredient fan-out | Parser errors or relevant unqueried sources can remain |
| S2 Absence or no-effects wording presented as safety | Explicit absence fields, no-effects flag, indexed/mentioned study types, unknown study count | No validated study counting, evidence quality or clinical reassurance assessment; partial control |
| S3 Population mismatch | Source population on every evidence item, separate requested population, neonate/infant/child/adolescent selectors | Indexing and heuristics do not confirm applicability, prematurity or developmental equivalence |
| S4 Counts misread as rates | FAERS causation and denominator caveats travel in payload | Counts cannot establish incidence, individual risk or causal effects |
| S5 Superseded information presented as current | Legacy-category flags, SPL provenance, MPRINT snapshot date/revision | In-use labels may lag FDA-approved labeling; freshness is not guaranteed |
| S6 Discontinuation harm from asymmetric salience | Relevant source context, missing-context disclosure, standing medication-change caution, two framing evaluations | Accurate wording can still alarm. Source context is not a personal benefit-risk judgment. Clinical review required; partial control |

S2 and S6 require review of actual answers by a clinician. Code tests cannot establish whether a factually accurate sentence gives a misleading clinical impression. No clinical review or certification has occurred. The implementation does not invent study counts, reassurance or balancing context when missing.

## Current evaluation

See [current report](../evaluation/program-safety-revision/REPORT.md), [raw metrics](../evaluation/program-safety-revision/summary.json), [source freeze](../evaluation/program-safety-revision/source-freeze.json), and [grader changes](../evaluation/program-safety-revision/GRADER_CHANGE.md). New S6 case IDs are `S6-lactation` and `S6-pregnancy`. Initial rate-limited attempts are retained separately; they are not silent passes.

The previous revision and matching source snapshot remain under `evaluation/evidence-revision`. Its scores are historical. New tests, expanded cases and revised diagnostic grading prevent a direct improvement claim.

## Verified primary sources

- [RePORTER v2 API](https://api.reporter.nih.gov/?urls.primaryName=V2.0) and [data elements](https://api.reporter.nih.gov/documents/Data%20Elements%20for%20RePORTER%20Project%20API_V2.pdf): request filters, administering IC and monetary fields. Live probes verify `HD` to `NICHD` mapping.
- [PubMed help](https://pubmed.ncbi.nlm.nih.gov/help/) and [PMC OA service](https://pmc.ncbi.nlm.nih.gov/tools/oa-service/): publication type/date filters and availability metadata.
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api): single-study fetch and results-posted metadata.
- [DailyMed web services](https://www.dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm): SPL identity, document content and history.
- [RxNorm related concepts by type](https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getRelatedByType.html): related clinical/branded drug products.
- [openFDA drug shortages](https://open.fda.gov/apis/drug/drugshortages/): verified endpoint `https://api.fda.gov/drug/shortages.json`, with status, availability, presentation, dates and company fields. Live response retained with the protocol probes.

These are source/implementation observations, not clinical endorsement or production readiness.
