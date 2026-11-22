# Current safety and evidence revision

**359/359 tests pass**, zero failures, errors or skips. Pinned Python 3.13 passes pip check. **25 tools, four prompts, four resources. No deployment or push.**

Six scripted chat probes completed. Five showed intended behavior: two evidence/preparation answers and three fixed stops. One English evidence request was overblocked. Crisis, identity and Spanish-question stops made zero downstream model and evidence calls. The false positive is retained as D05; a clearer clinician-question request succeeded as separate D06, not a replacement score. Initial probes remain in initial-probes/.

Seven direct protocol probes cover empty LactMed results, Spanish MedlinePlus, two-ingredient RxNorm identity, the evidence brief, Gold metadata, Silver classifications and inactive vector status. Empty results contain a dedicated absence field. Unit mocks verify every combination ingredient reaches each source; the live probe verifies identity, not a live combination-bundle benchmark.

No new model grading, clinician review or clinical certification. These are execution/contract examples, not accuracy rates. Routing and content flags are heuristic, some source text is truncated, labels may not match exact products, and MPRINT is a snapshot.

## Prior revision and grading limitations

The credential-recovery run used 301 tests and 27 tools. It completed 16 chats and five paired questions. Selection, boundaries and URL provenance were 16/16; diagnostic fidelity and task scores were 15/16. Raw paired task scores were MCP 5/5 versus plain 0/5. The grader penalized honest abstention, normalized a citation failure into a pass, compared unmatched labels and demanded non-truncation statements without retrieval. Four calibration controls did not expose all errors. Those scores are historical and establish no accuracy or speed advantage for this revision.

## Reproduction

Run server/run-local.ps1 -Test. capture-protocol.py requires a local server on port 18080. cases.json records synthetic chat prompts; the companion needs an existing authenticated model connection. report.py checks saved artifacts. summary.json and source-manifest.json retain counts and hashes. Historical raw traces remain unchanged; TOOL_MIGRATION.md maps old names. Ordinary parent chats are not saved by default.

The demo viewer and narrated recording replay new saved local results; they are not a live user interface or independent clinical review.
