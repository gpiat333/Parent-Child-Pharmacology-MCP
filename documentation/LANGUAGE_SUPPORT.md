# English chat and Spanish patient education

This prototype supports **English research questions**. It does **not** support Spanish clinical chat. Selecting Spanish education does not turn off the language gate or translate the conversation.

| Request | Current behavior | Limitation |
|---|---|---|
| English evidence question | Preflight checks language, identity and safety before research | Language and safety detection are heuristic, not clinical triage |
| Spanish free-text question | Research is stopped; no downstream evidence retrieval or model-generated answer | The fixed response is currently in English, so it may not be accessible to a Spanish-only user |
| Mixed-language or uncertain-language question | Conservative stop when the language gate detects uncertainty or non-English segments | Detection can still miss some mixtures or incorrectly block technical English |
| English request for Spanish MedlinePlus education | `get_patient_education` can request source-authored Spanish content with `language="es"` and a confirmed RxCUI | This is a drug-code lookup, not Spanish free-text search, translation or a personalized answer |
| Spanish request without a confirmed drug code | No Spanish topic-search fallback; returns `spanish_requires_rxcui` when the permitted tool request lacks the code | A medicine's appearance or a vague name is insufficient |
| Spanish labels, LactMed summaries or abstracts | No translation feature is enabled | English evidence is not machine-translated and presented as reviewed Spanish medical guidance |

## How the supported education path works

1. Preflight the actual user question in English. Stop on urgent, crisis, identity-unconfirmed or any other blocked route.
2. Resolve the exact medicine using `normalize_drug`. Confirm uncertain matches and preserve combination ingredients. Do not guess a code.
3. Call `get_patient_education` with an English `topic`, the confirmed `rxcui` and `language="es"`.
4. Present the returned MedlinePlus title, summary and original source link as source-authored education. A missing Spanish match stays missing; an English match does not prove a Spanish counterpart exists.

Illustrative arguments (replace the placeholder with the confirmed code; this is not an executable example):

```json
{
  "topic": "What information is available in Spanish for this confirmed medicine?",
  "rxcui": "<confirmed RxCUI>",
  "language": "es"
}
```

Structured identifiers are data, not a substitute for preflighting the full question. A third-party client must enforce the same stop behavior; passing a drug code to a stateless tool cannot convey omitted conversational context.

## What is awaiting review

New Spanish safety/referral messages were deliberately held under build item 48 pending human Spanish-language review. There is no completed review or approved Spanish safety-message set in this submission. Some existing crisis cue matching recognizes limited Spanish phrases, but that does not establish comprehensive Spanish crisis detection. It must never be advertised as Spanish triage or bilingual crisis support.

Before enabling Spanish chat or new Spanish safety messages, the project needs a qualified Spanish-language reviewer, clinical review of safety/referral phrasing and interpretation, approved messages with recorded reviewer/date/version, and tests covering ordinary questions, ambiguity, mixed language, urgent/crisis statements, identity uncertainty and all downstream stops. Referral destinations and language availability must be verified for the intended country. Passing the current English tests is insufficient.

These are development and review prerequisites, not something that becomes supported by deploying the current package. The current English stop text is an accessibility limitation that remains unresolved while review is pending.

## Implementation and evidence

- [Language gate](../src/parent_child_pharmacology/core/language.py) and [preflight routing](../src/parent_child_pharmacology/core/safety.py).
- [MedlinePlus adapter](../src/parent_child_pharmacology/clients/medlineplus.py) and [education service](../src/parent_child_pharmacology/services/labels_safety.py).
- [Spanish code-lookup and stop tests](../tests/test_safety_revision.py), [mixed-language regressions](../tests/test_task_reliability.py), and [human-review hold](PROGRAM_AND_SAFETY_REVISION.md).
- [MedlinePlus Connect documentation](https://medlineplus.gov/medlineplus-connect/web-service/).
