# English chat and Spanish patient education

This prototype supports **English research questions**. It does **not** support Spanish clinical chat. Selecting Spanish education does not turn off the language gate or translate the conversation.

| Request | Current behavior | Limitation |
|---|---|---|
| English evidence question | Preflight checks language, identity and safety before research | Language and safety detection are heuristic, not clinical triage |
| Spanish free-text question | Research is stopped; no downstream evidence retrieval or model-generated answer. The reply includes `message_es`, a reviewed Spanish message pointing to MotherToBaby (Spanish spoken), 988 in Spanish and MedlinePlus en español, and `disclaimer_es` | Spanish questions are still not answered; the Spanish message is fixed text, never generated |
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

## Spanish safety messages (policy .26)

Fifteen fixed Spanish safety and referral messages live in `messages_es` in [policy.json](../src/parent_child_pharmacology/core/policy.json). A native Spanish speaker (an NIH colleague) reviewed every message on November 23, 2026 and left 28 comments; all were applied. The wording was then aligned with the official Spanish used by MedlinePlus en español, the 988 Lifeline and Postpartum Support International, with Linguee for context. A second review round was not performed. The English and Spanish messages both speak as the service ("This service can't…" / "Este servicio no puede…").

When a question is in Spanish, the stop reply carries `message_es` and `disclaimer_es` alongside the English text. A crisis message written in Spanish gets the Spanish 988 message, plus the maternal mental health hotline and the PSI HelpLine in Spanish when it mentions pregnancy, birth or breastfeeding. All numbers were checked on the providers' own Spanish pages, except the maternal hotline's Spanish name and "press 2" option, which come from PSI's Spanish page because HRSA's site refused automated access.

What this is not: Spanish questions are still not answered, evidence is not translated, and crisis detection in Spanish recognizes only a few phrases. It must not be advertised as Spanish triage or bilingual crisis support. Clinical review of the Spanish phrasing and a second language review remain open.

## Implementation and evidence

- [Language gate](../src/parent_child_pharmacology/core/language.py) and [preflight routing](../src/parent_child_pharmacology/core/safety.py).
- [MedlinePlus adapter](../src/parent_child_pharmacology/clients/medlineplus.py) and [education service](../src/parent_child_pharmacology/services/labels_safety.py).
- [Spanish code-lookup and stop tests](../tests/test_safety_revision.py), [mixed-language regressions](../tests/test_task_reliability.py), and [Spanish message tests](../tests/test_spanish_messages.py).
- [MedlinePlus Connect documentation](https://medlineplus.gov/medlineplus-connect/web-service/).
