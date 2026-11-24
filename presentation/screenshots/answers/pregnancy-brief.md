# Full answer: Prepare an evidence brief for sertraline during pregnancy, with questions to ask my clinician.

Captured November 23, 2026 from the deployed Databricks App (version 0.22.2, policy 2026-11-23.29) through `chat-client/demo.sh`. Tools called: medication_evidence_brief. The text below is the answer exactly as returned.

---

## Evidence brief: sertraline during pregnancy

**Identity:** The medicine was resolved as **sertraline**, an exact ingredient match. This evidence does not establish safety or interactions for combination products. [S21](https://rxnav.nlm.nih.gov/REST/rxcui/36437/properties.json)

**Evidence status:** Evidence was retrieved, but this is a bounded summary—not a complete literature review or a safety verdict. The MCP server grouped passages heuristically; clinical framing review remains required.

### Effect on the pregnant person

- The selected DailyMed label describes a prospective longitudinal study of **201 pregnant women with a history of major depression** who were euthymic while taking antidepressants at the beginning of pregnancy. In that study, women who discontinued antidepressants during pregnancy were more likely to experience relapse than women who continued. This is treatment-context evidence from that study population and is not an individualized treatment recommendation. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)
- The label states that sertraline hydrochloride use in the month before delivery **may be associated with an increased risk of postpartum hemorrhage**. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)
- The retrieved label is **SERTRALINE HYDROCHLORIDE TABLET [REMEDYREPACK INC.]**, effective November 5, 2026. It is one selected product label, not every sertraline formulation. The pregnancy section was truncated in the returned summary, and the label’s warnings, warnings-and-precautions, boxed-warning, and drug-interactions sections were missing from the extract. Missing sections do not establish absence of information. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)

### Fetal or infant exposure

