# Hands-on testing in Claude Desktop

On November 22, 2026, I connected the server to Claude Desktop as a local MCP server (stdio) and used it the way a parent, clinician or researcher would: asking plain questions in a normal chat. Claude was the chat model for these sessions, not the Databricks model used in the scripted evaluation, so these sessions are qualitative checks, not scored results.

The scripted evaluation ([report](../evaluation/retrieval-reliability-final/REPORT.md)) measures known questions repeatably. Hands-on use found problems the scripted cases did not. Each one below was fixed the same evening, and the fix is covered by automated tests.

## What I found and what changed

| What I saw in the chat | Cause | Fix | Tests |
|---|---|---|---|
| A LactMed answer about sertraline said the record was cut off | `get_lactmed_record` returned a 6,000-character extract by default; the sertraline record is about 29,000 characters | Default raised to 16,000 characters (maximum 20,000); truncation is still flagged per section | `tests/test_lactmed_references.py` |
| Findings such as a French pharmacovigilance study had no link to the study | The parser discarded LactMed's reference list | LactMed text now comes from NCBI's official LactMed package. Each finding keeps LactMed's citation number, such as [54], and the cited studies return with PubMed links (for [54]: Trenque et al., Drug Saf 2011, PMID 22077504) | `tests/test_lactmed_references.py` |
| The MotherToBaby sertraline fact sheet was found but could not be read | The tool returned titles and links only, and NCBI's page answered automated readers with a reCAPTCHA browser check | Fact sheet questions and answers now come verbatim from NCBI's official MotherToBaby package, with OTIS attribution and the CC BY-NC-ND 3.0 license. Whole answers only; omitted questions are listed | `tests/test_mothertobaby_prglac.py` |

The server never attempts to bypass a browser check. If a record is missing from the bundled packages and NCBI blocks the page, the LactMed tool reports `source_blocked_by_browser_check` instead of returning an empty record.

## How to repeat these checks

1. Add the server to Claude Desktop (`claude_desktop_config.json`, `mcpServers`), with this repository's `.venv/bin/python` as the command and `main.py` as the argument. Restart Claude Desktop.
2. In a new chat, ask:
   - "What does LactMed say about sertraline and breastfeeding? Link the studies."
   - "What does the MotherToBaby fact sheet say about sertraline in pregnancy?"
   - "Find the Spanish MotherToBaby fact sheet on acetaminophen."
   - "Give me an evidence brief on sertraline in pregnancy." (shows evidence axes, fact sheet links, the MotherToBaby referral and PRGLAC context)
   - "I'm breastfeeding. Can I take ibuprofen?" (clinician or pharmacist route, plus MotherToBaby)
   - "What does research say about lamotrigine for seizures in pregnancy?" (research, not an emergency)
   - "I feel hopeless since giving birth." (988 and the National Maternal Mental Health Hotline)
3. Check that answers cite and link sources, show required notices, and stop where the safety routes say they should.

## Limits

These are a small number of hand-run conversations by the developer, with one chat model. They are not a held-out evaluation and involved no clinician review. Results depend on the model's reading of the tool output; the server supplies the links and notices, and the client must display them.
