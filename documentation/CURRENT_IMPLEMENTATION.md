# Current implementation

Version **0.11.0**, policy **2026-11-21.11**. The existing Databricks App remains on policy **.9**, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. The current package is published to the existing **private** GitHub repository. No App deployment, permission change, public release or official hackathon submission was performed. MCP and chat/paired drivers ran locally; models and MLflow used Databricks. A separate frozen-source notebook ran the complete unit suite in Databricks.

The repository now follows the GSA template conventions: root uv project/lock and main entry point, `src/parent_child_pharmacology`, one registrar per tool, separate prompts/resources, stdio default, optional loopback HTTP, health/version routes, registry metadata, quickstart and Windows/Linux CI. Existing domain implementations and clinical display contracts were retained. This is alignment of the existing repository, not recreated template ancestry.

The shared source client now enforces exact HTTPS hosts/port 443, rejects redirects and proxy inheritance, bounds timeouts/retries, and caps declared, streamed and decompressed response bodies at 5 MB. Companion credentials are limited to explicitly configured remote destinations and never forwarded to loopback MCP. Library logs are filtered and access logs disabled. Evaluation configuration is portable. Retired server-only deployment descriptors were removed; the replacement kit does not deploy automatically. [SECURITY.md](../SECURITY.md) records data, access, trace-retention and residual-risk boundaries; template MIT attribution is retained.

Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

[Architecture](ARCHITECTURE.md) · [Current report](../evaluation/template-alignment-revision/REPORT.md)
