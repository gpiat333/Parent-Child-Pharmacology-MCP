# Databricks validation

Current source **0.12.0**, policy **2026-11-21.12**. The existing Databricks App remains on .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. MCP/chat/paired drivers and Phoenix ran locally; models and MLflow used Databricks. A separate Databricks serverless notebook ran the frozen source tests. Code is pushed only to the existing private GitHub repository. No App deployment, access-policy change, public release or official GSA submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **686/686 locally; 686/686 in Databricks**, no failures or skips | Contract/regression tests, not clinical correctness |
| Grader tests and controls | **30/30 unit tests; 10/10 synthetic fidelity controls** | Development checks, not independent adjudication |
| MCP Inspector | **9/9 checks** | 30 tools, four prompts, four resources; bounded protocol checks |
| Fresh chat routes and tools | **28/28 expected routes; 28/28 tool checks** | Known development questions |
| Fixed stops | **7/7**, zero downstream calls | Heuristic boundaries, not triage validation |
| Research answers | **21/21 fidelity passes; 18/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain model 0/7** | Seven known questions; unequal workflow capabilities |
| Paired fidelity pass/fail/N/A | **MCP 6/1/0; plain 1/5/1** | N/A is excluded from fidelity rates |
| Citation and trace checks | **21/21 URL membership; 42 unique MLflow rows verified** | Membership is not support for a claim |
| New fixed-snapshot benchmark | **3/10 exact answers; 7/10 generated final answers** | Separate Phoenix benchmark; three conservative routing stops and other retrieval/reasoning gaps |


[Notebook receipt](https://dbc-aae0ba16-8727.cloud.databricks.com/?o=7474654188777746#job/365762992429541/run/722956547264765) · [MLflow](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/591268c202e94d44bfadb2178a33bc8d)

The fresh notebook passed all 686 tests on its first submitted run, using an isolated Python 3.13 uv environment and the frozen public source archive. No App deployment occurred.