- The retrieved passages describe research measuring psychotropic-drug concentrations in maternal serum and breast milk, but the returned extract does not provide verified numeric sertraline fetal or cord-blood concentrations. [S16](https://pubmed.ncbi.nlm.nih.gov/36103361/)
- A PubMed abstract describes a population pharmacokinetic model for sertraline in women during the perinatal period using maternal plasma and breast-milk concentrations; an additional fetal compartment allowed cord-blood concentrations to be described. The returned extract does not establish the detailed study population or provide numerical concentration results. [S20](https://pubmed.ncbi.nlm.nih.gov/39030897/)
- Another abstract reports a naturalistic sample of **60 mothers**, with concentrations measured in serum and breast milk at different time points and child development observed during the first 12 months. The returned extract does not establish sertraline-specific findings or a design label. [S16](https://pubmed.ncbi.nlm.nih.gov/36103361/)

### Fetal or neonatal outcomes

- The selected label states that available published epidemiologic studies of pregnant women exposed to sertraline in the first trimester suggest no difference in major birth-defect risk compared with background rates in comparator populations. It also states that some studies reported increases for specific major birth defects, but those findings were inconclusive. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)
- The label reports a study of **831,324 infants born in Sweden from 1997–2005**. In that study, patient-reported maternal SSRI use “in early pregnancy” was associated with a PPHN risk ratio of **2.4** (95% CI 1.2–4.3); early-pregnancy SSRI use combined with an antenatal SSRI prescription “in later pregnancy” was associated with a risk ratio of **3.6** (95% CI 1.2–8.3). These findings concern SSRIs as reported in the label, not necessarily sertraline alone. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)
- A systematic review of meta-analyses examined antidepressant use during pregnancy and outcomes involving pregnant women, embryos, fetuses, newborns, and developing children. The returned abstract excerpt reports findings across antidepressants and does not provide enough sertraline-specific detail to attribute every listed outcome to sertraline. [S17](https://pubmed.ncbi.nlm.nih.gov/36853497/)
- The label includes clinical considerations concerning neonatal complications after late-pregnancy SSRI/SNRI exposure, including prolonged hospitalization, respiratory support, tube feeding, and PPHN. These are label-described risks and clinical considerations, not evidence that a particular infant experienced them. [S8](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=687ebdc4-6946-454e-8d46-3207488ccf32)

### FDA spontaneous-report context

For the returned sertraline pregnancy-exposure query, FAERS reported:

| Reported term | Reports |
|---|---:|
| Foetal exposure during pregnancy | 2,435 |
| Premature baby | 312 |
| Atrial septal defect | 308 |
| Small for dates baby | 211 |
| Drug withdrawal syndrome neonatal | 205 |
| Respiratory disorder neonatal | 177 |
| Ventricular septal defect | 175 |
| Patent ductus arteriosus | 165 |

These are reporting volumes from reports matching the query, not incidence rates, confirmed clinical outcomes, or proof of causation. An exposure denominator was unavailable, and the queried source population was not confirmed. The results cannot be generalized to all infants or all people exposed to sertraline. [S1](https://api.fda.gov/drug/event.json?search=patient.drug.openfda.generic_name%3A%22sertraline%22+AND+patient.reaction.reactionmeddrapt%3A%22foetal+exposure+during+pregnancy%22&count=patient.reaction.reactionmeddrapt.exact&limit=8) [S13](https://open.fda.gov/apis/drug/event/)

### Retrieval limitations

- The PubMed search was bounded and not systematic. [S9](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28%28%22sertraline%22%5BMeSH+Terms%5D+OR+%22sertraline%22%5BSubstance+Name%5D+OR+%22sertraline%22%5BTitle%2FAbstract%5D%29%29+AND+%28%22Pregnancy%22%5BMeSH+Terms%5D+OR+pregnan%2A%5BTitle%2FAbstract%5D+OR+gestation%2A%5BTitle%2FAbstract%5D%29&retmax=5&sort=relevance&retmode=json)
- Abstract text was retrieved for **6 of 7 requested PubMed records**. No abstract text was returned for **PMID 38133585**; this is a retrieval limitation, not evidence that the research does not exist. Titles alone were not used as outcome evidence. [S18](https://pubmed.ncbi.nlm.nih.gov/38133585/)
- The MCP server did not identify a curated federal pregnancy counterpart to LactMed in this source review. The pregnancy evidence returned here comes from product labeling and primary literature, and coverage is not exhaustive. [S25](https://www.fda.gov/drugs/labeling/questions-and-answers-pregnancy-and-lactation-labeling-rule) [S26](https://www.ncbi.nlm.nih.gov/books/NBK501922/)
- No relevant **RECRUITING** sertraline-and-pregnancy study was returned by the filtered ClinicalTrials.gov query. This means no record was returned by that query; it does not establish that no other study exists. [S2](https://clinicaltrials.gov/api/v2/studies?query.term=sertraline+AND+%28pregnancy%29&filter.overallStatus=RECRUITING&pageSize=20&format=json)

## Questions to ask your clinician

1. Does this evidence apply to my exact sertraline product, formulation, and any other active ingredients?
2. How closely do these study populations match my pregnancy, including gestational stage and relevant medical conditions?
3. Which findings are measured exposure, and which are observed clinical outcomes?
4. How should the findings about the treated condition and the pregnancy-related findings be considered together in my situation?
5. What information is missing from the label or studies that matters for my circumstances?
6. What follow-up questions should we address for pregnancy and the newborn?
7. Would a pharmacist or perinatal psychiatry specialist add useful context?

**Continuity notice from the MCP server:** Stopping or changing a medication can also carry risks. Discuss changes with the prescribing clinician. This tool cannot advise starting, stopping, or changing treatment.

Application limits:
These FAERS results cover only the queried report subset. They cannot be generalized to all infants or all people exposed to the medicine, and cannot establish incidence or causation.
Human clinical framing review remains required. This generated answer is not clinically validated.
Stopping or changing a medication can also carry risks. Discuss changes with the prescribing clinician. This tool cannot advise starting, stopping, or changing treatment.
PubMed abstract coverage: abstract text was retrieved for 6 of 7 requested PMIDs. No abstract text was returned for PMID(s): 38133585. Missing abstract text is a retrieval limitation, not evidence that a study or research does not exist. Titles alone are not outcome evidence.
Structured evidence rows (retrieval inventory)
| Evidence axis | Extracted findings | Context-only passages | Gap statements |
|---|---|---:|---:|
| Effect on the pregnant or lactating person | 3 extracted candidate passages; source interpretation requires review. | 0 | 2 |
| Measured transfer or exposure to fetus or infant | 6 extracted candidate passages; source interpretation requires review. | 0 | 3 |
| Observed outcomes in fetus or infant | 6 extracted candidate passages; source interpretation requires review. | 2 | 3 |
These are counts of extracted passages, not studies or proven effects. Context-only passages and gap statements are counted separately. Empty rows do not establish absence of evidence elsewhere or safety. This inventory does not replace the cited findings or validate applicability.

Informational only; not medical advice. Compiled from public NIH/NLM/FDA data, which may be incomplete or out of date. Patients should talk to a clinician, pharmacist or poison control before starting, stopping or changing any medication.
