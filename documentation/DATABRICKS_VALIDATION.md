# Databricks validation

Version **0.11.0**, policy **2026-11-21.11**. The existing Databricks App remains on policy **.9**, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. The current package is published to the existing **private** GitHub repository. No App deployment, permission change, public release or official hackathon submission was performed. MCP and chat/paired drivers ran locally; models and MLflow used Databricks. A separate frozen-source notebook ran the complete unit suite in Databricks.

Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

The complete 622-test suite ran in an isolated serverless notebook with Python 3.13 and checksum-pinned PowerShell, using the same uv lock and source. Attempt receipts and archive hashes are in `evaluation/template-alignment-revision`. Setup failures were corrected, not excluded from the audit trail. Models, diagnostic grading and MLflow tracking used the existing workspace; the App was not redeployed. See [the current report](../evaluation/template-alignment-revision/REPORT.md) and [portable notebook kit](../eval/databricks/README.md).
