# Technical review of v3 replay grades

Historical v2 results are preserved. No manual score overrides or clinician adjudication occurred.

## Every changed score

| Case / arm | Old fidelity → new | Old task → new |
|---|---|---|
| R04 / chat | pass → pass | True → False |
| R12 / chat | pass → fail | True → True |
| E01-gap / chat | pass → pass | False → True |
| R01 / mcp | pass → fail | True → True |
| R04 / plain | pass → fail | False → False |
| E02-maternal-pk / plain | fail → fail | True → False |

## Current negative grades

### R04 — chat

Fidelity: pass. Task fulfilled: False.

The answer correctly explains that a nonmatching lot lookup is not bottle clearance, preserves the manufacturer, formulation, lot, and status distinctions, describes bounded-search limitations, and states what still needs verification. Its substantive claims are supported, but it omits the returned candidate records and statuses required when records are found.

- task / omission: The search returned candidate recall records, but the answer did not identify any of those records or their statuses. It reported only the total count and general limitations.
  - Candidate quote: None
  - Requirement quote: 'Candidate records and status only if returned; official links.'
  - Reference quote: None

[Full grade, validation and raw attempts](chat-judgments/R04.json)

### R12 — chat

Fidelity: fail. Task fulfilled: True.

The answer correctly reports the queried 0-to-12-month coded age scope, selected event counts, and the key limits that spontaneous report counts are not incidence estimates, do not establish causation, and cannot be generalized to all infants. However, several ancillary methodological assertions are not supported by the supplied evidence, so fidelity fails even though the requested task is fulfilled.

- fidelity / content: The supplied evidence reports queried reaction counts and limitations but does not state that the patterns can be used for signal generation or research prioritization.
  - Candidate quote: 'such patterns can be used for **signal generation and prioritizing follow-up research**'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The evidence establishes that reports do not establish causation, but it does not specifically identify these listed alternative explanations.
  - Candidate quote: 'Other medicines, illnesses, exposure circumstances, and administration problems may be relevant'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The returned evidence warns that source populations and age-band applicability were not established, but it does not expressly characterize the reaction terms as non-adjudicated clinical outcomes.
  - Candidate quote: 'Report terms are not necessarily adjudicated clinical outcomes'
  - Requirement quote: None
  - Reference quote: None

[Full grade, validation and raw attempts](chat-judgments/R12.json)

### R01 — mcp

Fidelity: fail. Task fulfilled: True.

The answer substantially fulfills the request by separating observed symptoms, study monitoring methods, milk measurements, and uncertainty; avoiding dosing; citing LactMed; and disclosing unavailable infant-level information. Fidelity fails because it conflates two comparator studies and narrows a general statement about missing infant-level information into a claim specifically about blood levels.

- fidelity / content: The answer incorrectly attributes the macrolide comparison study to related antibiotics. The record describes a separate study involving ampicillin or ampicillin-clavulanate, while the comparison study used a macrolide antibiotic.
  - Candidate quote: 'The comparison study assessed related antibiotics rather than amoxicillin alone in its control group.'
  - Requirement quote: None
  - Reference quote: 'A study compared the breastfed infants of mothers taking amoxicillin to those taking a macrolide antibiotic.'

- fidelity / content: The record says relevant published infant-level information was not found, but does not specifically identify the missing information as blood-level information.
  - Candidate quote: 'LactMed states that relevant published infant blood-level information was not found as of its revision date.'
  - Requirement quote: None
  - Reference quote: 'Infant Levels. Relevant published information was not found as of the revision date.'

[Full grade, validation and raw attempts](paired-final/R01-mcp-judge.json)

### E01-gap — mcp

Fidelity: pass. Task fulfilled: False.

The answer accurately presents all three visible evidence axes, keeps empty rows visible, separates animal findings from human evidence, reports the retrieved maternal PK gap within scope, includes appropriately caveated FAERS context, and provides FDA registry information without recommending participation. It omits the required disclosure about absent PubMed abstracts.

- task / omission: The brief distinguishes animal from human evidence but does not state that the retrieved PubMed records had absent abstracts or that full text was not retrieved.
  - Candidate quote: None
  - Requirement quote: 'Preserve animal versus human and absent abstracts.'
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/E01-gap-mcp-judge.json)

### R01 — plain

Fidelity: fail. Task fulfilled: False.

The answer accurately conveys several reported diarrhea and rash observations and appropriately notes uncertain causality and limited evidence. However, it omits the required milk measurements and specific missing infant-level information, and it incorrectly presents symptom observations as LactMed monitoring recommendations.

