# Parent-child Pharmacology MCP

**GSA MCP & SI Agent Government Hackathon · Track: Dataset Access Server**

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

[![Slide 1 of the deck. Click to page through all 42 slides.](presentation/slides/img/slide-01.png)](presentation/slides/slide-02.md)

**[▶ Click through the slide deck (42 slides)](presentation/slides/slide-01.md)**: click the slide above, then keep clicking each slide to move to the next.

**[Watch the demo video (8:49)](presentation/Parent-child%20Pharmacology%20MCP%20-%20Demo%20video.mp4)** · [Deck as PDF](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Hackathon%20deck%20v34.pdf) · [Deck as PowerPoint](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Hackathon%20deck%20v34.pptx) · [Evaluation document](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.pdf)

Pediatric and maternal medication information is spread across product labels, lactation records, publications, trial registries and research datasets—and it is divided twice over. Once by population: evidence about a fetus, a breastfed infant and a six-year-old belongs to different literatures, and “pediatric” alone spans a preterm neonate to an adolescent. Once again by purpose: what the drug is, what the label says, what published studies found, what is being studied now, and what outcomes were actually measured each live somewhere different.

Naming sits on top of both. A parent knows a brand name, a label uses the ingredient, a paper uses the generic, and a dataset keys on a PMID or an RxCUI. Before anyone can search, they have to work out which population they are asking about, which kind of resource answers that question, and what the medicine is even called.

A parent preparing for a clinician visit, a clinician reviewing source evidence, a researcher scoping what has already been studied, and a program officer reviewing a portfolio each need a different view of that evidence—and each needs to see what is missing. This MCP server gives AI clients structured, cited access to those sources through one interface.

### How it answers

After preflight permits research, the workflow addresses the three problems: resolve the drug name, flagging uncertain matches instead of guessing; preserve the requested population and age band in population-aware searches and the composite brief; then use the resource that answers the question. A source match alone does not establish that a finding applies to the requested population.

The evidence brief separates three things that are easily conflated: effects on the pregnant or lactating person, measured fetal or infant exposure, and observed fetal or infant outcomes. Empty rows stay visible. **Missing data never means safe.** Where retrieved evidence runs out, the server makes that gap explicit. A separate participation lookup can surface registries and recruiting studies, without implying that participation is appropriate or that a listed study will resolve the gap.

### What it connects

