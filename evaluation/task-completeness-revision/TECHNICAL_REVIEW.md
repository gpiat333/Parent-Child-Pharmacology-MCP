# Technical review of diagnostic grades

Raw model scores are retained without overrides. This review checks the interpretation of the scores and selected answer text; it is not independent clinical adjudication.

## Meaning and scope

Fidelity checks source claims against the bounded captured evidence pool. Task fulfillment checks the specified lookup or output requirements. They are independent. A source-supported answer can omit a requirement; an honest inability to retrieve current information can leave a task incomplete. Not-assessable fidelity is excluded from fidelity rates. A URL match does not establish claim support.

The same known questions and grader v2 prompt were used. Each arm retains one completed response. Only MCP has retrieval, enforced workflows and fixed notices. The paired runner uses a shorter prompt than the chat companion. These conditions do not establish isolated model ability, clinical accuracy or general superiority.

## Current negative grades

### R09 — chat

Raw fidelity: **fail**. Raw task fulfilled: **True**.

Grader rationale (unadjudicated):

> The answer correctly reports the returned notice title, date, link, lack of retrieved full notice text or excerpts, unknown source population and age applicability, and the search coverage limits. However, the clause "Only the notice title and link were returned" is contradicted by the evidence, which also returned the listed date and population-context metadata. The citations otherwise accurately support the associated claims, and the response provides no personal treatment recommendations.

Technical observation: The answer displays the returned notice date, then says only the title and link were returned. The grader treats that literal metadata wording as a contradiction and retains task fulfillment. The disclosure that full notice text and excerpts were not retrieved matches the capture. This is a wording inconsistency about returned metadata, not a demonstrated false pharmacology claim. The raw fidelity failure is retained; no clinical override is applied.

[Captured answer and tool evidence](chats/R09-results.json) · [Raw grade](chat-judgments/R09.json)

### E01-gap — chat

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer preserves all three evidence axes, distinguishes human, animal, registry, and spontaneous-report evidence, states the bounded maternal-PK gap, and separates FDA registry information without ranking or recommending participation. However, it fails the explicit instruction not to provide doses: the animal-evidence section reports dose-related information, including "doses up to 8 and 10 times the maximum recommended human dose (MRHD) of 50 mg" and related dose values. It also includes the uncited source claim, "The MCP lookup notes that stopping or changing a medicine can also carry risks," which is not represented in the supplied reference pool.

Technical observation: The cited dose quotation and 50 mg value appear in the reference material, not in the saved answer. The answer contains no numeric dose regimen in its visible text. The continuity-of-care caution also appears explicitly at reference_evidence[0].result.continuity_of_care_notice and is attributed to the MCP in the answer. The retained grader-attribution-audit.json checks the exact quotation, reference field and file hashes. This supports an evaluator attribution error, not a demonstrated dosing violation in the answer. The raw task failure is preserved; no clinical adjudication or score override is applied.

[Captured answer and tool evidence](chats/E01-gap-results.json) · [Raw grade](chat-judgments/E01-gap.json)

### R01 — mcp

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer accurately separates observed symptoms from study-assessment items and does not turn those items into a universal monitoring recommendation. It correctly reports diarrhea, rash, somnolence, urticaria, the no-adverse-effects study, limited evaluation, uncertain causality, and the absence of relevant published infant blood-level information. However, the criteria specifically require summarizing milk measurements, and the answer only says that milk exposure was low without reporting the retrieved measured milk concentrations or clearly stating that those measurements were omitted. Therefore the response is source-faithful but does not fully satisfy the task.

Technical observation: The revised answer correctly separates study-assessment items from recommendations, but still summarizes milk exposure qualitatively. The retrieved numeric concentrations are absent from the final answer. This residual omission prompted the next .7 source revision, which exposes exact concentration expressions and their context in a dedicated field. This .6 score is retained.

[Captured answer and tool evidence](paired-final/R01-mcp.json) · [Raw grade](paired-final/R01-mcp-judge.json)

### E01-gap — mcp

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer presents all three requested axes with empty rows, separates animal from human evidence, states the retrieved maternal PK result, and keeps registry information separate and non-recommendatory. Its substantive source claims are supported within the bounded retrieval scope, with no contradicted claims. However, it fails the explicit instruction not to provide doses: it includes animal dose levels and the MRHD in the fetal/infant outcomes section, for example, "in pregnant rabbits... highest tested exposure group" is accompanied by label-derived dose information and the cited animal findings include dose values such as 300 mg/kg/day, 120 mg/kg/day, and 50 mg. The exact two PubMed URLs cited are not present in the reference pool, so those citations are unverified even though equivalent supplied search evidence supports the retrieval conclusions.

