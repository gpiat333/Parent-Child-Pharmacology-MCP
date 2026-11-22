> Historical local demo from the prior .4 revision. The current .5 app includes the later routing fix. See [current validation](../../evaluation/brief-paraphrase-revision/REPORT.md).

# Current narrated demonstration

Computer-generated narration. Replay of current saved local results, not live chat. Nothing deployed.

## 00:00:00.000 — Measured exposure and observed outcomes

This is a replay of the current saved response. It separates measured milk and infant exposure from observed infant outcomes, with direct source links. The full answer also identifies missing and truncated sections, the selected manufacturer label, and uncertainty about study counts. LactMed covers lactation only.

Source: `evaluation/notice-citation-revision/chats/D01-cross-source-results.json`.

## 00:00:23.360 — Unconfirmed identity stops the request

The little white pill question stops for identity confirmation. Appearance is not enough to identify a medicine. This trace has zero downstream model calls and zero evidence calls.

Source: `evaluation/notice-citation-revision/chats/D02-identity-results.json`.

## 00:00:37.277 — A crisis cue stops the medication workflow

The postpartum crisis example stops the medication workflow and returns fixed support referrals. It performs no diagnosis or severity assessment. Research and participation are suppressed, and no model generates a clinical answer.

Source: `evaluation/notice-citation-revision/chats/D03-crisis-results.json`.

## 00:00:54.543 — Daridorexant pregnancy: evidence, gaps, participation

Daridorexant is the pre-tested gap example. The count-only tool reports source matches, with LactMed marked not applicable to pregnancy. These counts are different units, not a measure of study quality. The selected label reports limited human pregnancy data. Empty evidence rows remain visible. The registry appears separately with public contacts, unranked and not recommended. Missing data never means safe.

Source: `evaluation/notice-citation-revision/gap-brief.json`.

## 00:01:25.027 — Empty retrieval carries an explicit boundary

The synthetic no-match lookup returns machine-readable absence fields. No evidence retrieved is not evidence of safety. The model should preserve that distinction rather than turning a missing result into reassurance.

Source: `evaluation/notice-citation-revision/empty.json`.

## 00:01:39.949 — Questions prepare the clinician conversation

The brief returns questions to ask a clinician about the exact product, the relevant population, exposure versus outcomes, missing evidence and follow-up. These questions are authored by the prototype. They are preparation, not a medication plan.

Source: `evaluation/notice-citation-revision/gap-brief.json`.

## 00:01:58.760 — Clinical review must assess the impression an answer creates

Two safety risks need special emphasis. No reported effects can sound safe even when evidence is thin. Adverse findings can also prompt someone to stop a needed medicine. The payload preserves source context and includes a medication-change caution, and two cases examine framing. These are partial controls. A clinician must review real answers for reassurance and alarm that code checks cannot judge.

Source: `evaluation/notice-citation-revision/GRADER_CHANGE.md`.

## 00:02:27.414 — Execution evidence has a defined scope

The current source passes five hundred eight unit tests and exposes thirty tools. The client now renders required clinical review and activity code notices, and the URL checker separates adjacent citations. The evaluation compares seven paired questions on the same model, with retrieval tools only in the MCP arm. Automated grades are diagnostic. Routing and extraction remain heuristic, retrieval is bounded, and MPRINT uses snapshots. There is no clinician review, clinical certification or production readiness claim. New Spanish safety strings await human review. Nothing was deployed.

Source: `evaluation/notice-citation-revision/summary.json`.

Captions are aligned approximately within each narrated panel. The voice is Microsoft Zira Desktop. Runtime: 190.1 seconds. The plain comparison has no retrieval tools; diagnostic grades do not establish clinical accuracy.
