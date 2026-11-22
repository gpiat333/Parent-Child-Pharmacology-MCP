# GSA template alignment evaluation

Version **0.11.0**, policy **2026-11-21.11**. The existing Databricks App remains on policy **.9**, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. The current package is published to the existing **private** GitHub repository. No App deployment, permission change, public release or official hackathon submission was performed. MCP and chat/paired drivers ran locally; models and MLflow used Databricks. A separate frozen-source notebook ran the complete unit suite in Databricks.

Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

## Changes and test environments

The repository now follows the GSA template conventions: root uv project/lock and main entry point, `src/parent_child_pharmacology`, one registrar per tool, separate prompts/resources, stdio default, optional loopback HTTP, health/version routes, registry metadata, quickstart and Windows/Linux CI. Existing domain implementations and clinical display contracts were retained. This is alignment of the existing repository, not recreated template ancestry.

The shared source client now enforces exact HTTPS hosts/port 443, rejects redirects and proxy inheritance, bounds timeouts/retries, and caps declared, streamed and decompressed response bodies at 5 MB. Companion credentials are limited to explicitly configured remote destinations and never forwarded to loopback MCP. Library logs are filtered and access logs disabled. Evaluation configuration is portable. Retired server-only deployment descriptors were removed; the replacement kit does not deploy automatically. [SECURITY.md](../../SECURITY.md) records data, access, trace-retention and residual-risk boundaries; template MIT attribution is retained.

The 30 added tests cover 20 outbound-policy cases, six entry-point cases, one real stdio connection and three credential-destination cases. The final unit suite passes locally and in Databricks. Databricks attempt 1 lacked PowerShell and two saved public fixtures (586 pass, 33 fail, three skip); attempt 2 stopped on a checksum text-encoding issue; attempt 3 installed the required prerequisites, checked the official release hash and passed 622/622. An initial oversized archive upload was rejected before execution; sharded uploads retain a whole-archive SHA-256. All receipts are retained. The first local grader run had two fixture-path failures after migration; corrected path discovery passes 30/30 without changing grader semantics.

## Method and limitations

Fidelity asks whether claims are supported by the captured, bounded reference pool; task fulfillment asks whether requested requirements were met. They are separate, fallible model judgments. A supported answer may omit an item; an honest abstention may leave a lookup incomplete. Quote checks and URL membership do not establish medical truth, relevance or safety.

Cases and grader v3 core are unchanged. These are known development questions with one retained fresh answer per case/arm, not held-out or repeated-trial validation. Live sources, caches, snapshots and model variability affect results. The judge is from the same model family; no clinician adjudication or manual score override occurred. MCP alone has retrieval, preflight enforcement and application notices; the main companion adds a source-review pass absent from the paired runner. The shared reference pool can contain evidence an answer never received. This is a small workflow comparison, not proof of clinical accuracy, speed or general superiority.

Retained research flags concern an absence-of-literature statement overstated as absence of measurement (R02), extra caveat claims outside the captured pool (R12), ancillary wording about an unvalidated MCP-generated review (E01), and a lactation-only heading on mixed pregnancy/lactation research (S6-pregnancy). Paired E01 has a separate FDA-approved label-status flag. Some flags concern scope or wording rather than a contradicted medical fact; they are not equally consequential. Read the complete raw rationales in the technical review; grading itself requires adjudication before a clinical-accuracy interpretation.

## Operational observations

Observed median elapsed time for the 28 chats: 18.41 seconds, including fixed stops. Seven-pair medians: MCP 20.16 seconds and plain 6.61 seconds. Reported answer-generation tokens: chats 5883506, paired MCP 521663, plain 10832. These are single-run observations with different tool work, caching, review passes and network conditions; they are not a speed comparison. Judge tokens, other runtime overhead and costs are not included in these token totals; no cost claim is made.

## Evidence locations

- `run-design.json`: source hashes and design frozen before capture.
- `chats/`, `paired-final/`: all retained fresh answers, source references and raw judgments.
- `chat-judge-inputs/`, `paired-judge-inputs/`: exact grader inputs.
- `unit-tests.xml`, `grader-tests.xml`, `inspector/summary.json`: local checks.
- `databricks-job-attempt3-output.json`: remote 622-test result; earlier attempt receipts retained.
- `mlflow/*-verification.json`: 42 unique trace readbacks with applicable scores.
- `summary.json`, `TECHNICAL_REVIEW.md`: current metrics and all negative grades.

No failed diagnostic grade was edited or dropped. Earlier revision directories remain immutable. GitHub is private; the App remains unchanged.
