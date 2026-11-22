# Raw diagnostic flags and benchmark failures

Fidelity asks whether claims are supported by the captured, bounded evidence pool. Task fulfillment asks whether the requested requirements were met. They are separate, fallible same-family model judgments. Quote checks and URL membership do not establish relevance, medical truth or safety. All negative grades and raw rationales are retained; there were no manual score overrides or clinician adjudication.

The 28 development questions and seven paired questions retain grader v3 and the prior case definitions. There is one retained completed answer per case/arm; live sources, source caches, snapshots and generation variability affect results. Only MCP has retrieval, preflight and required notices. The companion also has a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer did not receive. No clinical-accuracy, speed or general-superiority claim follows.

The separate ten-question Phoenix benchmark uses a fixed MPRINT snapshot, independently explored read-only questions, an XML/CSV registry and exact string comparison. Only the two MPRINT evidence tools are exposed after preflight. Three research questions were conservatively blocked (two language gates and one urgent gate); other failures include arithmetic, record linkage and UNKNOWN answers. This is a newly authored known benchmark, not a held-out or clinical validation set. Its 3/10 result must not be merged with or substituted for the seven-case paired score. Three questions are moderate difficulty, and some share cohorts.

## R03 — mcp

Fidelity: **fail**. Task fulfilled: **True**.

The answer separates adult label warnings from LactMed infant findings, identifies the retrieved product and sources, discloses extraction and population limitations, and avoids administered doses. Most substantive claims are supported. Fidelity is reduced by one unsupported claim about lactic acidosis not being reported in the infants.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Does not report lactic acidosis in the breastfed infants described",
    "reference_quote": null,
    "explanation": "The supplied LactMed extract reports infant outcomes and exposure findings but does not explicitly establish the absence of lactic acidosis; this is an unsupported absence claim rather than a directly reported observation."
  }
]
```

## E01-gap — plain

Fidelity: **fail**. Task fulfilled: **False**.

The answer is an honest abstention and correctly keeps the three evidence axes visible, avoids dosing and medication decisions, and appropriately cautions that missing data do not establish safety. However, it fails the requested brief because it treats available retrieved evidence as unavailable, omits the animal findings, provides no FDA registry contacts, and includes no required label or directory citations.

```json
[
  {
    "dimension": "task",
    "kind": "content",
    "requirement_quote": "Show FDA registry contacts separately without recommending participation.",
    "answer_quote": "No FDA pregnancy-registry contact information was retrieved and verified in this session.",
    "reference_quote": "Website: www.QuviviqPregnancyStudy.com Phone: 1-833-400-9611",
    "explanation": "The supplied evidence contained FDA directory registry contact information, so the answer failed to provide the required contacts."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Prepare a pregnancy evidence brief for daridorexant.",
    "answer_quote": null,
    "reference_quote": "In animal reproduction studies, oral administration of daridorexant to pregnant rats and rabbits during the period of organogenesis did not cause fetal toxicity or malformation at doses up to 8 and 10 times the maximum recommended human dose (MRHD) of 50 mg, respectively, based on AUC.",
    "explanation": "The answer explicitly left animal or nonhuman findings unsummarized, although the retrieved label contained relevant animal pregnancy findings that should have been preserved separately from human evidence."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Cite label and directory.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer supplied no citations, despite the criteria expressly requiring citation of the label and FDA directory."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "No FDA pregnancy-registry contact information was retrieved and verified in this session.",
    "reference_quote": "There will be a pregnancy exposure registry that monitors pregnancy outcomes in women exposed to QUVIVIQ during pregnancy. Pregnant women exposed to QUVIVIQ and healthcare providers are encouraged to call Idorsia Pharmaceuticals Ltd at 1-833-400-9611.",
    "explanation": "This statement conflicts with the supplied retrieval, which included registry contact information and an FDA directory listing."
  }
]
```

## E02-maternal-pk — plain

Fidelity: **fail**. Task fulfilled: **False**.

The answer uses the requested three-axis structure, avoids dose values and personal medication advice, keeps several gaps visible, and includes clinician questions. It nevertheless fails because it misstates the retrieved literature coverage, does not accurately report the supplied DailyMed Clinical Considerations evidence, omits study populations and designs, and adds unsupported claims including umbilical-cord transfer and neonatal adaptation.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "PubMed abstract coverage was not completed",
    "reference_quote": "Requested PubMed records only; not a complete literature review.",
    "explanation": "The answer says abstract coverage was not completed, but the supplied retrieval reports abstracts for all eight requested records; the actual limitation was that the search was bounded and not a complete literature review."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "lamotrigine clearance commonly increases during pregnancy",
    "reference_quote": "There have been reports of decreased lamotrigine concentrations during pregnancy and restoration of pre-pregnancy concentrations after delivery.",
    "explanation": "The supplied evidence supports decreased concentrations and postpartum restoration, but does not establish the stronger claim that clearance commonly increases."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "particularly UGT-mediated metabolism",
    "reference_quote": null,
    "explanation": "The supplied pregnancy evidence does not support this specific mechanistic assertion."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Lamotrigine has been measured in umbilical-cord blood",
    "reference_quote": null,
    "explanation": "No umbilical-cord-blood or placental-transfer study finding appears in the supplied evidence pool."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Neonatal adaptation or withdrawal-like effects have been described",
    "reference_quote": null,
    "explanation": "The supplied evidence does not report lamotrigine-specific neonatal adaptation or withdrawal-like effects in pregnancy."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Link PK claims to source label/abstracts and preserve study population and design.",
    "answer_quote": null,
    "reference_quote": "There have been reports of decreased lamotrigine concentrations during pregnancy and restoration of pre-pregnancy concentrations after delivery.",
    "explanation": "The answer does not link its principal PK claims to the supplied DailyMed Clinical Considerations source or preserve the actual populations and designs of the retrieved literature."
  },
  {
    "dimension": "task",
    "kind": "content",
    "requirement_quote": "Describe the maternal pharmacokinetic evidence retrieved from Clinical Considerations and literature",
    "answer_quote": "A verified lamotrigine-specific Clinical Considerations document was not available for direct citation here.",
    "reference_quote": "As with other AEDs, physiological changes during pregnancy may affect lamotrigine concentrations and/or therapeutic effect.",
    "explanation": "The supplied evidence did include lamotrigine-specific DailyMed Clinical Considerations, so the answer incorrectly presents that retrieved source as unavailable and fails to describe it accurately."
  },
  {
    "dimension": "task",
    "kind": "content",
    "requirement_quote": "Distinguish effects on the pregnant person, fetal exposure, and fetal outcomes.",
    "answer_quote": "Neonatal adaptation or withdrawal-like effects have been described as a possible consideration",
    "reference_quote": null,
    "explanation": "Although the answer uses three headings, this fetal-outcomes content is unsupported in the supplied evidence and does not clearly identify the actual retrieved evidence and its limits."
  }
]
```

