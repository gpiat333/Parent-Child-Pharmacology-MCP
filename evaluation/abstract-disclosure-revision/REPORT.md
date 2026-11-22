# Fresh local MCP evaluation: abstract disclosure and answer grounding

GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.

The prior version returned blank PubMed abstracts without an explicit coverage contract; its composite brief dropped the abstract-fetch wrapper. The local .10 version returns PMID-level coverage, distinguishes missing text, unreturned records and request failures, and preserves it through combination-product briefs. Both companion clients append the required disclosure from validated structured coverage, even when the model omits it. A later successful refetch updates the disclosure. Policy and identity stops still suppress downstream retrieval and notices. Arbitrary third-party clients must honor the payload contract themselves.

General response instructions now retain returned recall candidates and statuses, keep separate studies and comparator medicines separate, preserve unspecified infant specimens, and avoid unsupported methodological additions. These were development changes motivated by prior failures, not changes to the evaluation cases or grader.

## Verified results

| Measure | Current result | Scope |

|---|---:|---|

| Server unit tests | 592 passed | Local final source; zero failures, errors or skips |

| Grader unit tests | 30 passed | Unchanged grader v3; separate suite |

| Synthetic development controls | 10/10 fidelity, 10/10 task | Not held-out or clinical validation |

| Fresh chats completed | 28/28 | 21 research + seven fixed stops |

| Routes / tool selection | 28/28 / 28/28 | Deterministic execution checks |

| Fixed stops | 7/7 | No downstream evidence or model calls |

| URL membership | 21/21 | Membership is not claim support |

| Research fidelity | 21 pass / 0 fail / 0 N/A | Model judgment against bounded retrieved pool |

| Research tasks fulfilled | 21/21 | Separate requested-output completeness |

| MLflow rows verified | 42/42 | 21 research + seven stops + 14 paired; zero scorer errors |

| MCP Inspector | 9/9 checks | Local protocol and tool checks; not clinical validation |

## Fresh paired comparison

| Measure | MCP | Plain model |

|---|---:|---|

| Completed answers | 7/7 | 7/7 |

| Tasks fulfilled | 5/7 | 0/7 |

| Fidelity pass / fail / N/A | 6 / 1 / 0 | 1 / 6 / 0 |

Both arms use the same model and shared application instructions, with newly retrieved reference pools. Retrieval uses the normal source clients, including their caches and dated snapshots; fresh tool calls do not imply that every upstream record is newly updated. Only MCP receives tools, enforced routing and application notices. The main chat companion also has an extra source-review pass that the paired runner does not use. A shared pool can contain evidence the plain answer never received. Honest abstention can leave a requested lookup incomplete. This is a workflow comparison, not proof of superior intrinsic model ability, clinical accuracy or speed.

## Grading limits and historical comparison

The previous .9 captures, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The new scores come from fresh .10 answers and live references. Cases and grader core are byte-identical, but prompts, application code, live sources and model outputs can differ. This is not a controlled causal estimate of the code change. Older results remain historical, including .5 research tasks 18/21 and paired MCP 5/7.

The unchanged grader v3 accepted 35 grades in 41 model attempts (6 structural correction attempts). It validates answer quotations for negative content claims, anchors omissions to requested requirements, and binds citation IDs to original answer URLs. It retains the first structurally valid grade, including failures. No manual score overrides occurred. Literal quotation checks do not establish semantic correctness, clinical importance or safety. The ten synthetic controls are known development cases.

Fidelity asks whether factual claims are supported by the captured pool. Task fulfillment asks whether the requested work was completed. These measures are separate. Unverified in a bounded pool does not prove medically false; N/A means no assessable source claims and is excluded from fidelity rates. The same-family judge is fallible. One answer per known development case and no independent clinician review limit all results.

## Targeted cases

**E01-gap / chat: fidelity pass; task fulfilled True.** The answer presents all three requested evidence axes with visible empty rows, separates animal findings and spontaneous-report context from human evidence, states the maternal PK retrieval gap within the retrieved scope, preserves absent-abstract information, cites the label and FDA directory, lists registry contacts separately without ranking or recommending participation, and provides no administered doses or medication decisions.

**E01-gap / mcp: fidelity pass; task fulfilled True.** The answer visibly presents all three requested evidence axes, preserves empty human rows, distinguishes animal findings and spontaneous reports from human outcomes, states the retrieved maternal PK gap within the bounded search scope, provides label and directory citations, separates registry contact information without recommending participation, and avoids administered doses or medication decisions.

**R04 / chat: fidelity pass; task fulfilled True.** The answer correctly reports the bounded search result, avoids treating the missing fictional lot as clearance or proof of safety, preserves product/manufacturer/lot/status distinctions, lists returned records and statuses with official links, and explains the additional verification needed. One ancillary source-derived statement about treatment changes is not separately cited, but this does not prevent task fulfillment or constitute a substantive fidelity failure.

**R12 / chat: fidelity pass; task fulfilled True.** The answer states the queried age scope exactly, reports retrieved terms and counts without presenting them as incidence, explains that causation and generalization cannot be established, and cites the returned query and relevant source material. It also preserves the metadata warning that applicability of individual terms was not established.

**R01 / mcp: fidelity pass; task fulfilled False.** The answer accurately separates milk measurements, observed infant symptoms, and symptoms that were only monitored in a study. It avoids administered doses and appropriately explains causality and evidence uncertainty. The sole task deficiency is failure to disclose the record-level completeness limitation.

## Remaining negative grades