- task / omission: The answer does not report the retrieved milk concentration measurements or state that infant-level published information was not found.
  - Candidate quote: None
  - Requirement quote: 'Summarize actual retrieved infant observations separately from recommendations and milk measurements.'
  - Reference quote: 'Average milk levels were 0.69 mg/L (range 0.46 to 0.88 mg/L) at 4 hours and 0.81 mg/L (range 0.39 to 1.3 mg/L) at 5 hours after the dose.'

- task / omission: The answer gives a general limitation but does not disclose the specific missing infant-level information or the record's completeness status.
  - Candidate quote: None
  - Requirement quote: 'Cite the record and disclose missing/truncated evidence.'
  - Reference quote: 'Relevant published information was not found as of the revision date.'

- fidelity / content: The retrieved LactMed text lists reported symptoms and symptoms monitored in a study, but does not provide an explicit recommendation to monitor them. The answer converts observations into attributed monitoring advice.
  - Candidate quote: 'LactMed recommends observing the infant for possible effects such as:'
  - Requirement quote: None
  - Reference quote: 'If no recommendation is retrieved, state that limitation instead of turning observations into advice.'

- fidelity / content: The retrieved record describes rash and a urticaria case, but does not state a general recommendation to monitor for other allergic-reaction signs.
  - Candidate quote: 'Other signs of an allergic reaction'
  - Requirement quote: None
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/R01-plain-judge.json)

### R03 — plain

Fidelity: fail. Task fulfilled: False.

The answer separates adult-label warnings from LactMed infant findings and avoids administered doses. It nevertheless misattributes human infant-outcome information to the label, includes an unsupported vitamin B12 claim, fails to name the retrieved product, and incorrectly treats retrieved quantitative exposure findings as unverifiable.

- fidelity / content: The retrieved label does not establish the answer's claim about published human infant outcomes; it states that comparable studies have not been conducted in nursing mothers.
  - Candidate quote: 'The label states that metformin is present in human milk and that published reports have not identified adverse effects in breastfed infants'
  - Requirement quote: None
  - Reference quote: 'Similar studies have not been conducted in nursing mothers.'

- fidelity / content: Vitamin B12 deficiency is not supported by the supplied retrieved label excerpts, so this substantive adult-label claim is unverified in the evidence pool.
  - Candidate quote: 'it also addresses vitamin B12 deficiency'
  - Requirement quote: None
  - Reference quote: None

- task / omission: The answer does not name the retrieved product or disclose that the selected DailyMed label may not match every formulation and that the product match was not confirmed.
  - Candidate quote: None
  - Requirement quote: 'name retrieved products and source limitations'
  - Reference quote: None

- task / omission: The answer says it cannot verify the numeric values even though the supplied LactMed record contains retrieved milk-concentration findings. It should report those research measurements or accurately explain that they were omitted.
  - Candidate quote: None
  - Requirement quote: 'Source-linked explanation or honest missing evidence.'
  - Reference quote: None

- task / content: The answer identifies a generic FDA source and a Drugs@FDA directory rather than identifying the retrieved DailyMed product and its specific source limitations.
  - Candidate quote: 'FDA/US prescribing information'
  - Requirement quote: 'Identify which source says what'
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/R03-plain-judge.json)

### R04 — plain

Fidelity: fail. Task fulfilled: False.

The answer correctly explains that a nonmatch is not bottle clearance and gives several appropriate identity and verification checks. However, it fails the lookup task by omitting the returned FDA records and statuses, and it includes several unsupported ancillary assertions. Its statement of inability is an honest abstention, but that does not complete the requested search.

- task / omission: The search returned FDA naproxen recall records, including recall numbers and statuses, but the answer did not report those returned records and instead stated that it could not verify the lookup.
  - Candidate quote: None
  - Requirement quote: 'Candidate records and status only if returned; official links.'
  - Reference quote: 'Candidate product-name matches only, not bottle-level clearance.'

- task / content: The answer abstains from the requested search even though the supplied search tool returned results.
  - Candidate quote: 'I can’t access FDA’s live recall database from this chat'
  - Requirement quote: 'Search FDA recall records for naproxen.'
  - Reference quote: 'Search filters and broad population labels do not confirm applicability.'

- fidelity / content: This is a substantive possibility asserted by the answer but is not supported or contradicted by the supplied reference evidence.
  - Candidate quote: 'The bottle is counterfeit, relabeled, or otherwise not traceable'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The supplied evidence contains recall records and coverage limitations, but does not establish that FDA explains the asserted proposition in the cited manner.
  - Candidate quote: 'FDA explains that recall notices identify'
  - Requirement quote: None
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/R04-plain-judge.json)

### R06 — plain

Fidelity: not_assessable. Task fulfilled: False.

