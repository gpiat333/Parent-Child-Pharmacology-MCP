# Requested changes

| Items | Implemented | Review evidence |
|---|---|---|
| 1–3 | Fixed crisis/urgent referrals and conservative language stops | core/safety.py, core/language.py; route tests and three zero-call demos |
| 4 | Spanish MedlinePlus drug-code retrieval | spanish-education.json; free-form Spanish chat still stops |
| 5 | Renamed brief throughout current interfaces; raw old traces preserved | TOOL_MIGRATION.md and new traces |
| 6–7 | Explicit missing-evidence fields and dose-bearing source paths | core/evidence.py and response tests |
| 8 | Clinician questions in brief and dedicated MCP prompt | brief.json, D06 and prompts inventory |
| 9 | Scoped pregnancy coverage finding and payload notice | core/evidence.py; domain slide and DOCX |
| 10–12 | Removed letter categories, distinct age bands, FAERS caveats | content flags, population contracts and regression tests |
| 13 | Every normalized ingredient searched; no combination safety inference | RxNorm live identity plus mocked per-source fan-out tests |
| 14 | Two MPRINT tools with explicit table enum | inventory.json and two direct protocol probes |
| 15–16 | RePORTER staff oversight; public-input notices retained in appendix | main staff slide, appendix inventory |
| 17 | Inactive vector path returns not_enabled | inactive-vector.json |
| 18–21 | Boundaries, oversight, missing-data principle and pregnancy slides | 50-slide deck; 15 main |
| 22–26 | Cross-source links, white-pill stop, crisis stop, empty result and questions | current-demo viewer, video and unchanged source records |
| 27 | Limits spoken aloud | NARRATION.md, audible video and video-validation.json |

Clinical validation remains unperformed. The pregnancy finding is explicitly scoped; historical raw traces are not rewritten. One conservative false positive is retained. Nothing deployed.
