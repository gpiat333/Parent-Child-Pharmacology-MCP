# Technical review of diagnostic grades

Raw model scores are retained without overrides. This review checks the interpretation of the scores and selected answer text; it is not independent clinical adjudication.

## Meaning and scope

Fidelity checks source claims against the bounded captured evidence pool. Task fulfillment checks the specified lookup or output requirements. They are independent. A source-supported answer can omit a requirement; an honest inability to retrieve current information can leave a task incomplete. Not-assessable fidelity is excluded from fidelity rates. A URL match does not establish claim support.

The same known questions and grader v2 prompt were used. Each arm retains one completed response. Only MCP has retrieval, enforced workflows and fixed notices. The paired runner uses a shorter prompt than the chat companion. These conditions do not establish isolated model ability, clinical accuracy or general superiority.

## Current negative grades

### R12 — chat

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer accurately reports the queried age scope, retrieved reaction counts, and the limits of spontaneous-report data. However, the criteria explicitly require stating that a subset of reports cannot be generalized to all infants. The answer implies limited applicability through its discussion of unconfirmed infant-specific findings and the queried cohort, but it does not directly state the required non-generalizability conclusion.

Technical observation: The answer describes the queried cohort, absent denominators and uncertain age metadata, but does not explicitly say that the subset cannot be generalized to all infants. This supports the narrow omitted-wording rationale; it is separate from fidelity.

[Captured answer and tool evidence](chats/R12-results.json) · [Raw grade](chat-judgments/R12.json)

### D05-brief — chat

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer is substantively faithful to the supplied evidence and presents the requested three evidence axes, source links, limitations, and clinician questions without making a personal treatment decision. However, it does not fully satisfy the explicit instruction not to provide doses: it reproduces numerous dose values in the evidence summaries, including the clause “In a study of 12 lactating women...” followed by dose-related source details and multiple dose values throughout the LactMed-linked claims. These are historical source data rather than individualized dosing advice, but they still violate the requested no-doses constraint. The maternal-effects section also largely reports milk/infant exposure rather than effects on the lactating person, though the three-axis structure is present.

Technical observation: The saved answer contains study sizes and dates, but no numeric medication doses and no dose/doses/dosing wording. The supplied reference pool does contain dose values. The dose allegation therefore appears to confuse source content with final-answer text. The grader also raises a separate maternal-axis placement concern that remains unadjudicated. The raw task failure is retained; no clinical judgment is overridden.

[Captured answer and tool evidence](chats/D05-brief-results.json) · [Raw grade](chat-judgments/D05-brief.json)

### P01-portfolio — chat

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer faithfully reports the supplied evidence: the FY2025 group, 20 retrieved records, 19 distinct core projects, separate award and direct-cost totals, the exact query filters, the 20-of-96 capped result, and the activity-code limitation are all supported. However, the criteria require grouped counts, and FY2024 does not provide an explicit numeric count; it only says that no group was returned. The homepage citation is also insufficient by itself to support the associated totals and cap claims, although those claims are supported by the supplied structured evidence.

Technical observation: The answer gives 20 FY2025 records and says no FY2024 group was returned, explicitly noting that this is not proof of no projects. The grader demands an explicit numeric FY2024 count. This is rubric-sensitive: zero in the capped extract must not be read as zero in the full portfolio. The raw fail is preserved for human adjudication.

[Captured answer and tool evidence](chats/P01-portfolio-results.json) · [Raw grade](chat-judgments/P01-portfolio.json)

### R01 — mcp

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> Most of the observed-symptom and uncertainty summary is faithful to the retrieved LactMed record, and no dose was given. However, the answer presents diarrhea/stool changes, rash/diaper rash, thrush, feeding difficulty, and unusual sleepiness as LactMed 'monitoring targets.' The record reports some of these as observed effects or as findings monitored in a study, but it does not provide the stated general monitoring advice, so those five advice claims are unverified. The answer also omits the requested milk measurements (including the reported maternal milk concentrations and modeled relative infant dose), despite mentioning only that milk levels were low. It therefore does not fully satisfy the criterion to separate and summarize milk measurements, observations, and recommendations.

Technical observation: The grader flags two different concerns: monitoring advice attributed to LactMed without support in the supplied record, and omitted quantitative milk-exposure findings. These are retained as source-attribution and task-completeness findings; no independent clinical adjudication was performed.

[Captured answer and tool evidence](paired-final/R01-mcp.json) · [Raw grade](paired-final/R01-mcp-judge.json)

