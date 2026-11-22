# Diagnostic flags and exact benchmark results

Fidelity asks whether claims are supported by the captured references. Task fulfillment asks whether all requested requirements were met. Neither is clinical accuracy. These are known development cases, one retained completed answer per case/arm, bounded references and a fallible same-family model judge. There was no clinician adjudication, manual score override or selection of a better completed answer. Live sources and model outputs vary. Other clients must enforce preflight and display contracts themselves.

The seven-case comparison measures the MCP workflow, including tools, preflight and required notices. The plain arm has no retrieval tools; 0/7 can reflect honest inability to verify a current lookup, not seven fabricated or medically wrong answers. Both arms receive the same updated instructions. The paired runner omits the companion’s additional source-review pass.

The ten-question benchmark is an exact-answer test of joins, filters, candidate selection and arithmetic against a fixed MPRINT snapshot. It is separate from the chat and paired scores. It is small, known, partly cohort-sharing and not held out. Runtime and client instructions changed together, so any gain is not a controlled estimate of one fix. Exact agreement with snapshot fields does not establish clinical truth, safety, source completeness or performance across all 30 tools.

The judge prompt is unchanged. Grader v3.1 now rejects a negative finding based only on the exact mandatory application footer, enforcing an existing rubric rule. It requests a new bounded model judgment and never sets a failed score to pass in code. Semantic grading errors remain possible. R08 alone has the disclosed criterion clarification above; other criteria and every question are unchanged. Heuristic routing and independent review of framing, omissions and evidence gaps remain limitations.

## E01-gap — plain

Fidelity: fail. Task fulfilled: False.

The answer correctly keeps all three evidence rows visible, avoids dosing and medication decisions, and states a bounded maternal-PK gap. It nevertheless fails to provide the retrieved registry contacts, required label and directory citations, animal-versus-human distinction, and absent-abstract disclosure. It also incorrectly says the registry contact and source retrieval were not verified.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Show FDA registry contacts separately without recommending participation.",
    "answer_quote": null,
    "reference_quote": "Website: www.QuviviqPregnancyStudy.com Phone: 1-833-400-9611",
    "explanation": "The answer does not display the retrieved registry website and telephone contact separately."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Cite label and directory.",
    "answer_quote": null,
    "reference_quote": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3a2d1503-b816-40c9-9fac-7e03c5a3bcef",
    "explanation": "The answer does not cite the supplied DailyMed label or the supplied FDA pregnancy-exposure-registry directory."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Preserve animal versus human and absent abstracts.",
    "answer_quote": null,
    "reference_quote": "No abstract text was returned for PMID(s): 36630579, 35802843, 36630580.",
    "explanation": "The answer omits the retrieved animal findings and does not disclose that the three retrieved PubMed records had no returned abstracts."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "A current FDA pregnancy-exposure registry contact for daridorexant was **not verified in the available retrieval**.",
    "reference_quote": "QUVIVIQ Pregnancy Registry",
    "explanation": "The supplied retrieval identified the QUVIVIQ Pregnancy Registry and supplied its contact information, so describing the contact as not verified is inconsistent with the evidence."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "I could not verify live source records or retrieve current FDA labeling, registry pages, or published study abstracts in this session.",
    "reference_quote": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3a2d1503-b816-40c9-9fac-7e03c5a3bcef",
    "explanation": "The supplied evidence includes a retrieved DailyMed label URL, so the answer inaccurately presents the source retrieval as unavailable."
  }
]
```

## E02-maternal-pk — plain

Fidelity: fail. Task fulfilled: False.

The response is well organized, separates the three requested axes, avoids dose values and individualized medication advice, and includes clinician questions. However, many substantive PK, placental-transfer, and outcome claims rely on citations absent from the supplied evidence pool. It also overstates the retrieved Clinical Considerations content by converting concentration observations into a commonly increased-clearance claim and does not clearly preserve the supplied study-specific registry context. Therefore fidelity fails and the task is not fully fulfilled under the source-linking criterion.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Lamotrigine clearance commonly increases during pregnancy",
    "reference_quote": null,
    "explanation": "The supplied evidence supports reports of decreased lamotrigine concentrations during pregnancy and restoration after delivery, but not the stronger assertion that clearance commonly increases or the claimed breadth across several studies."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Lamotrigine crosses the placenta.",
    "reference_quote": null,
    "explanation": "Placental transfer and cord-blood ratios are not reported in the supplied evidence pool, so this substantive exposure claim is unverified here."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Some analyses reported malformation rates near background rates",
    "reference_quote": null,
    "explanation": "The supplied label contains related registry findings, but the answer gives an unspecific summary attributed to unavailable sources and does not preserve the specific registry populations and designs in the evidence pool."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "other analyses explored possible associations with specific defects",
    "reference_quote": null,
    "explanation": "The answer does not identify the supplied registry context for the oral-cleft finding and instead relies on an unavailable label citation, leaving this substantive claim insufficiently source-faithful."
  },
  {
    "dimension": "task",
    "kind": "content",
    "requirement_quote": "Link PK claims to source label/abstracts and preserve study population and design.",
    "answer_quote": "The literature includes prospective observational cohorts, therapeutic-drug-monitoring studies, and pharmacokinetic analyses",
    "reference_quote": null,
    "explanation": "The answer lists study designs and populations but links them to citations outside the supplied evidence pool; the retrieved literature in the pool was mainly abstracts and reviews, and no such primary PK records were supplied."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Keep gaps visible",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer does not clearly state that the Clinical Considerations passage is labeling context rather than a quantified maternal pharmacokinetic study, despite that being a material limitation of the retrieved evidence."
  }
]
```

