# Evaluation evidence index

Current: [template alignment revision](template-alignment-revision/REPORT.md), local MCP .11. Application tests: **622/622 locally and 622/622 in a Databricks serverless notebook**, no failures or skips. Separate grader tests: **30/30**. Synthetic development controls: **10/10** on both dimensions. MCP Inspector: **9/9**, covering 30 tools, four prompts and four resources. Windows/Linux GitHub CI passes lint, formatting, application/grader tests and package builds.

Fresh chats: **28/28 completed**, **28/28 expected routes**, **28/28 tool checks**; **7/7 fixed stops** made zero downstream evidence/model calls. URL membership: **21/21** research answers. All **42 MLflow rows** were read back with their applicable scores and zero scorer execution errors.

Research grades: **17/21 fidelity passes**, **21/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP 7/7, plain model 0/7**. Paired fidelity pass/fail/N/A: **MCP 6/1/0**, **plain 1/4/2**. N/A is excluded from fidelity rates.

Use [the portable harness](../eval/README.md) for new runs. Historical revision folders, including abstract-disclosure-revision (.10), grader-attribution-revision, report-context-revision, brief-routing-revision and earlier snapshots, retain their original figures and machine-specific helper copies. They are audit records, not current installation instructions.
