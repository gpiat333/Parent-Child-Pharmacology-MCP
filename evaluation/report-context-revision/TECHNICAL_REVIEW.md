# Technical review of diagnostic grades

Raw model scores are retained without overrides. This review checks the interpretation of the scores and selected answer text; it is not independent clinical adjudication.

## Meaning and scope

Fidelity checks source claims against the bounded captured evidence pool. Task fulfillment checks the specified lookup or output requirements. They are independent. A source-supported answer can omit a requirement; an honest inability to retrieve current information can leave a task incomplete. Not-assessable fidelity is excluded from fidelity rates. A URL match does not establish claim support.

The same known questions and grader v2 prompt were used. Each arm retains one completed response. Only MCP has retrieval, enforced workflows and fixed notices. The paired runner uses a shorter prompt than the chat companion. These conditions do not establish isolated model ability, clinical accuracy or general superiority.

## Current negative grades

### E01-gap — chat

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer substantially matches the supplied evidence: it keeps all three evidence axes visible, separates animal findings from human findings, reports the retrieved maternal PK gap within scope, preserves empty rows and absent abstracts, and presents FDA registry information separately without recommending participation. However, it fails the explicit instruction not to provide doses. The clauses "at doses up to 8 and 10 times the maximum recommended human dose (MRHD) of 50 mg" and the animal-context discussion reproduce dose-related source content, and the related registry eligibility text also includes exposure timing based on half-lives. This makes task_fulfilled false despite the source claims being generally supported. The statement that LactMed was not applicable is supported by the reference evidence but lacks a direct citation in the answer.

Technical observation: The final chat displays separate FAERS report terms and counts with uncertainty and keeps the clinical-outcome row empty. The grader attributes an 8-and-10-times statement, 50 mg and half-life eligibility timing to the answer; none is present in the final answer, while all occur in the supplied reference. The exact-text audit documents the misattribution. The uncited LactMed applicability sentence remains a presentation limitation; no score override or clinical pass is assigned.

[Captured answer and tool evidence](chats/E01-gap-results.json) · [Raw grade](chat-judgments/E01-gap.json)

### E01-gap — mcp

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer preserves all three requested evidence axes, distinguishes animal from human evidence, keeps empty rows visible, states the retrieved maternal PK gap within scope, separates spontaneous reports from observed outcomes, and presents FDA registry information without recommending participation. However, it violates the explicit no-doses requirement by including animal dose levels and the MRHD in clauses such as "at the highest tested exposure," "up to 8 and 10 times the maximum recommended human dose (MRHD) of 50 mg," and the animal findings listing mg/kg/day values. The claim that no measured fetal or infant exposure was retrieved is supported by the supplied evidence but is not directly cited in that table row.

Technical observation: The answer now displays FAERS report terms and counts separately from the empty clinical-outcome row, retaining population uncertainty and noncausation/denominator caveats. The grader quotes an 8-and-10-times exposure statement, 50 mg and mg/kg/day values as answer text; those numeric regimens are absent from the answer and present in the reference. The exact-text audit documents that misattribution without changing the task failure. The empty exposure row does lack a direct citation, a separate presentation limitation. No clinician adjudication or adjusted pass rate is claimed.

[Captured answer and tool evidence](paired-final/E01-gap-mcp.json) · [Raw grade](paired-final/E01-gap-mcp-judge.json)

### R01 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer correctly separates symptoms from general uncertainty and does not provide a dose. However, it materially understates and incompletely reports the retrieved observations: the record reports diarrhea in 3 of 25 infants, diarrhea in 2 of 40 and rash in 1 of 40, rash and somnolence in another comparison study, and a generalized urticaria case after exposure to amoxicillin/clavulanate plus gentamicin. The clause "one breastfed infant developed a rash" is therefore misleading as a summary of the record, and "some infants ... had loose stools or diarrhea" omits the reported study counts and other findings. More importantly, the answer states that "LactMed recommends observing" for diarrhea, rash, thrush, and allergic reactions, but the retrieved record does not contain an explicit monitoring recommendation; it describes symptoms reported or parameters monitored in studies. The answer also omits the required milk measurements and the explicit statement that published infant-level measurements were not found: the record reports milk concentrations of 0.69 mg/L (range 0.46–0.88) at 4 hours and 0.81 mg/L (range 0.39–1.3) at 5 hours. Thus it does not satisfy the criterion to summarize observations separately from advice and milk measurements.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R01-plain.json) · [Raw grade](paired-final/R01-plain-judge.json)

