# GSA template and requirements alignment

Reviewed November 21, 2026 against [GSA-TTS/mcp-hackathon-template](https://github.com/GSA-TTS/mcp-hackathon-template) commit `f39249f1768309e3ef8b31742390a4f3a656b5f3` and the [official event page](https://www.gsa.gov/super-intelligence/si-community-of-practice/events-and-training/mcp-server-and-si-agent-government-hackathon). The event requests a documented repository, presentation, and evaluation covering methodology, metrics, security, and lessons, for a sandbox prototype using public government data. The official page lists November 20, 2026 as the submission deadline; this repository audit does not establish an extension or submission acceptance.

The [sample evaluation DOCX](https://www.gsa.gov/system/files/MCP-hackathon-sample-evaluation-document.docx) is linked from the event page. The existing project DOCX follows its evaluation structure, with project-specific metrics and security analysis; its example CDC/Phoenix results are not reused. The template includes a Databricks/MLflow evaluation path as well as other backends. MLflow is an appropriate supported adaptation; Phoenix is not asserted to be mandatory.

| Requirement or template convention | Current implementation | Qualification |
|---|---|---|
| Root runnable project and locked dependencies | `pyproject.toml`, `uv.lock`, `main.py`, `.python-version`, `.env.example`, `QUICKSTART.md` | Python 3.13; local stdio default, optional loopback HTTP |
| Clear package and registration boundaries | `src/parent_child_pharmacology/{tools,services,clients,models,core,prompts,resources}` | One registrar per tool; domain implementations remain separate services |
| Discovery and operational routes | 31 tools, four prompts, four resources; `/health`, `/version`; `server.json` | Registry metadata only; no public endpoint or registry publication |
| Strict contracts and provenance | Bounded schemas, coverage/truncation metadata, source tags, required notices | Third-party clients must honor preflight and display rules |
| Outbound and credential security | HTTPS host allowlist, no redirects/proxy inheritance, 5 MB cap, token destination checks | DNS/IP pinning and per-tool remote auth tested; no cloud firewall or penetration-test claim; see `SECURITY.md` |
| Automated quality checks | Windows/Linux GitHub CI for lint, formatting, unit and grader tests, package build | CI has read-only repository permissions and no deploy step |
| Evaluation and no-tool baseline | Portable `eval/run.py`, frozen cases/hashes, fresh chat/paired captures and MLflow readbacks | Same-family diagnostic model grading; known cases, single trials, no clinical review |
| Databricks validation | Isolated serverless notebook runs the frozen source tests; existing model gateway and MLflow | The App itself is unchanged; job attempts and outcomes retained |
| Presentation and mission | Dataset Access Server; parents, clinicians, researchers, program staff; 15-slide main flow and appendix | Saved demo images/video are historical and labeled |
| Documentation and attribution | README, quickstart, security model, architecture, evaluation, deployment guidance, template MIT license | Existing repository aligned in place; no claim of recreated template ancestry |

The local package is .14; the existing Databricks App remains .9. GitHub publication is authorized to the existing **private** repository. No App deployment, access-policy change, public release or official submission is performed by this work. Current verified metrics live in [the current evaluation report](../evaluation/retrieval-reliability-final/REPORT.md); prior reports are historical evidence, not current status.

Remaining grading and readiness limits are deliberate disclosures: no clinician adjudication/certification, no held-out benchmark, no load/penetration test, source freshness and snapshot coverage limits, heuristic language/safety routing, and no production-readiness claim. The template scaffolding is not evidence that these limitations are resolved.


The [complete 65-file audit and remediation table](TEMPLATE_DETAILED_AUDIT.md) supersedes earlier broad alignment statements. The new Phoenix XML/CSV benchmark is implemented and run, with results and limitations reported separately; its explicit gateway loop and exact scoring adapt the LangChain/model-judge example. The historical .12 benchmark scored 3/10. See [current task-reliability evidence](../evaluation/retrieval-reliability-final/REPORT.md) for the repaired workflow, fresh results and limitations.