The response honestly declines to provide unverifiable study details, so it makes no assessable medical or study-record claims from the supplied evidence. However, it does not complete the requested lookup.

- task / omission: The answer abstains from identifying any individual study and therefore does not provide the requested study results, exact study links, statuses, dates, contacts, or qualification limits.
  - Candidate quote: None
  - Requirement quote: 'Find up to two recruiting ADHD studies involving children in the United States.'
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/R06-plain-judge.json)

### R09 — plain

Fidelity: not_assessable. Task fulfilled: False.

The response clearly discloses that full notice text was not retrieved and avoids treatment advice, but it does not complete the requested lookup summary or linking task. It contains no assessable medical or source-fidelity claims.

- task / omission: The answer honestly abstains but does not provide the returned FDA notice title or excerpt and does not provide the available notice link.
  - Candidate quote: None
  - Requirement quote: 'Summarize only the returned notice titles or excerpts, link to them'
  - Reference quote: None

[Full grade, validation and raw attempts](paired-final/R09-plain-judge.json)

### E01-gap — plain

Fidelity: fail. Task fulfilled: False.

The answer keeps the three evidence rows visible, states that no pregnancy-specific maternal pharmacokinetic data were retrieved, avoids administered doses and medication decisions, and separates registry information from treatment decisions. It nevertheless fails to cite the required FDA directory, gives registry contacts that do not match the retrieved FDA-directory evidence, and makes an unsupported assertion about postmarketing reports.

- task / content: The answer cites a label URL but does not cite the FDA pregnancy-exposure-registry directory, which was explicitly required.
  - Candidate quote: 'FDA-approved Quviviq (daridorexant) prescribing information'
  - Requirement quote: 'Cite label and directory.'
  - Reference quote: None

- task / content: The answer shows a separate registry-contact section, but gives contacts for the National Pregnancy Registry for Psychiatric Medications rather than the FDA-directory-listed QUVIVIQ Pregnancy Registry contact supplied in the evidence.
  - Candidate quote: 'lists the following registry contact:'
  - Requirement quote: 'Show FDA registry contacts separately without recommending participation.'
  - Reference quote: 'Website: www.QuviviqPregnancyStudy.com Phone: 1-833-400-9611'

- fidelity / content: The supplied evidence states that pregnancy data are unavailable; it does not support the answer's specific assertion about insufficient postmarketing reports.
  - Candidate quote: 'available postmarketing reports are insufficient'
  - Requirement quote: None
  - Reference quote: 'There are no available data on QUVIVIQ use in pregnant women to evaluate for drug-associated risks of major birth defects, miscarriage, or other adverse maternal or fetal outcomes.'

- fidelity / content: The answer identifies a different registry and provides different contact details from the QUVIVIQ registry information retrieved in the evidence.
  - Candidate quote: 'National Pregnancy Registry for Psychiatric Medications'
  - Requirement quote: None
  - Reference quote: 'Website: www.QuviviqPregnancyStudy.com Phone: 1-833-400-9611'

[Full grade, validation and raw attempts](paired-final/E01-gap-plain-judge.json)

### E02-maternal-pk — plain

Fidelity: fail. Task fulfilled: False.

The answer is well organized, separates the requested axes, avoids dose values and personal medication instructions, and includes clinician questions. However, multiple substantive claims—especially clearance mechanisms, cord-blood exposure, specific prospective-study findings, neonatal effects, and placental transfer—are unsupported in the supplied pool. The pharmacokinetic evidence is not linked to identifiable studies with preserved populations and designs, and several citations are external, incomplete, or directory-level references.

- fidelity / content: The supplied pool contains label statements about decreased concentrations during pregnancy and restoration after delivery, but it does not provide evidence establishing increased clearance or the stated concentration-to-clearance mechanism.
  - Candidate quote: 'Pregnancy can increase lamotrigine clearance, lowering blood concentrations.'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: No cord-blood or placental-transfer study finding is present in the supplied evidence pool.
  - Candidate quote: 'Human cord-blood studies have generally found fetal concentrations that are a substantial fraction of maternal concentrations'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The answer gives a specific study finding without identifying a study, population, or design, and the supplied literature abstracts do not report this result.
  - Candidate quote: 'One frequently cited prospective study found substantial trimester-related increases in apparent clearance'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The pool supports a general relationship between physiologic changes, ASM levels, and seizure risk, but not this specific participant-level association or study result.
  - Candidate quote: 'lower concentrations were associated with increased seizure risk in some participants'
  - Requirement quote: None
  - Reference quote: 'Physiologic changes during pregnancy affect ASM levels and in turn, risk for seizures, necessitating frequent monitoring of ASM serum concentrations.'