## R01 — plain

Fidelity: fail. Task fulfilled: False.

The answer cites the LactMed record, avoids administered doses, separates observations from a labeled advice section, and appropriately notes causal and evidentiary uncertainty. However, it incorrectly presents monitoring advice as a LactMed recommendation, omits the required numeric milk measurements, and does not disclose the bounded-record limitation.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "recommends monitoring the infant for possible effects",
    "reference_quote": "If no recommendation is retrieved, state that limitation instead of turning observations into advice.",
    "explanation": "The retrieved record reports symptoms and lists symptoms monitored in studies, but does not provide an explicit monitoring recommendation. The answer converts observations into advice and attributes that advice to LactMed."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Summarize actual retrieved infant observations separately from recommendations and milk measurements.",
    "answer_quote": null,
    "reference_quote": "Average milk levels were 0.69 mg/L (range 0.46 to 0.88 mg/L) at 4 hours and 0.81 mg/L (range 0.39 to 1.3 mg/L) at 5 hours after the dose.",
    "explanation": "The answer says milk concentrations were low but omits the retrieved milk concentration values and units, which the criteria specifically require to be reported separately from infant outcomes."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Cite the record and disclose missing/truncated evidence.",
    "answer_quote": null,
    "reference_quote": "This LactMed response is a bounded extract, not a complete record. Omitted sections or truncation can limit the summary; absence of retrieved findings is not evidence of safety.",
    "explanation": "Although the answer discusses limited information and missing infant specimens, it does not disclose that the retrieved material is a bounded, non-exhaustive extract or explicitly address the record's completeness limitation."
  }
]
```

## R03 — plain

Fidelity: fail. Task fulfilled: False.

The answer correctly distinguishes adult label warnings from infant observations and avoids administered doses. However, it attributes some adult-label claims to a different FDA label, omits the retrieved QPharma product limitation and quantitative exposure findings, and inaccurately characterizes the availability of infant serum measurements.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Compare metformin label warnings for the adult taking it with findings in breastfed infants.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer generally separates adult warnings from infant findings but does not report the retrieved infant serum findings or the specific observed infant outcomes in sufficient detail."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "name retrieved products and source limitations.",
    "answer_quote": null,
    "reference_quote": "METFORMIN HCL TABLET [QPHARMA, INC.]",
    "explanation": "The answer does not name the retrieved QPharma product or disclose the retrieved product and formulation limitation."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Source-linked explanation or honest missing evidence.",
    "answer_quote": null,
    "reference_quote": "Six women had milk levels that varied little over 24 hours and averaged 270 mcg/L.",
    "explanation": "The answer acknowledges measurements but omits the retrieved concentration values and their study context, leaving the requested findings materially incomplete."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "The U.S. label contains a boxed warning about metformin-associated lactic acidosis",
    "reference_quote": "Missing sections do not establish safety or absence of information elsewhere in the label.",
    "explanation": "The supplied retrieved label evidence does not establish that the selected product contains a boxed warning; the label extraction identifies limitations around missing sections. The claim is therefore unsupported for the retrieved product."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "The label warns that metformin may decrease vitamin-B12 concentrations",
    "reference_quote": null,
    "explanation": "No vitamin-B12 warning appears in the supplied retrieved label evidence, so this substantive label claim is unverified in the evidence pool."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "The label states that metformin generally does not cause hypoglycemia by itself",
    "reference_quote": null,
    "explanation": "That statement is not present in the supplied label excerpts and is therefore unverified in the evidence pool."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "The retrieved material did **not** establish a universal infant blood or serum concentration",
    "reference_quote": "Serum levels were measured in 4 breastfed infants",
    "explanation": "The evidence does not establish a universal concentration, but it does establish that infant serum concentrations were measured. The answer's wording incorrectly suggests that infant blood or serum concentration information was not established at all."
  }
]
```