Technical observation: The cited dose values (300 mg/kg/day, 120 mg/kg/day and 50 mg) are absent from the saved final answer and occur in the supplied reference material. The raw task failure therefore again confuses reference text with the answer. The rationale separately flags two PubMed URLs absent from the bounded pool; that citation observation is retained. No grade is overridden.

[Captured answer and tool evidence](paired-final/E01-gap-mcp.json) · [Raw grade](paired-final/E01-gap-mcp-judge.json)

### R01 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer appropriately separates purported observations from purported monitoring advice, avoids giving a dose, and conveys that low milk transfer and absence of reported effects do not prove safety. But it omits the retrieved milk measurements and infant-level finding (no relevant published infant levels), which the criteria required to distinguish measurements from observations. It also misstates the 25-participant study and converts reported symptoms into a LactMed monitoring recommendation. The claimed single older rash report is incomplete and does not accurately represent the record, which includes two rashes among 40 exposed infants, another study reporting rash and somnolence, and a case of urticaria after exposure to amoxicillin-clavulanate plus gentamicin where causation by a specific drug was uncertain. The uncertainty discussion is broadly reasonable but the claim that the evidence consists of small observational experience rather than large controlled studies is not directly cited.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R01-plain.json) · [Raw grade](paired-final/R01-plain-judge.json)

### R03 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer appropriately separates adult treatment warnings from infant exposure and observed outcomes, avoids doses, and accurately conveys most LactMed findings and limitations. However, the clause "The U.S. label states that metformin is present in human milk and that published reports have not identified an association with metformin exposure through milk and adverse effects in breastfed infants" conflicts with the supplied retrieved label. That label instead says animal milk excretion was observed, human nursing studies had not been conducted, and there was potential for infant hypoglycemia. The answer also lists "vitamin B12 deficiency" and broad contraindications/precautions as label warnings, but those claims are not verifiable from the supplied label extract. It fails to identify the retrieved product as "METFORMIN HCL TABLET [QPHARMA, INC.]" and does not disclose the extracted label's missing warnings-and-precautions and boxed-warning sections or the product-selection limitation. Therefore the source comparison is materially incomplete and contains a source attribution error.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R03-plain.json) · [Raw grade](paired-final/R03-plain-judge.json)

### R04 — plain

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer correctly states that a nonmatch for NOTREAL-77 would not clear the bottle and appropriately preserves the need to verify formulation, manufacturer, lot, expiration, and label details. Its warnings about bounded searches, indexing/reporting limits, and the insufficiency of a no-match are supported by the reference evidence. However, it says it cannot verify the live FDA records and therefore does not report the retrieved search result: the supplied evidence shows a naproxen product-name search returned candidate records and no returned lot matched NOTREAL-77, while expressly stating that this is not bottle-level clearance. The answer also makes several additional claims about state, wholesaler, pharmacy, manufacturer, and counterfeit-related sources that are not directly supported by the reference pool. Because the requested lookup was not actually reported, task fulfillment is false, although the abstention is honest.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R04-plain.json) · [Raw grade](paired-final/R04-plain-judge.json)

### R06 — plain

Raw fidelity: **not_assessable**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer honestly abstains from reporting study information and makes no substantive claims about the ClinicalTrials.gov records. However, it does not fulfill the requested lookup: it provides no studies, exact links, statuses, update dates, contacts, or qualification limits, despite the reference evidence containing two recruiting pediatric U.S. studies with those details.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R06-plain.json) · [Raw grade](paired-final/R06-plain-judge.json)

### R09 — plain

Raw fidelity: **not_assessable**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer honestly disclosed that it could not verify the search and that full notice text was not retrieved, but it did not report the returned notice title or link to the returned FDA notice. The evidence shows one returned result: “FDA requires Boxed Warning about serious mental health side effects for asthma and allergy drug montelukast (Singulair); advises restricting use for allergic rhinitis,” with a supplied FDA notice URL. The answer therefore did not fulfill the requested lookup, although its inability claim is an honest abstention rather than a false claim about the FDA evidence.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R09-plain.json) · [Raw grade](paired-final/R09-plain-judge.json)

### E01-gap — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The response presents all three requested axes, keeps rows visible, states that no pregnancy-specific maternal PK data were retrieved, separates registry contacts, avoids medication decisions, and does not give a patient-specific dose. However, it materially conflicts with the supplied evidence. The clause "available postmarketing reports are insufficient" is not supported by the reference label, which says there are no available data on use in pregnant women. The animal claim that pregnancy/lactation exposure was associated with "decreased pup body weight and delayed pup development" and that the label describes embryo-fetal findings at maternally toxic exposures is contradicted by the supplied label, which reports no maternal, fetal, or developmental toxicity in the described animal studies. The registry section gives MotherToBaby contacts, whereas the supplied label and FDA-directory evidence identify Idorsia/QUVIVIQ Pregnancy Registry contacts and www.QuviviqPregnancyStudy.com. It also fails the criterion to cite the FDA directory. The statement about nonpregnant adult PK and CYP3A4 is not verifiable from the provided reference extract. Because unsupported and contradicted source claims affect the central evidence brief and registry information, the task is not fully fulfilled.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/E01-gap-plain.json) · [Raw grade](paired-final/E01-gap-plain-judge.json)