### R03 — mcp

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer generally separates adult label information from breastfed-infant observations, identifies the retrieved QPharma product and LactMed, distinguishes theoretical warning from observed infant outcomes, discloses several limitations, and avoids giving medication doses. However, it makes a material false retrieval claim: "The retrieved label’s adult adverse-reaction section was not returned as a separate section." The supplied evidence explicitly includes that section, so the answer omits relevant adult label findings and incorrectly presents the adult comparison as incomplete. This is not an honest abstention because the evidence shows the section was retrieved.

Technical observation: The answer’s actual get_label_sections call returned only pregnancy, lactation and pediatric_use. The adult adverse_reactions section appears in the evaluator’s separate get_parent_medication_info reference capture, not in the answer’s tool result. Thus the claim that its own retrieval omitted the adult section is supported by that trace; the fidelity rationale conflates the two captures. The requested adult comparison still remains incomplete, so the raw task failure is retained. Neither grade was overridden.

[Captured answer and tool evidence](paired-final/R03-mcp.json) · [Raw grade](paired-final/R03-mcp-judge.json)

### E02-maternal-pk — mcp

Raw fidelity: **fail**. Raw task fulfilled: **True**.

Grader rationale (unadjudicated):

> The answer fulfills the requested three-axis brief, distinguishes Clinical Considerations from individualized clinician decisions, preserves study context and gaps, avoids dose values and personal medication advice, and includes clinician questions. However, the clause "The retrieved sources support that fetal exposure occurs after maternal use" is not established by the supplied evidence: the cited trial is recruiting and is evaluating fetal exposure, with no fetal-concentration results provided, while the literature evidence concerns breast milk rather than measured fetal exposure. The answer appropriately states that quantitative human fetal-concentration estimates were not retrieved, but the stronger assertion that fetal exposure is supported should have been framed as expected or under investigation rather than as a demonstrated retrieved finding. The search-record counts and bounded-search description also lack direct inline citations.

Technical observation: The grader distinguishes an assertion that fetal exposure was demonstrated in retrieved sources from the narrower finding that a recruiting study is investigating exposure without posted concentration results. The answer acknowledges missing quantitative fetal data, but its stronger opening claim and missing inline citations remain a fidelity concern in the supplied pool. The raw fidelity fail and task pass are retained; no independent clinical adjudication was performed.

[Captured answer and tool evidence](paired-final/E02-maternal-pk-mcp.json) · [Raw grade](paired-final/E02-maternal-pk-mcp-judge.json)

### R01 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer appropriately separates observed symptoms from a monitoring section, avoids dosing, and accurately conveys several LactMed findings. The source supports reports of infant diarrhea, rash, thrush, and studies in which no adverse effects were reported, as well as low milk levels and uncertainty about causation. However, the exact clause 'monitoring is not routinely required beyond observing the infant for possible gastrointestinal effects or rash' is not present in the retrieved LactMed record and is therefore an unsupported recommendation. The statements that diarrhea and rash are common in infants and that LactMed does not establish safety for every medication combination are also not stated in the supplied evidence. Most importantly, the answer omits the requested milk measurements: reported maternal milk concentrations and the record's statement that published infant-level information was not found. It therefore does not fully satisfy the criterion to summarize milk measurements and disclose the available record context.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R01-plain.json) · [Raw grade](paired-final/R01-plain-judge.json)

### R03 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer appropriately separates adult label warnings from infant exposure and outcome findings, avoids dosing, and accurately reports most LactMed findings and limitations. However, the clause "The U.S. prescribing information has a boxed warning for lactic acidosis" is not established by the supplied retrieved evidence: the selected label extract lists "boxed_warning" among missing sections and warns that missing sections do not prove absence or presence. More importantly, the retrieved DailyMed label explicitly contains a lactation section warning that hypoglycemia in nursing infants may exist; the answer omits this infant-specific label warning and states broadly that the label does not provide an infant-specific warning equivalent to the adult boxed warning. That omission prevents a complete source comparison. The answer also fails to name the retrieved product precisely as "METFORMIN HCL TABLET [QPHARMA, INC.]" and does not disclose the label-extraction limitation that the warnings section was truncated and that the product/formulation was not confirmed. The B12 assertion is also not supported by the supplied extracted label evidence.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R03-plain.json) · [Raw grade](paired-final/R03-plain-judge.json)