The sources divide along the same lines as the problem. RxNorm helps resolve medicine names and ingredients. DailyMed supplies in-use product labeling, which may differ from the latest FDA-approved version, and an FDA dataset tracks pediatric labeling changes over time. [LactMed, NLM’s peer-reviewed lactation database](https://www.ncbi.nlm.nih.gov/books/NBK501922/), covers drug and chemical levels in breast milk and infant blood and reported effects in breastfed infants. It is a lactation resource, not a pregnancy database.

PubMed and ClinicalTrials.gov cover what has been published and what is being studied. openFDA carries adverse-event reports and recalls, MedlinePlus provides patient education, and NIH RePORTER shows what is funded and by which institute. NICHD-supported resources—BPCA and Pediatric Trials Network study summaries, MPRINT Gold and Silver, and public study metadata from the Data and Specimen Hub (DASH)—support pediatric therapeutics and study discovery. DASH discovery does not provide controlled participant-level data.

Public source adapters query online sources, subject to caching, availability and bounded retrieval. The MPRINT tables are versioned published snapshots carried with the server. Source dates, coverage limits and configured data paths are described in the [source coverage](#data-sources-and-tool-coverage) and [architecture](documentation/ARCHITECTURE.md) sections.

### Why the gaps matter

Important evidence gaps remain for pregnant people, lactating people and children. NICHD identifies therapeutics development for these populations as lagging behind that for adults outside pregnancy. Federal efforts including BPCA and PREA for pediatrics, the PRGLAC recommendations for pregnancy and lactation, MPRINT and the Pediatric Trials Network address these gaps; their existence does not mean the gaps are closed. [NICHD research priorities](https://www.nichd.nih.gov/about/advisory/council/202610/Concept_Review_by_Council/Maternal_Pediatric_Pharmacology_Therapeutics) · [PRGLAC recommendations](https://www.nichd.nih.gov/about/advisory/PRGLAC/recommendations).

For a given medicine, this server makes the shape of what remains visible: what has been published, what is currently under study, and where the sources return nothing at all. Trial and registry records are presented as information only—listed, never ranked, recommended, or encouraged. Absence is reported as absence *in the retrieved sources*, not as proof that no evidence exists anywhere.

### Safety and boundaries

A companion chat client is included. Its heuristic preflight checks are designed to stop urgent/crisis, identity-unconfirmed and personal treatment-advice requests before downstream evidence retrieval or model answering. Permitted requests return evidence, its limitations, and questions to bring to a clinician. Other clients must enforce the same preflight and display contracts; MCP registration alone does not guarantee that behavior.

The workflow must not provide personal dosing or medication-change advice, determine eligibility, perform clinical triage, or make clinical decisions. Retrieved source passages can contain dosing or administration information; those fields are flagged for client handling rather than guaranteed absent. This is user-guided evidence discovery and clinician preparation, not an independent clinical decision-maker. [Safety controls and remaining risks](#safety-and-security).

### At a glance

**21 tools, 4 prompts and 5 resources** spanning drug identity, lactation and pregnancy evidence, literature and trials, labeling and safety signals, NICHD research data, and study participation.

**1,051 automated tests pass** on Linux, Windows and Databricks, plus 33 tests of the grader. The full evaluation was re-run in **23 rounds** as the server changed, each with 27 or 28 fresh chats, and every round is kept in [evaluation/](evaluation/). On the final version: 27 of 27 chats completed, 7 of 7 safety stops held, 20 of 20 research answers stayed faithful to their sources, 7 of 7 paired tasks were done with the MCP against 0 of 7 without it, and 10 of 10 benchmark answers were exact. [Results](#results-at-a-glance).

---

*Prototype built for the GSA MCP Hackathon by Gabriela Piatkowski, MS; Program Analyst, Obstetric and Pediatric Pharmacology and Therapeutics Branch, NICHD. Not an official NIH product, service or endorsement. No production-readiness claim. Views are the author’s.*

**Start here:** [Demo video](#demo-video) · [Screenshots](#screenshots) · [For judges](#for-judges) · [Results](#results-at-a-glance) · [Run locally](#run-it-yourself)

| Submission material | Open it |
|---|---|
| Presentation | [Click-through deck](presentation/slides/slide-01.md) · [PowerPoint: 38 main slides and 4 appendix slides](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Hackathon%20deck%20v34.pptx) · [PDF](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Hackathon%20deck%20v34.pdf) |
| Evaluation | [GSA evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx) · [PDF](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.pdf) · [readable report](evaluation/v0222-final/REPORT.md) |
| Demonstration | [8:49 demo video, narrated by the author](presentation/Parent-child%20Pharmacology%20MCP%20-%20Demo%20video.mp4) · [recording slides](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Demo%20slides.pptx) |
| Evidence | [Chat scores](evaluation/v0222-final/chat-summary.json) · [benchmark scores](evaluation/v0222-final/benchmark/summary.json) · [MLflow receipts](evaluation/v0222-final/mlflow/) · [Databricks test receipt](evaluation/databricks-validation-2026-11-23-v0222/databricks-job-output.json) · [all captures and judgments](evaluation/v0222-final/) |
| Implementation | [Quickstart](QUICKSTART.md) · [architecture](documentation/ARCHITECTURE.md) · [security](SECURITY.md) · [template alignment](documentation/GSA_REQUIREMENTS_REVIEW.md) |

**Version and access:** the current source is **0.22.2**, policy **2026-11-23.29**, with 21 tools. It is the version the scores below describe, it passes all 1,051 tests on Linux and Windows CI and in a Databricks serverless run, and it is the version running on the Databricks App `mcp-mc` (deployment 01f1e7a50b1c1872be5159c39a70aff2, November 23, 2026), with Databricks workspace sign-in as its access control; see [deployment status](documentation/DEPLOYMENT_STATUS.md). Workspace access is required for Databricks links below. What changed in each version and policy is in the [change history](CHANGELOG.md) and the [tool migration notes](documentation/TOOL_MIGRATION.md).

The [complete 65-file template audit and remediation table](documentation/TEMPLATE_DETAILED_AUDIT.md) records implemented controls, deliberate adaptations, and deployment prerequisites still outstanding.

## For judges

| Criterion | Where to look | What to assess |
|---|---|---|
| Mission alignment | [Users and mission](#users-and-mission) · [architecture](documentation/ARCHITECTURE.md) | Evidence discovery for parents, clinicians, researchers and NICHD program staff; visible population and evidence gaps |
| Technical quality: maintainability | [Package](src/parent_child_pharmacology/) · [tool registrars](src/parent_child_pharmacology/tools/) | Separate schemas, source clients and domain services; thin entry point; one registrar per tool |
| Technical quality: performance and reliability | [Evaluation report](evaluation/v0222-final/REPORT.md) · [tests](tests/) · [Databricks test receipt](evaluation/databricks-validation-2026-11-23-v0222/databricks-job-output.json) | Inputs, attempts, error handling, fresh captures and measured results; operational timings are observations, not a speed claim |
| Technical quality: MCP design | [Tool catalog](src/parent_child_pharmacology/tools/__init__.py) · [models](src/parent_child_pharmacology/models/) · [Inspector results from the earlier .14 build](evaluation/retrieval-reliability-final/inspector/summary.json) | Bounded inputs, goal-oriented tools, structured provenance and explicit absence-of-evidence contracts |
| Innovation | [Workflow](#how-it-works) · [evidence-axis tests](tests/test_evidence_axes.py) | Separate maternal effects, transfer/exposure and infant outcomes, with clinician questions and a distinct participation tier |
| Presentation | [Video](#demo-video) · [screenshots](#screenshots) · [deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Hackathon%20deck%20v34.pptx) | Author-narrated walk-through: the problem, the design, a live demo, a cited answer, safety stops, a Spanish reply and the results |

## Users and mission

The intended mission contribution is to support pregnancy, lactation, child-health and pediatric-pharmacology evidence discovery relevant to NICHD. This does not establish NIH sponsorship or endorsement.

| User | Example use | Boundary |
|---|---|---|
| Parents and caregivers | Prepare clinician questions using an exact medication name and linked evidence | No personal treatment, dose or medication-change recommendation |
| Clinicians | Inspect the label, lactation record and literature behind a generated summary | Discovery aid; no substitute for clinical judgment or comprehensive review |
| Researchers | Find studies, missing abstracts, thin coverage and separate participation information | Source counts are not evidence-quality scores |
| NICHD program staff | Search funded research by institute, fiscal year and topic; inspect portfolio coverage | Public RePORTER evidence for oversight, not a complete internal grants record |

## Demo video

[**Watch or download the demo video (8:49, MP4), narrated by the author**](presentation/Parent-child%20Pharmacology%20MCP%20-%20Demo%20video.mp4)

This is the submission video, recorded November 23, 2026 over the [recording slides](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Demo%20slides.pptx) for version 0.22.2. The file was re-encoded on November 24, 2026 so the picture and narration stay in sync in every player; the recording itself is unchanged.

## Screenshots

### Real answers from the live server

These three answers were captured on November 23, 2026 from the deployed Databricks App (version 0.22.2) through the companion chat client. Each image shows the question, the tools the model called, and the answer as returned; long answers are excerpted, and the full text is linked under each.

**A cited LactMed answer.** Milk levels and infant measurements, each with its study link.

![Real answer: sertraline during breastfeeding from LactMed, with milk concentrations and study links](presentation/screenshots/answers/lactmed-sertraline.png)

[Full answer text](presentation/screenshots/answers/lactmed-sertraline.md)

**An evidence brief in three rows.** Effects on the pregnant person, fetal or infant exposure, and fetal or neonatal outcomes stay separate, and missing label sections are stated.

![Real answer: evidence brief for sertraline during pregnancy in three separate rows](presentation/screenshots/answers/pregnancy-brief.png)

[Full answer text](presentation/screenshots/answers/pregnancy-brief.md)

**A safety stop.** A personal stop-my-medicine question gets a fixed reply and no search or model answer.

![Real reply: the service declines a personal medication decision and gives clinician and MotherToBaby contacts](presentation/screenshots/answers/safety-stop.png)

[Full reply text](presentation/screenshots/answers/safety-stop.md)

### From the deck

These are slides from the recording deck for version 0.22.2.

| One server, three populations | Safety check before any source |
|---|---|
| ![One MCP server connects pregnancy, breastfeeding and pediatric data](presentation/screenshots/one-server.png) | ![Architecture: a safety check runs before any federal source is called](presentation/screenshots/architecture.png) |

| A cited evidence answer | Questions that need a person |
|---|---|
| ![Sertraline during breastfeeding: measured exposure with study links](presentation/screenshots/answer.png) | ![Crisis, rule-override, vaccine-decision and off-topic replies](presentation/screenshots/safety-stops.png) |

| Help in Spanish | Results |
|---|---|
| ![Spanish-language reply with MotherToBaby and 988](presentation/screenshots/spanish.png) | ![Results: 7 of 7 paired tasks with the MCP, 0 of 7 without](presentation/screenshots/results.png) |

## How it works

```mermaid
flowchart TD
    U[User with a public or synthetic question] --> C[Companion client]
    C --> P[Mandatory preflight]
    P -->|Stop route| F[Fixed response: no evidence or model calls]
    P -->|Research permitted| M[Model selects MCP tools]
    M --> T[21 tool registrars and validated domain services]
    T --> H[Bounded HTTPS source clients]
    T --> S[Dated public MPRINT snapshots]
    H --> A[Approved public evidence sources]
    A --> E[Structured evidence, provenance and required notices]
    S --> E
    E --> C
    C --> O[Cited response, visible gaps and clinician questions]
```

1. **Confirm the question and medication identity.** The bundled client applies preflight before downstream research. Urgent/crisis, unconfirmed-identity and unsupported-language routes stop conservatively.
2. **Retrieve bounded evidence.** Tools normalize ingredients, query public sources and return structured results. The composite brief covers confirmed ingredients and preserves population/age-band tags.
3. **Keep three evidence axes visible.** Effects on the pregnant/lactating person, measured fetal/infant transfer or exposure, and observed fetal/infant outcomes stay separate—even when a row is empty.
4. **Carry limitations with the data.** Missing abstracts/sections, truncation, source dates, label-selection basis, dose-bearing passages and noncausal adverse-event counts travel in the payload.
5. **Support preparation.** Responses link to sources and offer clinician questions. Registries and recruiting studies form a separate, unranked participation tier, suppressed on stop routes.

The model is supplied by the client; an MCP server is not itself a model or chatbot UI. The bundled companion uses a Databricks model gateway. Other clients must implement the same preflight and required-display contracts; MCP registration alone does not enforce those client behaviors. [Architecture details](documentation/ARCHITECTURE.md).

## Data sources and tool coverage

| Source or capability | Purpose | Important limit |
|---|---|---|
| RxNorm | Normalize names and ingredients | A name match does not confirm the user's exact product |
| LactMed | Lactation records, exposure measurements and infant findings | **Lactation-only**, not a pregnancy database |
| DailyMed and FDA sources | Selected labeling, pediatric changes, recalls, alerts and adverse-event reports | Label selection/version matter; FAERS counts lack denominators and do not establish causation |
| PubMed | Pregnancy/lactation literature and available abstracts | Search coverage is bounded; missing abstracts are disclosed |
| ClinicalTrials.gov and FDA registry directory | Studies and pregnancy exposure registries | Verify status and contacts; inclusion is not a recommendation |
| NIH RePORTER | Funded research and program-staff portfolio exploration | Public records have coverage and reporting limits |
| Public MPRINT snapshots; NICHD/BPCA material | Domain-specific records, outcomes, classifications and research links | Dated snapshots are not a live or complete evidence base |
| MedlinePlus | Patient education, including source-authored Spanish material | Spanish education does not imply supported Spanish clinical chat |

**Data provenance.** Every source above is a public federal source, with two exceptions that are included deliberately and labeled in tool results:

| Source | Who publishes it | Why it is included | How it is labeled |
|---|---|---|---|
| MPRINT knowledge-base snapshot | The MPRINT Hub, funded by NICHD, publishes it openly on a university lab's GitHub repository under an MIT license (bundled as [MPRINT-LICENSE.txt](src/parent_child_pharmacology/mc/data/MPRINT-LICENSE.txt)). The freshness check reads `api.github.com`, the only non-federal host on the outbound allowlist. | It is the curated maternal and pediatric pharmacology dataset closest to NICHD's mission, and the fixed-snapshot benchmark is built on it. | Results state the snapshot date and revision, and that inclusion is not proof of quality or of MPRINT funding. |
| MotherToBaby fact sheets | The Organization of Teratology Information Specialists (OTIS), a nonprofit, under CC BY-NC-ND 3.0. The text is read from the National Library of Medicine's NCBI Bookshelf package. | They are the plain-language pregnancy and breastfeeding summaries that NLM itself distributes alongside LactMed. | Results call them nonprofit consumer content, separate from federal evidence, and reproduce them word for word with attribution. |

The FDA pregnancy exposure registry directory is a federal page; the registries it lists are run by companies and universities, and are shown as unranked listings, never recommendations. Both exceptions can be removed without affecting the other tools.

Browse the [21-tool catalog](src/parent_child_pharmacology/tools/__init__.py), [source clients](src/parent_child_pharmacology/clients/), [four prompts](src/parent_child_pharmacology/prompts/) and [five resources](src/parent_child_pharmacology/resources/). The main workflow tool is `medication_evidence_brief`; targeted tools include `normalize_drug`, `check_evidence_coverage`, `search_funded_research` and `find_pregnancy_exposure_registries`.

## Results at a glance

**Design review.** After the .25 evaluation, a review of the code against GSA's judging criteria found problems the scripted cases could not see: one evidence brief returned up to 1.5 million characters, several tools overlapped, some crisis wording was let through, and short English searches were blocked. Versions 0.20.0 and 0.21.0 merge 31 tools into 21, return a summary brief first (about 20 times smaller, with totals and a statement of what was left out), and fix the routing rules with tests in both directions. The lesson: measure what the AI client receives, not only whether answers pass. See [tool migration](documentation/TOOL_MIGRATION.md).

**Hands-on testing.** I also connected the server to Claude Desktop and used it in ordinary chats. That found three problems the scripted cases missed (cut-off LactMed answers, no links to cited studies, unreadable MotherToBaby fact sheets), all fixed and tested. See [hands-on testing](documentation/HANDS_ON_TESTING.md).

**Latest evaluated version: 0.22.2** (policy .29, 21 tools; November 23, 2026; [report](evaluation/v0222-final/REPORT.md)). Every answer was generated fresh on this version. The earlier [.25 report](evaluation/policy25-final/REPORT.md) describes the 31-tool build. Scores measure different things and must remain separate.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **1,051 local; 1,051 Databricks** | No failures, errors or skips |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| MCP Inspector | **9/9 (.14; not repeated)** | Protocol, schemas and sampled contracts |
| Fresh chats | **27/27 completed** | 20 research and seven stop cases |
| Expected routes and tool checks | **27/27 routes; 27/27 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls; on known wording. Unseen wording: 57% and 16% ([held-out check](#held-out-safety-check)) |
| Research answers | **20/20 fidelity; 19/20 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 1/4/2** | N/A is not a fidelity pass |
| Citation and trace checks | **20/20 URL membership; 41 MLflow rows verified** | URL membership does not establish claim support |
| Fixed-snapshot benchmark | **10/10 exact answers; 10/10 completed** | Separate Phoenix task, not the seven-case comparison |

The one unfulfilled research task was judged accurate but left the recall reasons out of its table. This tool set was evaluated three times, and each run is kept: [0.22.0](evaluation/v0220-final/) scored MCP paired fidelity 5/2/0, which 0.22.1 corrected by stating who wrote each server notice; [0.22.1](evaluation/v0221-final/REPORT.md) scored 18/20 research tasks because the summary brief left out label text, which 0.22.2 corrected. Both fixes were written after seeing those failures on known questions. How the evaluation and its grader changed in earlier versions is in the [evaluation history](documentation/EVALUATION_HISTORY.md).

### Held-out safety check

After the results above, I wrote 282 new safety-routing messages in wording the router had never seen, committed them before running them ([questions](eval/heldout/)), and ran each once on version 0.22.2. **The fixed stops caught 74 of 130 stop-worthy messages in the first set (57%) and 14 of 88 in a second set with more varied wording (16%).** 59 of 64 research questions were correctly let through. By category in the first set: Spanish 10 of 10, dose questions 15 of 20, role-play 9 of 12, crisis 9 of 15, start or stop decisions 10 of 20, emergencies 5 of 15, poisoning 4 of 10.

A drafted update to the wording rules reached 169 of 170 on the first set but only 43 of 112 on the second, so it was not applied: adding wording rules does not generalize. In the missed cases read so far, the question went on to the model, which still told the person to call emergency services or declined to give a dose, but without the fixed 988, maternal hotline and Poison Help text. The 7 of 7 result in the table is on wording the router was built around. The fixed stops are a first layer, not a guarantee; the next step is a model-based check in front of them. [Result files](evaluation/heldout-2026-11-23/).

### What the grades mean

Fidelity asks whether claims are supported by the captured references. Task fulfillment asks whether all requested requirements were met. Neither is clinical accuracy. These are known development cases, one retained completed answer per case/arm, bounded references and a fallible same-family model judge. There was no clinician adjudication, manual score override or selection of a better completed answer. Live sources and model outputs vary. Other clients must enforce preflight and display contracts themselves.

The seven-case comparison measures the MCP workflow, including tools, preflight and required notices. The plain arm has no retrieval tools; 0/7 can reflect honest inability to verify a current lookup, not seven fabricated or medically wrong answers. Both arms receive the same updated instructions. The paired runner omits the companion’s additional source-review pass.

The ten-question benchmark is an exact-answer test of joins, filters, candidate selection and arithmetic against a fixed MPRINT snapshot. It is separate from the chat and paired scores. It is small, known, partly cohort-sharing and not held out. Runtime and client instructions changed together, so any gain is not a controlled estimate of one fix. Exact agreement with snapshot fields does not establish clinical truth, safety, source completeness or performance across all tools.

## Safety and security

The intended use is **evidence discovery and clinician preparation**. This is not prescribing or personal treatment guidance, clinical triage, exhaustive evidence or a guarantee of safety, or clinical certification.

| Failure mode | Implemented control and remaining boundary |
|---|---|
| Partial retrieval looks complete | Missing sections, truncation, label-selection basis and ingredient coverage are disclosed; extraction can still miss context |
| Missing data sounds reassuring | Explicit no-evidence fields and study-base uncertainty; “no reports” is not a safety conclusion |
| Population mismatch | Population tags and separate neonate/infant/child/adolescent bands; generated wording still needs review |
| Counts read as rates | FAERS denominator and causation caveats remain in the payload |
| Superseded information looks current | Legacy letter-category flags, label dates and snapshot revision metadata; freshness remains source-dependent |
| Adverse findings prompt medication discontinuation | Context and standing medication-change notices; accurate wording can still be alarming and needs independent clinical review |

Network controls include an exact HTTPS host/port allowlist, rejected redirects, disabled proxy inheritance, bounded timeouts/retries and a 5 MB response cap. Credentials are attached only to explicitly configured remote MCP destinations; no Databricks token is sent to loopback. Logging is filtered and HTTP access logs are disabled. See [outbound-security tests](tests/test_outbound_security.py), [credential tests](tests/test_client_credentials.py) and [the security model](SECURITY.md).

**LactMed study links.** LactMed record text comes from NCBI's official LactMed package (`scripts/build_lactmed_snapshot.py`), because NCBI's web pages can show automated clients a browser check that this server never bypasses. Each record keeps LactMed's own citation markers, such as [54], and returns the cited studies with PubMed links. Search still runs live through NCBI E-utilities.

**Pediatric evidence briefs.** `medication_evidence_brief` with a pediatric population (neonate, infant, child, adolescent or pediatric) returns three pediatric rows: effectiveness and safety findings, pharmacokinetics and exposure, and labeling status and changes, drawn from DailyMed 8.4 Pediatric Use, FDA pediatric labeling changes, pediatric abstract sentences and FAERS report context, plus BPCA/PTN links. Both chat clients display the matching rows.

**MotherToBaby fact sheets.** `search_mothertobaby_fact_sheets` returns English and Spanish fact sheet questions and answers verbatim from NCBI's official MotherToBaby package (`scripts/build_mothertobaby_snapshot.py`), with OTIS attribution and the CC BY-NC-ND 3.0 license. Answers are never shortened; when the length limit is reached, whole questions are omitted and listed. Fact sheets are labeled as nonprofit consumer content, separate from federal evidence.

**Data freshness.** MPRINT, LactMed and the MotherToBaby fact sheets are bundled, dated copies; every other source is fetched live. Every LactMed result states the package date and the record's last revision. Every MPRINT result includes a `data_freshness` block with the saved copy's date, revision and a plain-language note to show users. **Checking by prompting:** ask the AI whether the MPRINT data is current, and `find_mprint_records` with `check_for_updates` checks MPRINT's repository live and reports whether newer data has been published since the saved copy. The server is read-only, so a question never rewrites the data; a maintainer rebuilds the copy. The `parent-child://mprint-snapshot` resource runs the same check, and a weekly GitHub workflow (`.github/workflows/data-freshness.yml`) fails when MPRINT publishes changes. The upstream check reads `api.github.com`, the only non-federal host on the allowlist, read-only.

Use **public or synthetic questions only**. Local HTTP defaults to loopback. Non-loopback HTTP now fails closed without operator-configured RS256 verification and individual tool permissions. Connection-time DNS/IP pinning is tested. Future hosting still requires issuer/key configuration, gateway access, cloud egress and retention policies. Routing is heuristic; no penetration-test, clinical-certification or production-readiness claim is made. The staged source scan found no credentials. The final capture/artifact scan is recorded in the current evidence directory.

## Run it yourself

Prerequisites: **Python 3.13 and [uv](https://docs.astral.sh/uv/)**. Clone this repository, then run from its root:

```sh
uv sync --locked --group dev
uv run --locked python main.py
```

Default transport is **stdio**, for an MCP client to launch as a subprocess—not a browser interface. Public-source retrieval does not require Databricks or a model account. Configure your NCBI contact email for live NCBI use. [QUICKSTART.md](QUICKSTART.md) covers client configuration, `.env.example`, optional loopback HTTP, `/health` and `/version`.

Run application and grader checks:

```sh
uv run --locked pytest tests -q
uv run --locked pytest eval/harness/tests -q -o pythonpath=eval/harness
uv run --locked ruff check src tests main.py eval/run.py eval/databricks/submit-tests.py
uv run --locked ruff format --check src tests main.py eval/run.py eval/databricks/submit-tests.py
uv build
```

Fresh chat/model comparisons need separately configured Databricks model access and can incur costs. Follow the [evaluation harness](eval/README.md) and use a **new output directory**. The [Databricks test kit](eval/databricks/README.md) runs isolated notebook tests without changing the App. Frozen source hashes, failed attempts and raw grades are preserved.

## Repository map and template alignment

| Path | Role |
|---|---|
| `main.py`, `pyproject.toml`, `uv.lock`, `.env.example` | Root entry point, package, locked dependencies and configuration |
| `src/parent_child_pharmacology/` | Application, schemas, source clients, shared controls and domain services |
| `src/parent_child_pharmacology/tools/` | One registrar per tool; separate `prompts/` and `resources/` |
| `chat-client/` | Companion orchestration, preflight and required-display behavior |
| `tests/` | Application, security and client-contract regression tests |
| `eval/` | Current portable evaluation harness and Databricks test kit |
| `evaluation/` | Dated captures, metrics, raw judgments, test and MLflow receipts |
| `presentation/` | Deck, demo video, recording slides and screenshots |
| `documentation/` | Evaluation DOCX, architecture, methodology, requirements and deployment guidance |
| `deploy/databricks/`, `Dockerfile`, `server.json` | Deployment kit, container build and registry metadata; deployment is a manual step |
| `.github/workflows/ci.yml` | Windows/Linux lint, format, application/grader tests and package builds |
| `SECURITY.md`, `NOTICE.md`, `LICENSE-GSA-TEMPLATE` | Security boundaries and template attribution |

The [GSA template](https://github.com/GSA-TTS/mcp-hackathon-template) supplies the engineering scaffold. The [complete 65-file audit and remediation table](documentation/TEMPLATE_DETAILED_AUDIT.md) distinguish implemented controls, adaptations and outstanding deployment prerequisites. This repository aligns its existing implementation in place; it does **not** claim a recreated template ancestry. This README adds a project-specific submission guide. [The requirements review](documentation/GSA_REQUIREMENTS_REVIEW.md) maps implementation to the template and official evaluation materials.

## Scope and next steps

The prototype surfaces evidence gaps; it does not close them. Priorities before considering real-world use are independent clinical framing review, held-out and repeated evaluations, broader adversarial/language testing, source-coverage review and deployment security/operating review. The Databricks App `mcp-mc` was redeployed with version 0.22.2 (policy .29) on November 23, 2026; hosted use relies on workspace sign-in and still needs a deployment security and operating review.

Built for the GSA hackathon as a prototype. **Not an official NIH MCP tool. No production readiness claim.**