### E02-maternal-pk — plain

Raw fidelity: **fail**. Raw task fulfilled: **True**.

Grader rationale (unadjudicated):

> The answer fulfills the requested structure: it separates maternal effects, fetal exposure, and fetal outcomes; avoids numeric dose values and individualized medication advice; states important confounding and evidence gaps; and includes clinician questions. The supplied DailyMed label supports several central claims, including pregnancy-associated concentration decreases and postpartum restoration, epilepsy-related risks, and registry outcome summaries. However, the maternal PK section overstates what was retrieved. The clauses "increased lamotrigine clearance during pregnancy," "beginning early in pregnancy," "often becoming more pronounced later," "pregnancy-related induction of glucuronidation, particularly through UGT pathways," "postpartum transition may occur faster," and the detailed interindividual and co-medication claims are not supported by the supplied abstracts or label passages. The answer also states that lamotrigine crosses the placenta and that cord concentrations are similar to maternal concentrations, but the reference pool contains no placental or cord-sample evidence. The claim about serious rash and hypersensitivity is not verifiable because the supplied label extraction lacks the relevant adult warnings/adverse-reaction sections. The cited Pennell, Tran, AAN/AES, FDA, UKTIS, MotherToBaby, EUROCAT, and International Registry URLs are mostly absent from the reference pool, so their associated claims remain unverified. The answer also does not preserve the actual study population and design for the key PK literature it cites, contrary to the stated criterion.

Technical observation: The raw task grade is True even though its rationale says the answer does not preserve study population and design as required. Fidelity is Fail. This disagreement within the rationale is retained, and the plain arm receives its raw task credit. It is not evidence of source-supported pharmacokinetic accuracy.

[Captured answer and tool evidence](paired-final/E02-maternal-pk-plain.json) · [Raw grade](paired-final/E02-maternal-pk-plain-judge.json)

## Technical observations on passing grades

### R01 — chat

The new answer explicitly separates study monitoring from a source recommendation and says that no separate monitoring recommendation was retrieved. It summarizes milk levels qualitatively, without numeric milk concentrations. The preceding paired grade demanded quantitative milk findings, while this grade accepts the separation. The criterion does not explicitly demand numeric concentrations; this illustrates variation in grader strictness, rather than independent validation of completeness.

[Captured answer](chats/R01-results.json) · [Raw grade](chat-judgments/R01.json)

### D05-brief — chat

The new maternal row contains milk-supply and lactogenesis observations, made available by balanced section allocation. The raw passing rationale refers to historical dose values, but the saved final answer gives study sizes and serum-level ratios rather than an administered dose regimen. This wording is another grader interpretation issue, even though the final grade is a pass. No raw score is changed. The source-axis grouping and answer remain unadjudicated clinically.

[Captured answer](chats/D05-brief-results.json) · [Raw grade](chat-judgments/D05-brief.json)

## Historical figures in the question

The preceding .5 run had 21/21 fidelity passes and 18/21 fulfilled research tasks, with paired tasks MCP 5/7 and plain 0/7. The earlier .4 run had 19/21 fidelity and 19/21 tasks, with paired tasks MCP 7/7 and plain 0/7. These are separate historical runs. The two paired task failures were an omitted quantitative milk summary with inferred monitoring advice, and an incomplete adult label comparison. The three research failures were an omitted FAERS subset caveat, an absent numeric empty-year count and a disputed dose allegation plus an axis-placement concern. Fresh answers, live sources and model judgments can vary. Zero plain tasks fulfilled was not a finding that every answer was false. Current totals are in summary.json and REPORT.md.

## Completeness changes

The current source retains all available LactMed sections within a shared character budget, returns adult and population label sections from the same selected SPL, explicitly shows zero retrieved records for a requested empty fiscal year while keeping capped portfolio totals unknown, appends the FAERS scope notice, and narrows maternal-axis assignment. Seventeen additional test cases pass. The cases, paired system prompt and grader remain unchanged; the companion source-review instructions were strengthened. These are development-case repairs, not independent validation.

## Routing regression

The original “Give me a pregnancy evidence brief for lamotrigine” question completed with medication_evidence_brief as its first evidence call. Twelve direct deployed preflight checks cover positive variants, negation, incidental mention and overriding stops. They are separate from the 28-case benchmark and 42 final MLflow rows. The matcher remains a narrow English heuristic, not exhaustive language understanding.

No clinician adjudication occurred. Raw negative scores and all completed answers remain unchanged.
