# Current implementation

Current source **0.12.0**, policy **2026-11-21.12**. The existing Databricks App remains on .9, deployment `01f1e5f7f6fc162fb8c3cc875e7f8546`. MCP/chat/paired drivers and Phoenix ran locally; models and MLflow used Databricks. A separate Databricks serverless notebook ran the frozen source tests. Code is pushed only to the existing private GitHub repository. No App deployment, access-policy change, public release or official GSA submission occurred.

The .12 revision adds connection-time public-IP validation and pinned HTTPS connections with original TLS verification; fail-closed remote RS256 authorization with individual tool scopes; initialize-level guidance; JSON/Markdown outputs that preserve structured safety fields; explicit continuation metadata and PubMed offsets; staged src imports; and public SDK Tool construction without private manager mutation. Sixty-four added tests exercise these boundaries. The GSA template's 65-file audit is retained with current dispositions.

Remote hosting still requires an operator-managed issuer/public key/audience, gateway access controls and network egress policy. No firewall or identity infrastructure was provisioned. The official pinned mcp SDK and stable tool names remain documented adaptations. Sources without continuation support explicitly report unknown completeness rather than inventing cursors. A .12 deployed-App evaluation remains outstanding because this revision does not deploy the App.

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