## R04 — plain

Fidelity: fail. Task fulfilled: False.

The answer correctly explains that a nonmatch is not clearance and identifies several verification fields, but it does not fulfill the requested FDA-record lookup or report the returned candidates, statuses, and official links. Its explicit abstention is honest, but one product-use recommendation is unsupported in the evidence pool.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Search FDA recall records for naproxen.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer declines to perform or report the FDA lookup even though records were returned in the supplied evidence."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Candidate records and status only if returned; official links.",
    "answer_quote": null,
    "reference_quote": "D-0523-2026",
    "explanation": "Returned candidate records and their statuses were not reported, and no official links were provided."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Do not use the product until its status is verified",
    "reference_quote": null,
    "explanation": "The supplied evidence does not support this specific product-use recommendation; it cautions against inferring safety and says not to infer medication changes."
  }
]
```

## R06 — plain

Fidelity: not_assessable. Task fulfilled: False.

The response is an explicit and honest abstention, so it contains no assessable medical or study claims for source-fidelity comparison. It does not fulfill the requested recruiting-study lookup.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Find up to two recruiting ADHD studies involving children in the United States.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer honestly declines the lookup and supplies no study results."
  },
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Include exact study links, overall and site status if present, update dates, contacts and qualification limits.",
    "answer_quote": null,
    "reference_quote": null,
    "explanation": "The answer provides none of the requested study links, statuses, dates, contacts, or qualification limits."
  }
]
```

## R09 — plain

Fidelity: pass. Task fulfilled: False.

The abstention is honest and its statement that full notice text was not retrieved is consistent with the title-only search evidence. However, the response did not provide the returned notice title or link, so it did not fulfill the lookup-and-summary request.

```json
[
  {
    "dimension": "task",
    "kind": "omission",
    "requirement_quote": "Summarize only the returned notice titles or excerpts, link to them, and explain if full notice text was not retrieved.",
    "answer_quote": null,
    "reference_quote": "FDA requires Boxed Warning about serious mental health side effects for asthma and allergy drug montelukast (Singulair); advises restricting use for allergic rhinitis",
    "explanation": "The answer honestly disclosed that full notice text was not retrieved, but it omitted the returned FDA notice title and its direct link."
  }
]
```

## R06 — chat

Fidelity: fail. Task fulfilled: True.

