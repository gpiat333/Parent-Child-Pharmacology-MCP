# Current request: completion and limits

No deployment, push, provider configuration change or external submission occurred.

| Request | Current implementation / evidence |
|---|---|
| English false positive | Context-aware English question checks and separate scientific selectors; original D05 and all 24 final routes pass. Spanish/mixed-language regression tests retained. |
| Rerun chats and comparison | Frozen source; 24 chats, seven paired questions, all 14 paired answers retained. Diagnostic grades and errors documented. |
| Update deck and DOCX | Current figures and grading limitations in the 52-slide deck (15 main) and 10-page GSA-template DOCX. |
| 28: three axes | Exactly three rows per ingredient: maternal effects, measured fetal/infant exposure, observed fetal/infant outcomes. Empty rows visible; animal/model/recommendation context separated. |
| 29: PLLR subsections | Risk Summary, Clinical Considerations and Data parsed, with optional registry subsection. Clinical Considerations and its dose-adjustment subheading are preserved as source text. |
| 30: maternal PK | Clinical Considerations and retrieved abstract candidates; citations and explicit no-data state. No personal dose or automatic confirmation of human applicability. |
| 31: MeSH strategies | Versioned pregnancy/lactation population and focus strategies; substance-name/title-abstract fallbacks, no arbitrary year cutoff, translation/warnings/counts retained. |
| 32: FDA registry tool | `find_pregnancy_exposure_registries(drug)` returns listed contacts, links, status and non-recommendation. Older registry interface remains compatible. |
| 33: participation | Registry, recruiting-study and public-input tools share an unranked tier. Mandatory preflight suppresses participation and retrieval on urgent/crisis/identity stops. Stateless tools cannot infer omitted conversational context. |
| 34: LactMed scope | Current tool descriptions, README, deck, evaluation and video explicitly describe lactation-only scope. Historical raw traces remain unchanged. |
| 35: DART/TOXNET | NLM retirement/transition/filter sources verified and linked in PREGNANCY_EVIDENCE.md. No unsupported all-records migration or current DART-connection claim. |
| 36: gaps slide | Main-flow slide grounds gaps in PRGLAC, BPCA and PREA; the tool surfaces gaps rather than closing them. |
| 37: gap demo | Daridorexant pre-tested; one-screen evidence/gap/registry contacts. Empty axes scoped to bounded label/abstract extraction; FAERS signals separate. Lamotrigine supplies a PK contrast. |

395 unit tests pass. Grading errors and actual answer shortcomings remain disclosed in REPORT.md and grading-review.json. No clinician review or clinical certification. Historical evaluations are not pooled with current results.