## R01 — plain

Fidelity: **fail**. Task fulfilled: **False**.

The answer appropriately avoids dosing and expresses some valid uncertainty, but it mainly abstains despite a retrieved, non-truncated record. It omits the specific infant observations, milk measurements, and explicit statement that no separate monitoring recommendation was retrieved. Its citation does not match the amoxicillin record.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Summarize actual retrieved infant observations separately from recommendations and milk measurements.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer declines to provide the retrieved infant observations, monitoring-recommendation limitation, and milk concentration findings."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Cite the record and disclose missing/truncated evidence.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer does not cite the retrieved amoxicillin record and does not disclose the actual evidence status: the record was retrieved, its expected sections were returned, and it was not truncated."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "https://www.ncbi.nlm.nih.gov/books/NBK501922/",
    "reference_quote": "https://www.ncbi.nlm.nih.gov/books/NBK500887/",
    "explanation": "The supplied citation points to a different record than the retrieved LactMed amoxicillin entry."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Any LactMed recommendation to watch for diarrhea, rash, thrush, or other effects is guidance",
    "reference_quote": "If no recommendation is retrieved, state that limitation instead of turning observations into advice.",
    "explanation": "The retrieved record reports observed effects and monitored study parameters but does not provide an explicit recommendation to monitor them; the answer presents a hypothetical LactMed recommendation without identifying that no such recommendation was retrieved."
  }
]
```

## R03 — plain

Fidelity: **fail**. Task fulfilled: **False**.

The answer separates adult label warnings from infant observations and avoids administered doses, but it omits the retrieved product identity and incorrectly adds or characterizes several claims, including vitamin B12 deficiency, breastfeeding compatibility, infant monitoring advice, and the availability of infant serum measurements. It also uses an invalid DailyMed citation URL.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "vitamin B12 deficiency as potential adverse effects",
    "reference_quote": null,
    "explanation": "The supplied label evidence does not contain vitamin B12 deficiency among the retrieved warnings or adverse reactions."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "generally considered compatible with breastfeeding",
    "reference_quote": null,
    "explanation": "The supplied LactMed evidence reports low milk levels, observed infant findings, and caution for certain infants, but does not state this general compatibility conclusion."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "some experts recommend monitoring the infant for gastrointestinal effects",
    "reference_quote": null,
    "explanation": "The supplied LactMed extract does not provide this monitoring recommendation."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Infant specimen type and infant concentration data were not verified",
    "reference_quote": "Serum levels were measured in 4 breastfed infants",
    "explanation": "The retrieved LactMed text explicitly identifies infant serum measurements, so presenting infant concentration data as unverified misrepresents the available record."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "name retrieved products and source limitations",
    "answer_quote": null,
    "reference_quote": "METFORMIN HCL TABLET [QPHARMA, INC.]",
    "explanation": "The answer refers generally to a DailyMed label but does not name the retrieved product, METFORMIN HCL TABLET [QPHARMA, INC.]."
  }
]
```

## R04 — plain

Fidelity: **pass**. Task fulfilled: **False**.