### R03 — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer correctly separates adult label risks from infant observations, avoids dosing, identifies LactMed's general role, and appropriately states that absence of reported adverse effects is not proof of safety. However, it does not fulfill the requested comparison completely. The answer says, "I cannot verify the exact numeric values" and later, "I cannot verify such measurements"; these are honest abstentions, but the retrieved LactMed evidence actually contains milk concentrations and infant-serum results, so the requested measured findings were omitted. The statement that infant blood-level information was "limited or unavailable in the retrieved record" is misleading because the record includes serum measurements in four infants and additional measurements in two infants. The claim that the label "states that metformin is present in human milk and that published reports have not identified adverse effects in breastfed infants" is not supported by the supplied label excerpt, which instead states that animal milk data exist, human nursing studies had not been conducted, and potential infant hypoglycemia was a concern. The answer also fails to name the retrieved product specifically (METFORMIN HCL TABLET, QPHARMA, INC.) and does not disclose the exact extracted missing label sections, namely warnings_and_precautions and boxed_warning; its general discussion of missing quantitative exposure and registry evidence is not a substitute for those source-extraction limitations.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R03-plain.json) · [Raw grade](paired-final/R03-plain-judge.json)

### R04 — plain

Raw fidelity: **pass**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer correctly explains that a nonmatch for NOTREAL-77 would not establish that the bottle was unaffected, preserves the distinction among product identity, manufacturer, formulation, lot, and recall status, and describes further verification. Its cautions about bounded database coverage, differing identifiers, delayed or incomplete records, and manufacturer/pharmacy confirmation are generally consistent with the supplied limitations. However, the answer says it cannot access the live database and therefore does not report the returned candidate naproxen recall records or their statuses, even though the reference evidence contains them; thus the requested lookup was not fulfilled. The counterfeit/relabeled-bottle possibility and the specific MedWatch recommendation are not substantiated by the supplied reference pool. The statement about inability to access the source is an abstention rather than a contradicted claim.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R04-plain.json) · [Raw grade](paired-final/R04-plain-judge.json)

### R06 — plain

Raw fidelity: **not_assessable**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer honestly abstains from providing study records because it says it cannot verify live ClinicalTrials.gov data. It does not make substantive claims about the studies that can be assessed against the reference evidence. However, it does not fulfill the requested lookup: it provides neither the two exact study links nor statuses, update dates, contacts, or qualification limits.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R06-plain.json) · [Raw grade](paired-final/R06-plain-judge.json)

### R09 — plain

Raw fidelity: **not_assessable**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The answer makes no substantive claims about the FDA notices and honestly abstains from reporting them. However, it does not fulfill the lookup request: the reference evidence contains a returned FDA notice title and URL, while the answer says, "Therefore, I cannot reliably provide the requested FDA links or summarize returned notices." It also correctly states that full notice text was not retrieved and that this is not evidence that no FDA communications exist.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/R09-plain.json) · [Raw grade](paired-final/R09-plain-judge.json)

### E01-gap — plain

Raw fidelity: **fail**. Raw task fulfilled: **False**.

Grader rationale (unadjudicated):

> The response appropriately keeps the three evidence axes visible, states that no pregnancy-specific maternal pharmacokinetic data were retrieved, avoids dosing and medication decisions, and separates registry information from treatment recommendations. Its abstention about live source verification is honest. However, it does not provide the FDA-listed Quviviq registry contact from the reference evidence: it instead identifies the National Pregnancy Registry for Psychiatric Medications and gives 1-866-961-2388 and a different website, whereas the retrieved FDA directory lists the QUVIVIQ Pregnancy Registry at 1-833-400-9611 and www.QuviviqPregnancyStudy.com. The statement that the FDA prescribing information says available postmarketing reports are insufficient is not supported by the supplied evidence, which states that there are no available data on use in pregnant women; this is a substantive source mismatch. The claims that daridorexant was approved in 2022 and that human pregnancy data may be limited are not established in the reference pool. The answer also omits the retrieved FDA-directory citation and the registry contact supported by the evidence.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/E01-gap-plain.json) · [Raw grade](paired-final/E01-gap-plain-judge.json)

### E02-maternal-pk — plain

Raw fidelity: **fail**. Raw task fulfilled: **True**.

Grader rationale (unadjudicated):

> The response fulfills the requested format: it separates effects on the pregnant person, fetal exposure, and fetal outcomes; discusses Clinical Considerations separately from individualized decisions; avoids dose values and personal medication advice; states limitations; and includes clinician questions. Several claims are supported by the supplied DailyMed label, including decreased concentrations during pregnancy with postpartum restoration, observational/epilepsy-cohort limitations, registry findings on overall malformations and oral-cleft uncertainty, and the lack of randomized pregnancy-safety trials. However, important substantive claims are not supported by the reference pool. In particular, the clauses "Lamotrigine crosses the placenta" and "Human cord-blood studies have generally found fetal concentrations that are a substantial fraction of maternal concentrations" have no supporting fetal-transfer source in the pool. The PK section also states that "One frequently cited prospective study found substantial trimester-related increases in apparent clearance and reported that lower concentrations were associated with increased seizure risk," but no retrieved abstract or supplied evidence identifies or supports that specific study result. The statements that observational pregnancy reports have not established a consistent maternal toxicity pattern, that postpartum clearance can fall rapidly, and that enzyme-inducing or enzyme-inhibiting medicines materially alter concentrations are likewise not directly supported by the supplied reference passages. The answer's cited MotherToBaby and EMA URLs are outside the reference pool, and its DailyMed citation is incomplete. These source-fidelity and citation-verification problems warrant failure despite otherwise good task fulfillment.

