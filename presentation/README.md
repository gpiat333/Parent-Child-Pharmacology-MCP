# Presentation and demonstration

49 slides: 15 main and 34 hidden appendix slides. The exact red title disclaimer and six clinical failure modes remain. Security, template alignment, fresh results and grading limits are updated.

Version **0.11.0**, policy **2026-11-21.11**. The existing Databricks App remains on policy **.9**, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. The current package is published to the existing **private** GitHub repository. No App deployment, permission change, public release or official hackathon submission was performed. MCP and chat/paired drivers ran locally; models and MLflow used Databricks. A separate frozen-source notebook ran the complete unit suite in Databricks.

Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

Fidelity asks whether claims are supported by the captured, bounded reference pool; task fulfillment asks whether requested requirements were met. They are separate, fallible model judgments. A supported answer may omit an item; an honest abstention may leave a lookup incomplete. Quote checks and URL membership do not establish medical truth, relevance or safety.

Cases and grader v3 core are unchanged. These are known development questions with one retained fresh answer per case/arm, not held-out or repeated-trial validation. Live sources, caches, snapshots and model variability affect results. The judge is from the same model family; no clinician adjudication or manual score override occurred. MCP alone has retrieval, preflight enforcement and application notices; the main companion adds a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer never received. This is a small workflow comparison, not proof of clinical accuracy, speed or general superiority.

Retained research flags concern an absence-of-literature statement overstated as absence of measurement (R02), extra caveat claims outside the captured pool (R12), ancillary wording about an unvalidated MCP-generated review (E01), and a lactation-only heading on mixed pregnancy/lactation research (S6-pregnancy). Paired E01 has a separate FDA-approved label-status flag. Some flags concern scope or wording rather than a contradicted medical fact; they are not equally consequential. Read the complete raw rationales in the technical review; grading itself requires adjudication before a clinical-accuracy interpretation.

Saved screenshots and narrated video illustrate .4. They are historical demonstrations; current metrics come from .11 fresh captures. See VIDEO_SCRIPT_CURRENT.md for updated spoken results.