The answer correctly explains that a nonmatch is not bottle clearance and appropriately preserves formulation, manufacturer, lot, and status distinctions in its verification guidance. Its bounded-search and safety caveats are consistent with the evidence. However, it incorrectly treats the requested lookup as unavailable and omits the returned FDA candidate records, their statuses, and the actual bounded-search result. The citations are relevant-looking official links but are not directly supported by the supplied evidence inventory.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Search FDA recall records for naproxen.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer abstains from reporting the available bounded FDA search result, including that NOTREAL-77 was not found and the returned naproxen recall records and statuses."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Candidate records and status only if returned; official links.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The supplied search returned candidate records with recall numbers and statuses, but the answer provides only a placeholder table and does not identify those records or statuses."
  }
]
```

## R06 — plain

Fidelity: **not_assessable**. Task fulfilled: **False**.

The response is an honest abstention and makes no substantive study-specific medical or registry claims to assess for source fidelity. However, it does not complete the requested lookup, although the supplied evidence includes two relevant recruiting studies.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Find up to two recruiting ADHD studies involving children in the United States.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer declines to identify any studies, despite the supplied evidence containing two recruiting U.S. pediatric ADHD studies."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Include exact study links, overall and site status if present, update dates, contacts and qualification limits.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer provides only a general search link and a checklist of information to look for; it does not provide the requested study-specific links, statuses, dates, contacts, or qualification limits."
  }
]
```

## R09 — plain

Fidelity: **fail**. Task fulfilled: **False**.

The response honestly discloses a lookup limitation and avoids treatment advice, but it does not fulfill the requested summary-and-link task and incorrectly says that no returned records were available despite a returned FDA notice.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Summarize only the returned notice titles or excerpts, link to them, and explain if full notice text was not retrieved.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer abstains instead of providing the returned FDA notice title, its link, and the requested explanation that the full notice text was not retrieved."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Returned records:** None available from a live search",
    "reference_quote": "FDA requires Boxed Warning about serious mental health side effects for asthma and allergy drug montelukast (Singulair); advises restricting use for allergic rhinitis",
    "explanation": "The supplied search results contain a returned FDA notice record, so stating that no returned records were available conflicts with the evidence."
  }
]
```

## R07 — chat

Fidelity: **pass**. Task fulfilled: **False**.

The answer accurately reports the single returned Canadian recruiting record, includes a direct study link and contact, preserves the indirect-match and bounded-search caveats, and does not substitute completed studies or make an exhaustive absence claim. Its only task omission is the lack of an explicit instruction that the study team must confirm eligibility.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Eligibility must be confirmed by study team.",
    "answer_quote": null,
    "reference_quote": "Study team must confirm site recruitment and eligibility; registry status can be stale.",
    "explanation": "The answer appropriately states that eligibility and current site availability were not confirmed, but it does not clearly tell the reader to confirm eligibility with the study team, as required."
  }
]
```

## R08 — chat

Fidelity: **pass**. Task fulfilled: **False**.

The notices, dates, relevance labels, uncertainty caveats, links, bounded-search disclosure, and no-submission statement are well supported by the evidence. The main task defect is labeling the dated past notices as past listed deadlines rather than clearly separating a closed-deadlines category as requested.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Separate verified future deadlines, closed deadlines and unknown deadlines",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer separates future, past listed, and unknown deadlines, but does not provide the requested explicitly labeled closed-deadlines category. It appropriately cautions that past dates do not independently verify portal closure, but the requested category is still not clearly supplied."
  }
]
```

## R09 — chat

Fidelity: **pass**. Task fulfilled: **False**.

The notice title, date, link, and limitations about full-text retrieval and current-index coverage are supported. The answer contains no contradicted or unverified medical claims and gives no personal treatment recommendation, but it includes an extra metadata statement outside the requested title-or-excerpt-only scope.

```json
[
  {
    "dimension": "task",
    "kind": "content",
    "requirement_quote": "Summarize only the returned notice titles or excerpts, link to them, and explain if full notice text was not retrieved.",
    "answer_quote": "The returned metadata did not establish a source population or age band for this notice.",
    "reference_quote": null,
    "explanation": "The answer adds population and age-band metadata rather than limiting the response to the returned notice title or excerpt and the explanation that the full notice text was not retrieved."
  }
]
```

## Fixed-snapshot benchmark

| Case | Expected | Actual | Exact match |
|---|---|---|---|
| B01 | 23.44 | 23.96 | False |
| B02 | Site 4 | Site 4 | True |
| B03 | 10.1007/s00737-018-0905-3 | 10.1007/s00737-018-0905-3 | True |
| B04 | 2 | 1 | False |
| B05 | 376 | 376 | True |
| B06 | Estradiol | UNKNOWN | False |
| B07 | 89.1 | UNKNOWN | False |
| B08 | 60 | UNKNOWN | False |
| B09 | 10.1016/j.ejogrb.2008.02.003 | UNKNOWN | False |
| B10 | 65.9 | UNKNOWN | False |