### R04 — plain

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer correctly states that a nonmatching lot does not establish that a bottle was unaffected, preserves the distinction among product identity, manufacturer, formulation, lot, and recall status, and explains that verification should compare the bottle with the official notice and confirm details independently. These points are consistent with the evidence that the search returns candidate product-name matches only, that no match is not clearance, that formulation/manufacturer/lot/expiration must be checked, and that records may lag announcements. The answer did not actually report the retrieved naproxen candidates or their statuses, and its statement that it could not query the live database means the requested lookup was not fulfilled. Several additional explanations—such as manufacturer, pharmacy, wholesaler, or state actions and counterfeit products—are plausible but not verifiable in the supplied reference pool.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R04-plain.json) · [Raw grade](paired-final/R04-plain-judge.json)

### R06 — plain

Raw fidelity: **not_assessable**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer honestly abstains, stating: “I’m unable to verify live ClinicalTrials.gov records in this environment.” This is an access statement rather than a claim about what the records contain, so it is not assessable as supported or contradicted from the reference evidence. However, the requested lookup was not performed: no studies, direct links, recruitment statuses, update dates, contacts, or qualification limits were provided.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R06-plain.json) · [Raw grade](paired-final/R06-plain-judge.json)

### R09 — plain

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer honestly states that it could not access or retrieve the notice text and avoids inventing titles, excerpts, mechanisms, or treatment instructions. Its statement that the full notice text was not retrieved is consistent with the evidence, which contains only title/index results. However, it fails the requested lookup because it does not report the returned notice title or link to the returned notice; instead, it provides an unverified topic-page URL. The access limitation is an honest abstention rather than a claim that no FDA safety notice exists.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R09-plain.json) · [Raw grade](paired-final/R09-plain-judge.json)

### E01-gap — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer presents all requested evidence axes, keeps empty rows visible, states that no pregnancy-specific maternal pharmacokinetic data were retrieved, separates registry information, avoids medication decisions, and provides no dosing instructions. However, it fails source fidelity and task fulfillment in important respects. The animal row says that “developmental findings were reported at maternal exposures above or near clinical exposure,” whereas the supplied label evidence reports no fetal toxicity, malformation, or maternal/developmental toxicity at the tested rat and rabbit exposures; it reports maternal toxicity in rabbits only at the highest tested exposure. The answer also supplies registry/contact information that conflicts with the retrieved FDA directory and label: the evidence gives the QUVIVIQ registry phone as 1-833-400-9611, while the answer gives 1-833-995-2735 and additionally asserts FDA-label direction to the National Pregnancy Registry for Psychiatric Medications, which is not supported by the supplied label evidence. Several claims about absence of measured fetal or infant concentrations, placental transfer, cord blood studies, lactation data, CYP3A4 metabolism, and MedWatch are not directly supported by the reference pool or are missing citations. The cited 2022 FDA PDF is also absent from the reference pool, so its support is unverified.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/E01-gap-plain.json) · [Raw grade](paired-final/E01-gap-plain-judge.json)

### E02-maternal-pk — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer has the requested three-axis structure, visible gaps, clinician questions, and avoids numeric medication doses and individualized dosing advice. It also honestly states that a live retrieval from Clinical Considerations could not be verified. However, task fulfillment fails because the requested maternal pharmacokinetic evidence is presented as if established from specific literature while the key cited Pennell and Clark sources are absent from the reference pool, and the answer does not preserve their study populations or designs. Several additional substantive claims—placental transfer, cord-blood similarity, EURAP and EUROCAT findings, and neurodevelopmental conclusions—are supported only by URLs not present in the evidence pool. The supplied evidence does support general claims about pregnancy-related concentration changes, postpartum restoration, seizure-control context, limited observational evidence, guideline framing, and the registry, but not the answer's full source-specific brief.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/E02-maternal-pk-plain.json) · [Raw grade](paired-final/E02-maternal-pk-plain-judge.json)

## Historical figures in the question

The preceding Databricks run had 19/21 fidelity passes and 19/21 fulfilled research tasks. Those were separate counts and did not identify the same two failures. Its paired task result of MCP 7/7 versus plain 0/7 concerned seven source-lookup tasks without retrieval tools in the plain arm. Zero tasks fulfilled was not a finding that every answer was false. The current totals are in summary.json and REPORT.md; older records are preserved.

## Routing regression

The original “Give me a pregnancy evidence brief for lamotrigine” question completed with medication_evidence_brief as its first evidence call. Twelve direct deployed preflight checks cover positive variants, negation, incidental mention and overriding stops. They are separate from the 28-case benchmark and 42 final MLflow rows. The matcher remains a narrow English heuristic, not exhaustive language understanding.

No clinician adjudication occurred. Raw negative scores and all completed answers remain unchanged.