The answer supplies two relevant recruiting studies with direct links, overall and site statuses where available, update dates, contacts, qualification limits, and appropriate cautions that it does not determine eligibility or site availability. It does not decide whether a child qualifies. Fidelity fails because it makes one unsupported-overstated claim about NCT05608434 involving established ADHD.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "The registry indicates this is an intervention for an established ADHD condition.",
    "reference_quote": "A condition keyword may describe an outcome or prevention topic rather than treatment of established disease. Review the summary and eligibility; do not imply the study is specifically for the requested condition from a keyword alone.",
    "explanation": "The answer overstates the registry evidence by characterizing the NCT05608434 study as an intervention for established ADHD. Its eligibility also permits a specified impairing inattention presentation that does not meet a full ADHD diagnosis, and the source expressly cautions against this inference."
  }
]
```

## R10 — chat

Fidelity: fail. Task fulfilled: True.

The answer provides the requested official FDA link, correctly explains that reporting alone does not establish causation, and states that no submission or identifying-data collection occurred. Its only source-fidelity issue is the additional unsupported wording about causation requiring further evaluation; the emergency-care characterization is source-supported but uncited.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "causation requires further evaluation",
    "reference_quote": "a report does not establish causation and is not emergency care.",
    "explanation": "The evidence supports that a report does not establish causation, but it does not expressly state that causation requires further evaluation."
  }
]
```

## R11 — chat

Fidelity: fail. Task fulfilled: True.

The answer correctly identifies the paper, states that the abstract was retrieved, distinguishes breast-milk and maternal exposure from infant outcomes, discloses unavailable infant age and prematurity information, and avoids claiming universal safety or causation. Its only source-fidelity issue is the unsupported characterization of the study as observational.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "an observational study of breastfeeding women with epilepsy",
    "reference_quote": "Women with epilepsy treated with levetiracetam were recruited to this study and completed a questionnaire.",
    "explanation": "The retrieved abstract describes recruitment, questionnaires, and measurements but does not explicitly characterize the study as observational. That design label is plausible but not actually stated in the supplied abstract."
  }
]
```

## R12 — chat

Fidelity: fail. Task fulfilled: True.

The answer correctly reports the queried 0-to-12-month age scope, retrieved reaction counts, and the limits that spontaneous-report counts do not establish incidence, risk, causation, or generalizability. It fulfills the requested task and cites the returned query, but includes several additional claims not established by the supplied evidence.

```json
[
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "Such reports can support **signal detection",
    "reference_quote": null,
    "explanation": "This interpretation is plausible but is not stated in the supplied retrieved evidence."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "each event was clinically confirmed or provide its timing or severity",
    "reference_quote": null,
    "explanation": "The supplied evidence describes reaction-term counts and their limitations but does not expressly establish these specific claims about confirmation, timing, or severity."
  },
  {
    "dimension": "fidelity",
    "kind": "content",
    "requirement_quote": null,
    "answer_quote": "cannot estimate incidence, prevalence, relative risk, or individual risk",
    "reference_quote": "Exposure denominators are absent; counts cannot estimate incidence or individual risk.",
    "explanation": "The source supports inability to estimate incidence and individual risk, but does not explicitly support the added claims about prevalence and relative risk."
  }
]
```

## Fixed-snapshot results

| Case | Expected | Actual | Exact match |
|---|---|---|---|
| B01 | 23.44 | 23.44 | True |
| B02 | Site 4 | Site 4 | True |
| B03 | 10.1007/s00737-018-0905-3 | 10.1007/s00737-018-0905-3 | True |
| B04 | 2 | 2 | True |
| B05 | 376 | 376 | True |
| B06 | Estradiol | Estradiol | True |
| B07 | 89.1 | 89.1 | True |
| B08 | 60 | 60 | True |
| B09 | 10.1016/j.ejogrb.2008.02.003 | 10.1055/s-0032-1323590 | False |
| B10 | 65.9 | 65.9 | True |