- R01 / mcp: fidelity pass, task False. The answer accurately separates milk measurements, observed infant symptoms, and symptoms that were only monitored in a study. It avoids administered doses and appropriately explains causality and evidence uncertainty. The sole task deficiency is failure to disclose the record-level completeness limitation.

- R03 / mcp: fidelity fail, task True. The answer largely fulfills the comparison, separates adult label warnings from infant observations and exposure measurements, identifies the retrieved products and sources, discloses missing sections, and avoids administered doses. Its main fidelity defect is treating surgery and contrast studies as increased-risk settings rather than reporting the label's separate temporary-discontinuation precaution.

- R06 / mcp: fidelity pass, task False. The answer accurately reports the two retrieved recruiting studies, direct links, overall and site statuses, update dates, age limits, contacts, qualification-limit summaries, and the non-determination of eligibility. It does not fully satisfy the contact-information requirement because it omits supplied contact extensions for the APG site.

- R01 / plain: fidelity fail, task False. The answer appropriately separates headings, reports several observed symptoms, conveys uncertainty, avoids dosing, and notes the absence of infant-level concentration data. However, it omits the required numeric milk concentrations, misidentifies a comparison-study exposure group, and incorrectly attributes a monitoring recommendation to LactMed. Several additional explanations about maternal illness, other exposures, and ordinary infant symptoms are plausible but not established in the supplied record.

- R03 / plain: fidelity fail, task False. The answer generally separates adult adverse effects from infant observations and avoids administered doses, but it misattributes LactMed findings to the label, includes unsupported label assertions, fails to name the retrieved QPharma product, and does not disclose the specifically missing label sections. Its DailyMed citation is incomplete.

- R04 / plain: fidelity fail, task False. The answer correctly explains that a lot nonmatch is not clearance and lists appropriate identity fields and verification sources. It is an honest abstention, but it does not complete the requested FDA-record lookup by reporting the records and statuses that were returned, and one broader coverage claim is not directly supported by the supplied evidence.

- R06 / plain: fidelity pass, task False. The response is an honest abstention and does not materially contradict the evidence. Its cautions about site-level recruitment, individual qualification, and treatment changes are supported or appropriately framed, but it does not fulfill the requested lookup.

- R09 / plain: fidelity fail, task False. The answer correctly disclosed that full notice text was not retrieved and cautioned that an empty result would not prove the absence of safety communications. However, it incorrectly reported no returned records and omitted the returned notice title and its specific link.

- E01-gap / plain: fidelity fail, task False. The answer presents all three axes, states a pregnancy PK gap, keeps registry information separate, and avoids individualized dosing. However, it misstates animal findings, asserts unsupported animal transfer and developmental outcomes, and gives the wrong registry and contacts. Its citations are not verifiable within the supplied reference pool and it omits the required FDA directory citation.

- E02-maternal-pk / plain: fidelity fail, task False. The answer is well organized, separates the three axes, avoids administered dose numbers and personal medication advice, and includes clinician questions. However, its central pharmacokinetic and fetal-exposure claims rely on citations and study findings not contained in the supplied evidence. It also fails to clearly distinguish the label's Clinical Considerations from literature evidence and does not preserve the retrieved study population and design. Therefore fidelity and full task completion fail.

## Technical review of grader limitations

**R01 / mcp:** The grader demands a generic whole-record completeness notice even though all four expected sections were returned without truncation. The answer discloses missing infant-level information. This is a strict disclosure judgment; it is not evidence that the retrieved outcome section was missing or that the answer invented outcomes.

**R06 / mcp:** The grader incorrectly says the answer contains the APG main phone but omits its extensions. The answer instead lists central contacts and an explicitly selected subset of site contacts; the APG phone is absent entirely. Whether every site contact is required by the broad contacts criterion is a scope judgment. The score is retained unchanged, and the rationale is flagged for human review.

**R03 / mcp:** The grader flags combining procedural precautions with explicit risk-factor statements in one sentence. The exact sentence appears in the answer; clinical significance and the broader label interpretation have not been independently adjudicated.

The numerical grades remain unchanged. The audit demonstrates why the model grader is not an authoritative human assessment: a structurally valid rationale can still misdescribe a candidate or apply a broad requirement too strictly. See [technical-grade-audit.json](technical-grade-audit.json).

## MLflow recording repair

All 14 paired rows re-logged from the same fingerprint-validated grades; no new answers or judge calls. Initial attempt retained, excluded from final 42-row count. The initial run created 14 traces but returned only 13 scored result-table rows; the readback caught that mismatch. It is a tracking failure, not an extra model-performance sample.

## Where work ran

Application changes are in the submission folder’s `server` and `chat-client`; this revision’s evidence is in `evaluation/abstract-disclosure-revision`. The MCP ran on local loopback. Unit tests, MCP Inspector, answer drivers and offline evaluation orchestration ran locally. Model calls, grading model calls and MLflow tracking used existing Databricks services. These were not remote notebook unit tests. The deployed app remains policy .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. No deployment, infrastructure or permission change, GitHub upload or official submission occurred.

The [MLflow parent run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a05a172e30e8447ab5dd6adaea0236f5) records the fresh evaluation and updated artifacts. Every one of the 42 saved evaluation rows was read back. Full tool traces are retained in artifacts; offline grading creates a root evaluation span per row. See [summary.json](summary.json), [source-changes.diff](source-changes.diff), [capture-lineage.json](capture-lineage.json), [run-design.json](run-design.json), and [grading-review.json](grading-review.json). Saved .4 demo screenshots and video remain historical; no new demonstration video was generated.
