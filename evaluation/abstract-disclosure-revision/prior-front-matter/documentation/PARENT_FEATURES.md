> Current status: policy .9 is unchanged; grader v3 replays the same answers and evidence. 562 server and 30 evaluator tests pass locally. No deployment or GitHub upload in this revision. See [current validation](DATABRICKS_VALIDATION.md). Earlier counts and deployment statements below are historical.

> Historical record. Current local code has 508 tests, 30 tools, four prompts and four resources; see [current implementation](CURRENT_IMPLEMENTATION.md). Historical names and counts remain below.

> Historical notes retained for traceability. The current local revision is documented in CURRENT_IMPLEMENTATION.md, the evaluation DOCX and ../evaluation/results.json. No deployment was performed.

# Parent-facing evidence and navigation

Implemented November 19, 2026. Eight additive tools (27 total); existing tool names
and signatures remain unchanged. `search_trials` adds participation fields.

| Tool | What it returns | Important limit |
|---|---|---|
| route_parent_question | Local fixed referral, urgent-help, identity, privacy or research route | English heuristic rules, not validated triage; can miss or overflag requests |
| get_parent_medication_info | RxNorm-confirmed ingredient, selected DailyMed label effects, LactMed evidence, MedlinePlus links | No diagnosis; confirm exact formulation; combinations require separate research |
| search_medication_recalls | FDA enforcement candidates, firms, product text, lots, dates, classifications and source URLs | No bottle clearance; lot ranges and all-lot notices need human interpretation; enforcement records lack consumer instructions |
| search_drug_safety_alerts | Dated FDA communication titles and links | Current index/title matching only, not full notices or all archives |
| find_recruiting_studies | Recruiting records with public eligibility, contacts, site status and update date | Potential matches only; first 20 screened, literal topic matching may miss synonyms; no distance/eligibility/enrollment decision |
| search_pregnancy_registries | FDA-listed registries, source statuses and public contacts | FDA does not operate/endorse them; verify current enrollment |
| search_parent_input_opportunities | NIH/FDA Federal Register candidate notices, deadlines if supplied, official PDFs and engagement directories | Closed meetings excluded; candidates still require checking; no complete RFI coverage or automatic submission |
| get_reporting_resources | MedWatch, Poison Help and NIH/FDA engagement links | Navigation only; no reporting/submission performed |

## Enforcement and privacy

`mc/audit.py` adds a structured safety envelope to every tool response and blocks
obvious identifying inputs before external retrieval. It never adds query text to
the audit log. Detection is heuristic, not comprehensive de-identification.

The companion `test-mcp-chat.ps1` calls the router before the model; recognized
urgent/referral/identity/privacy requests use fixed messages without model generation.
Missing router decisions fail closed. Tool identity/error blocks stop synthesis.
Narrow output checks reject direct personal treatment instructions and definite
eligibility/bottle-clearance claims. Prompt-based source review remains necessary;
neither regex nor prompting proves safety against arbitrary wording or injection.

The companion script no longer writes ordinary chat transcript files. `-SaveTrace` explicitly enables capture
for synthetic evaluation only; privacy-blocked requests are never captured. Existing
evaluation scripts need this switch to save fresh answers. Old captures are retained.
Questions still transit Databricks and relevant public services; platform retention
and shell command history are outside these application controls. Do not submit identifiable health histories.

Use `-Country US` for the verified US emergency/Poison Help routing. Other country
values return local-service guidance without guessed telephone numbers. Guidance
sources: https://poisonhelp.hrsa.gov/what-you-can-do and
https://www.poison.org/need-immediate-assistance . No clinician has certified this policy.

## Evidence boundaries

No personalized doses, schedules, missed-dose instructions, tapers or medication
start/stop/change decisions. Label effects in the medicine taker are not automatically
infant effects. Milk concentrations are not clinical outcomes. Monitoring recommendations
are not observed adverse events. Empty/missing results never establish safety.

Raw source excerpts may contain historical doses or treatment directions; clients must
not turn them into personal instructions. Third-party clients receive the tools and
metadata but do not automatically inherit companion-client enforcement.

## Reproduction

Expanded November 19 evaluation and architecture: see `METHODOLOGY.md` and companion
`evaluation/parent-expanded/report.html`. Initial failures and separate follow-ups
are retained. New wording coverage and fail-closed trace capture are documented there.

Server: `.venv\Scripts\python.exe -m pytest tests -q`.
Companion: `pwsh -NoProfile -File evaluation/test-parent-chat-policy.ps1` and
`pwsh -NoProfile -File evaluation/test-citation-output.ps1`.
Live source probes and deployment checks: companion `evaluation/parent-features/`.
This feature validation is separate from the earlier 32-question MLflow benchmark;
do not claim those historical scores validate these new tools or guardrails.


## 2026-11-19 pediatric population and public-input deadline correction
Pediatric discovery now requires explicit numeric registry age support below 18, retaining conflict checks and excluding adult-only and unverified records. CHILD category alone is insufficient for the main list. This conservative screen may omit eligible studies and does not establish individual eligibility. Applied to both trial tools, without signature changes. Returned age fields, exclusion counts, study type, relevance and bounded-search limitations remain available.
Public-input results separate the listed comment date and past/today/future/unknown relation from unverified submission acceptance. Meeting dates never establish comment closure; same-day dates do not establish a cutoff time.
Client instructions require population filtering and separate date/relevance/submission status. 215 local tests passed; 21 deployed checks passed. Final deployment: 01f1e4656e0c107e949cdadb1f6d24a8. Original generalization results and the first follow-up (which still admitted CHILD-only broad records) remain retained. See companion evaluation/population-deadline-final for captured answers, MLflow results and limitations. These are engineering evaluations, not clinical certification.
