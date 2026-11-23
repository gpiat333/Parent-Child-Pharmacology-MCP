> Historical feature/design note. Current .11 status, metrics and runtime boundaries are in [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md).

# Safety and evidence contracts

Policy `2026-11-21.4`. No prescribing or personal treatment decisions; no clinical triage; no exhaustive evidence or safety guarantee; no clinical certification.

## Routing

The companion client calls the preflight before any model completion. Recognized hopelessness, self/infant-harm intent, intentional overdose and postpartum depression/psychosis wording returns fixed guidance with `allow_research=false`, `allow_model_answer=false` and `clinical_assessment_performed=false`. US crisis referrals use verified 988 call/text details. Relevant perinatal responses add PSI's non-emergency callback support, explicitly distinguished from crisis care. Intentional-overdose framing takes precedence over ordinary poison routing. Urgent/poison responses include Poison Help and 911; there is no risk score, severity assessment or diagnostic questioning. Other countries receive no invented number.

Offline checks require the whole question to meet either langdetect English >= .95 or Lingua English >= .80. Sentences and overlapping eight-word spans are checked too. An ambiguous fragment can inherit strong English context if English ranks first at >= .35, or if English scores >= .15 with at least two English function-word anchors. Confident foreign fragments cannot inherit context. Missing detectors or errors stop research. These scores are heuristics, not calibrated clinical confidence.

Short structured scientific selectors are data, not substitutes for the actual question. Controlled English scientific concepts may accompany a medicine name; other multiword selectors must not be confidently foreign. Actual questions always require preflight, and direct source fields still undergo intent and identity screening. Spanish sentences, including one passed through `drug`, remain blocked. The original English false positive and technical-selector failures passed the current 28-case rerun. Unseen, mixed-language and obfuscated inputs can still be missed or overblocked. Third-party clients must enforce the same stop behavior; metadata cannot force arbitrary clients to comply.

## Payload fields

| Field | Meaning |
|---|---|
| evidence_status | State, no_evidence_retrieved, not_evidence_of_safety and a fixed message. Empty child sources remain visible when others return records. |
| content_flags.dose_or_administration | JSON Pointer paths for dose/administration text. Suppress or caveat historical observations; never present as personal instructions. Detection can miss content. |
| content_flags.removed_pregnancy_letter_categories | Historical A/B/C/D/X text with classification_current=false; FDA PLLR removed these categories. |
| report_count_interpretation | FAERS reports do not establish causation and lack exposure denominators; incidence or individual risk cannot be calculated. |
| questions_to_ask_clinician | MCP-authored preparation questions, also available as an MCP prompt; not source quotations or a treatment plan. |
| pregnancy_coverage_notice | This prototype's review did not identify a curated federal pregnancy counterpart to LactMed. Findings come from labeling and primary literature. This is a scoped finding, not proof of universal nonexistence. |

The brief researches every ingredient returned by a confirmed RxNorm identity and keeps evidence separated. It does not establish interactions or combination-product safety. Approximate identity stops first.

## Three axes, pregnancy and participation

The brief preserves maternal effects, measured fetal/infant exposure, and observed fetal/infant outcomes as three visible rows per ingredient, including empty rows. PLLR 8.1 subsections, maternal dose-adjustment source text and maternal PK candidates preserve citations and explicit absence. Human, animal, modeled and recommendation context remain distinct. Empty label/abstract rows are not evidence of absence of all human reports; FAERS remains a separate spontaneous-report source.

Pregnancy/lactation searches use curated MeSH strategies with source translation and warnings. LactMed is lactation-only. FDA registries, recruiting studies and public-input notices form an unranked participation tier, suppressed on urgent, crisis, unconfirmed-identity and other stop routes. A listing is not a recommendation or eligibility decision. See [pregnancy contracts and verified primary sources](PREGNANCY_EVIDENCE.md).

## Age bands and Spanish education

Prototype search conventions: neonate birth to under 28 days; infant 28 days to under 2 years; child 2 to under 12 years; adolescent 12 to under 18 years. These are not universal clinical boundaries. Broader pediatric remains for unspecified age. Preserve actual source age, gestational age and prematurity. PubMed uses distinct band terms; registry discovery requires numerical age overlap and retains the source bounds. MPRINT broad labels are not band-confirmed. Infant FAERS coverage cannot stand in for another band.

Spanish MedlinePlus is a code lookup: `language='es'`, confirmed `rxcui`, and an English question in `topic`, such as `What information is available in Spanish for sertraline?`. No Spanish free-text topic search or clinical chat is enabled. An English match does not guarantee a Spanish one.

RePORTER supports NICHD program staff discovering public awards by topic and linking to trial/literature records. Awards are not completed findings, performance ratings or an exhaustive portfolio. Public-input notices remain registered as appendix capability. The optional semantic LactMed tool returns `not_enabled` when inactive.

## Sources reviewed November 20 2026

988 details were supplied by the local hotline connector. PSI is non-emergency support.

- [MedlinePlus Connect](https://medlineplus.gov/medlineplus-connect/web-service/)
- [PSI support and callback service](https://postpartum.net/get-help/)
- [HRSA Poison Help](https://poisonhelp.hrsa.gov/what-you-can-do)
- [FDA PLLR](https://www.fda.gov/drugs/labeling/questions-and-answers-pregnancy-and-lactation-labeling-rule)
- [NLM LactMed scope](https://www.ncbi.nlm.nih.gov/books/NBK501922/)
- [openFDA limitations](https://open.fda.gov/apis/drug/event/)
- [Lingua methods](https://github.com/pemistahl/lingua-py)
- [langdetect seed and limitations](https://github.com/Mimino666/langdetect)

## Completeness and clinical framing revision

Expected/missing/returned sections, truncation, selected-label provenance, per-item source population and unknown study counts remain explicit. FAERS caveats and MPRINT dates remain in payloads. `continuity_of_care_notice` and `source_balance_context` support balanced framing, without personal treatment advice or invented reassurance. S2 and S6 remain partially controlled and need clinician review.

Spanish safety and referral messages were reviewed by a native Spanish speaker and enabled in policy .26 as fixed text (`message_es`); Spanish questions still stop. No clinical evidence is machine-translated. See [items 38–48 and S1–S6](PROGRAM_AND_SAFETY_REVISION.md) for complete fields, decisions and primary sources.

## Required evidence brief workflow

After an allowed preflight, an explicit brief request returns `requested_workflow.required_tool`. The companion requires that tool before optional retrieval or a final answer. A missing tool or bypass fails closed. Source confirmation and all stop rules remain active. Narrow intent matching and conservative language detection have limits; third-party clients must enforce the contract. See [workflow correction](BRIEF_WORKFLOW_REVISION.md).

## Fixed required notices

Allowed clinical evidence results expose a required clinical-framing-review notice; funding results expose the activity-code interpretation notice. The companion renders the trusted local texts after generation, with no additions on stopped routes. The paired MCP arm uses the same policy. Other clients must enforce the metadata. These notices are application contracts, not source findings or proof of clinical review. See [notice/citation correction](NOTICE_CITATION_REVISION.md).