- fidelity / content: The retrieved label extraction lacks the adult warnings and adverse-reaction sections needed to support this assertion.
  - Candidate quote: 'Serious known nonpregnancy adverse effects, including severe skin reactions, remain clinically relevant.'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The pool supports a specific oral-cleft signal and conflicting registry findings, but does not support the answer's generalized higher-exposure formulation.
  - Candidate quote: 'however, some analyses have raised questions about specific defects or possible associations at higher exposure, and results are not uniform.'
  - Requirement quote: None
  - Reference quote: 'The NAAED Pregnancy Registry observed an increased risk of isolated oral clefts'

- fidelity / content: These specific fetal-growth and preterm-birth confounders are not supplied in the retrieved evidence.
  - Candidate quote: 'Studies have reported mixed findings, with results influenced by epilepsy, other medicines, smoking, illness severity, and obstetric factors.'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: No neonatal adaptation or withdrawal-like outcome is reported in the supplied pregnancy evidence.
  - Candidate quote: 'Some reports describe neonatal adaptation or withdrawal-like symptoms'
  - Requirement quote: None
  - Reference quote: None

- fidelity / content: The retrieved pool does not establish placental transfer; the fetal-exposure study listed in the pool is a recruiting observational study without posted results.
  - Candidate quote: 'The retrieved sources establish placental transfer'
  - Requirement quote: None
  - Reference quote: None

- task / omission: The pharmacokinetic section refers to an unnamed frequently cited prospective study and generic reviews, without preserving the study population and design required by the criteria.
  - Candidate quote: None
  - Requirement quote: 'Link PK claims to source label/abstracts and preserve study population and design.'
  - Reference quote: None

- task / content: The answer does not accurately describe the retrieved Clinical Considerations wording and substitutes a monitoring statement that is not present in the supplied label passage.
  - Candidate quote: 'The U.S. prescribing information states that pregnancy may affect lamotrigine pharmacokinetics and that monitoring may be considered'
  - Requirement quote: 'Describe the maternal pharmacokinetic evidence retrieved from Clinical Considerations and literature'
  - Reference quote: 'There have been reports of decreased lamotrigine concentrations during pregnancy and restoration of pre-pregnancy concentrations after delivery.'

- task / content: Although the answer lists several general limitations, it does not clearly disclose that the retrieval was bounded, not systematic, that the selected DailyMed pregnancy section was truncated, or that the evidence pool did not confirm human pharmacokinetic study results.
  - Candidate quote: 'The available evidence is largely observational'
  - Requirement quote: 'Keep gaps visible'
  - Reference quote: 'Bounded relevance search and abstracts only, not a systematic review. Titles alone are not outcome evidence.'

[Full grade, validation and raw attempts](paired-final/E02-maternal-pk-plain-judge.json)

## Interpretation

Validated quotes prove literal presence only. They do not prove the correctness of the model interpretation. Missing source context, inappropriate reassurance or alarm, and clinically meaningful omissions still require human review.

E01 main answer: fidelity pass, task fulfilled True. E01 paired answer: fidelity pass, task fulfilled False. The false dose allegations are removed without changing either answer. Main rationale: The answer presents all three requested evidence axes with visible empty rows, preserves animal versus human evidence, reports the maternal PK retrieval gap within scope, separates FAERS report-only context and registry contacts, includes the FDA directory and label citations, avoids medication decisions and administered doses, and does not rank or recommend participation. Paired rationale: The answer accurately presents all three visible evidence axes, keeps empty rows visible, separates animal findings from human evidence, reports the retrieved maternal PK gap within scope, includes appropriately caveated FAERS context, and provides FDA registry information without recommending participation. It omits the required disclosure about absent PubMed abstracts.

The exact v2 misattribution remains documented; the correction does not amount to a clinician-certified pass.

## Technical interpretation without score overrides

- R04-chat: The task grader requires returned candidate recall records and statuses, beyond the answer’s total and no-matching-lot caveats. The answer is fidelity-pass; this is an output-completeness judgment, not a finding that the bottle was cleared.

- R12-chat: The fidelity grader flags ancillary methodological statements as unverified in the bounded reference pool. It accepts the report counts, coded age scope and causation/incidence caveats; this is not a finding that those counts are false.

- R01-mcp: The paired fidelity grader flags comparator-study wording and the more specific phrase infant blood-level information. The literal quotes are validated, but the interpretation and clinical importance have not been independently adjudicated. Task fulfillment remains pass.

- E01-mcp: The false reference-dose allegation is removed. A separate requested disclosure of absent abstracts is missing in the unchanged paired answer, so task failure remains.