No independent override is applied. The rationale is a model judgment and may require source or clinician review.

[Captured answer and tool evidence](paired-final/E02-maternal-pk-plain.json) · [Raw grade](paired-final/E02-maternal-pk-plain-judge.json)

## Technical observations on passing grades

### R01 — mcp

The captured answer now includes numeric milk concentrations of 0.69 and 0.81 mg/L with ranges and sampling times, explicitly separates milk measurements from infant blood levels, and distinguishes monitoring in a study from a source recommendation. These address the two concrete omissions identified in the .5 paired answer. This is a text-level completeness observation, not clinical adjudication.

[Captured answer](paired-final/R01-mcp.json) · [Raw grade](paired-final/R01-mcp-judge.json)

### R03 — mcp

The captured answer now includes the selected DailyMed label's adult warnings and adverse reactions, a separate LactMed exposure/outcomes summary, and a comparison table. It discloses truncation and the single-product selection. The previously missing adult-warning side is present; this does not establish exhaustive label coverage or clinical accuracy.

[Captured answer](paired-final/R03-mcp.json) · [Raw grade](paired-final/R03-mcp-judge.json)

### R12 — chat

The capture and fixed notice retain the age-code subset limitation and state that these report counts cannot establish incidence, causation or generalizability. The source-contract audit records the exact returned cohort scope.

[Captured answer](chats/R12-results.json) · [Raw grade](chat-judgments/R12.json)

### P01-portfolio — chat

The source-contract audit verifies an explicit retrieved count for each requested year, including zero in the capped extract. It separately preserves the unknown full-portfolio total, avoiding an unsupported claim of zero funded projects.

[Captured answer](chats/P01-portfolio-results.json) · [Raw grade](chat-judgments/P01-portfolio.json)

### D05-brief — chat

The captured answer separates effects on the lactating person, measured infant exposure and observed infant outcomes, with a separate FAERS report-context section and clinician-preparation questions. It discloses truncated LactMed sections. The numeric exposure values are concentrations rather than administered dose regimens. This observation does not adjudicate clinical framing.

[Captured answer](chats/D05-brief-results.json) · [Raw grade](chat-judgments/D05-brief.json)

## Historical figures in the question

The .5 run cited in the question had 21/21 fidelity passes and 18/21 fulfilled research tasks, with paired tasks MCP 5/7 and plain 0/7. The earlier .4 run had 19/21 fidelity and 19/21 tasks, with paired tasks MCP 7/7 and plain 0/7. These are separate historical runs. The two paired task failures were an omitted quantitative milk summary with inferred monitoring advice, and an incomplete adult label comparison. The three research failures were an omitted FAERS subset caveat, an absent numeric empty-year count and a disputed dose allegation plus an axis-placement concern. Fresh answers, live sources and model judgments can vary. Zero plain tasks fulfilled was not a finding that every answer was false. Current totals are in summary.json and REPORT.md.

## Completeness changes

The source retains available LactMed sections, adult and population sections from one label, explicit empty-year counts, the FAERS scope caveat, distinct maternal endpoints and numeric concentration passages. The final repair preserves report-only context beside empty outcome rows and requires neutral source-attributed wording. Both paired arms receive the same production clarification. The answer prompt changed; cases, criteria and grader v2 did not. Thirty-one test cases were added since .5, including five in .9. These are development-case repairs, not independent validation.

The intermediate .6 run retained research fidelity 20/21 and tasks 20/21, with paired tasks MCP 5/7 and plain 1/7. Its R01 concentration omission persisted; E01 task flags misattributed source doses to answers. The .7 payload-only pilot also omitted concentrations. The .8 R01 pilot included numeric concentrations, but its research run retained 20/21 fidelity and 18/21 tasks, exposing report-context and framing gaps. Full .8 pairs were intentionally not run. The final .9 pilot answers are reused once in their final sets. No completed answer was regenerated within the evaluated final configuration.

## Routing regression

The original “Give me a pregnancy evidence brief for lamotrigine” question completed with medication_evidence_brief as its first evidence call. Twelve direct deployed preflight checks cover positive variants, negation, incidental mention and overriding stops. They are separate from the 28-case benchmark and 42 final MLflow rows. The matcher remains a narrow English heuristic, not exhaustive language understanding.

No clinician adjudication occurred. Raw negative scores and all completed answers remain unchanged.
