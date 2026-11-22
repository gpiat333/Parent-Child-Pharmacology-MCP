# Current narrated demonstration

Computer-generated narration. Replay of current saved local results, not live chat. Nothing deployed.

## 00:00:00.000 — Exposure and outcomes remain distinct

This is a replay of a response from the updated local server. The answer separates measured milk exposure from observed infant outcomes and links to LactMed and the selected label. LactMed covers lactation only. These are complete excerpts; the full answer and its limitations remain available.

Source: `evaluation/evidence-revision/chats/D01-cross-source-results.json`.

## 00:00:20.555 — An unidentified pill stops before retrieval

The little white pill question stops for exact medicine identity. The current trace contains zero downstream model calls and zero evidence calls. No participation information appears, and appearance is not used to guess the medicine.

Source: `evaluation/evidence-revision/chats/D02-identity-results.json`.

## 00:00:37.462 — Crisis cues stop research and participation

A postpartum crisis cue stops the medication workflow and its participation tier. The response supplies fixed support referrals, including a clearly identified non-emergency postpartum callback service. It does not diagnose, assess severity, or ask the model to create a clinical answer.

Source: `evaluation/evidence-revision/chats/D03-crisis-results.json`.

## 00:00:58.932 — Daridorexant: evidence, gap and participation

Daridorexant was pre-tested for this gap example. The label reports a human pregnancy-data limitation, and animal findings remain separate. All three rows stay visible. The targeted maternal pharmacokinetic search returned no records, and the general records lacked abstracts. Spontaneous adverse-event reports remain separate signals, not proof of causation. The FDA directory provides a registry and contacts in a separate participation tier. It is unranked, not recommended, and not an eligibility decision. Empty rows describe this bounded label and abstract extraction, not the absence of all human reports.

Source: `evaluation/evidence-revision/pretest-daridorexant.json`.

## 00:01:43.134 — Clinical Considerations and maternal PK

Lamotrigine provides the contrasting example. The parser separates Risk Summary, Clinical Considerations and Data. The maternal dose-adjustment field preserves source labeling, while the pharmacokinetic field also draws on retrieved abstracts. Clinical Considerations is not automatically pharmacokinetic evidence. No individualized dose is calculated or recommended.

Source: `evaluation/evidence-revision/pretest-lamotrigine.json`.

## 00:02:09.659 — An empty result is not evidence of safety

A deliberately synthetic no-match query returns explicit absence-of-evidence fields. The payload states no evidence retrieved and not evidence of safety. The fields remain present when results are empty.

Source: `evaluation/evidence-revision/empty.json`.

## 00:02:24.290 — Prepare questions for a clinician

The brief ends with questions to ask a clinician about the exact product, population match, exposure versus outcomes, missing evidence and follow-up. These are preparation questions authored by this implementation. They do not prescribe a treatment plan.

Source: `evaluation/evidence-revision/pretest-daridorexant.json`.

## 00:02:43.051 — What the current evaluation establishes

The current version passes three hundred ninety-five unit tests. The original English false positive is fixed in the rerun. The paired comparison uses seven questions and the same model, but the plain arm has no retrieval tools. Automated grades are diagnostic, not clinical accuracy. Routing and extraction remain heuristic. Retrieval is bounded, and MPRINT uses snapshots. There is no clinician review or clinical certification. This tool surfaces evidence gaps rather than closing them. Nothing was deployed.

Source: `evaluation/evidence-revision/summary.json`.

Captions are aligned approximately within each narrated panel. The voice is Microsoft Zira Desktop. Runtime: 200.7 seconds. The plain comparison has no retrieval tools; diagnostic grades do not establish clinical accuracy.
