# Parent-child Pharmacology MCP

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

Dataset Access Server prototype for public-evidence discovery and clinician preparation by parents, clinicians, researchers and NICHD program staff.

Version **0.11.0**, policy **2026-11-21.11**. The existing Databricks App remains on policy **.9**, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. The current package is published to the existing **private** GitHub repository. No App deployment, permission change, public release or official hackathon submission was performed. MCP and chat/paired drivers ran locally; models and MLflow used Databricks. A separate frozen-source notebook ran the complete unit suite in Databricks.

Start with [QUICKSTART](QUICKSTART.md), [template requirements review](documentation/GSA_REQUIREMENTS_REVIEW.md), [the deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), and [fresh evaluation report](evaluation/template-alignment-revision/REPORT.md).

## Template and security changes

The repository now follows the GSA template conventions: root uv project/lock and main entry point, `src/parent_child_pharmacology`, one registrar per tool, separate prompts/resources, stdio default, optional loopback HTTP, health/version routes, registry metadata, quickstart and Windows/Linux CI. Existing domain implementations and clinical display contracts were retained. This is alignment of the existing repository, not recreated template ancestry.

The shared source client now enforces exact HTTPS hosts/port 443, rejects redirects and proxy inheritance, bounds timeouts/retries, and caps declared, streamed and decompressed response bodies at 5 MB. Companion credentials are limited to explicitly configured remote destinations and never forwarded to loopback MCP. Library logs are filtered and access logs disabled. Evaluation configuration is portable. Retired server-only deployment descriptors were removed; the replacement kit does not deploy automatically. [SECURITY.md](SECURITY.md) records data, access, trace-retention and residual-risk boundaries; template MIT attribution is retained.

## Current verified results

Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

[MLflow parent run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/c7692274f7784cfc8ec42460bf690dc5) · [Databricks notebook run](https://dbc-aae0ba16-8727.cloud.databricks.com/?o=7474654188777746#job/822020545690582/run/681391949470158) · [Raw metrics](evaluation/template-alignment-revision/summary.json)

## Grading limitations

Fidelity asks whether claims are supported by the captured, bounded reference pool; task fulfillment asks whether requested requirements were met. They are separate, fallible model judgments. A supported answer may omit an item; an honest abstention may leave a lookup incomplete. Quote checks and URL membership do not establish medical truth, relevance or safety.

Cases and grader v3 core are unchanged. These are known development questions with one retained fresh answer per case/arm, not held-out or repeated-trial validation. Live sources, caches, snapshots and model variability affect results. The judge is from the same model family; no clinician adjudication or manual score override occurred. MCP alone has retrieval, preflight enforcement and application notices; the main companion adds a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer never received. This is a small workflow comparison, not proof of clinical accuracy, speed or general superiority.

Retained research flags concern an absence-of-literature statement overstated as absence of measurement (R02), extra caveat claims outside the captured pool (R12), ancillary wording about an unvalidated MCP-generated review (E01), and a lactation-only heading on mixed pregnancy/lactation research (S6-pregnancy). Paired E01 has a separate FDA-approved label-status flag. Some flags concern scope or wording rather than a contradicted medical fact; they are not equally consequential. Read the complete raw rationales in the technical review; grading itself requires adjudication before a clinical-accuracy interpretation.

## Evidence contracts and boundaries

The brief keeps three axes for every confirmed ingredient: effects on the pregnant/lactating person, measured fetal/infant transfer or exposure, and observed fetal/infant outcomes. Empty rows remain visible. Missing abstracts, expected-but-missing sections, truncation, dose-bearing passages, population/age bands, source dates, study-count uncertainty and FAERS denominator/causation caveats remain structured fields. **LactMed is lactation-only**; pregnancy evidence comes from labeling and literature. Participation is separate, unranked and suppressed on stop routes. Inactive semantic LactMed search returns `not_enabled`.

No prescribing, personal treatment decisions, clinical triage, exhaustive-evidence or safety guarantee, or clinical certification. Routing and extraction remain heuristic; every MCP client must honor preflight and required-display contracts. Public or synthetic questions only. Source-authored Spanish education is separate from clinical chat.

## Reproduction and history

Use `uv sync --locked --group dev`, then `uv run python main.py` for stdio or follow the quickstart for local HTTP. Run `uv run pytest tests -q`. [eval/README.md](eval/README.md) documents fresh chat/paired/MLflow runs; [the Databricks test kit](eval/databricks/README.md) submits isolated tests without changing the App.

The preceding .10 run had 592 application tests, research fidelity 21/21 and tasks 21/21, and paired tasks MCP 5/7 versus plain 0/7. Those figures remain historical. Differences between fresh runs are not a causal estimate. Earlier raw evidence is preserved. Saved demo screenshots/video illustrate .4 and are labeled; the deck keeps 15 main slides and 34 hidden appendix slides.
