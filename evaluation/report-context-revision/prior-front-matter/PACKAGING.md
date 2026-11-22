# Submission package

The existing **mcp-mc Databricks sandbox app was updated** with the routing fix on November 21, 2026. No GitHub upload or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. Unit tests and the evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks.

Fresh local suite: **531 tests passed**, including 23 new routing regressions, with zero failures, errors or skips. All **93 deployed runtime files** match the staged source; 112 server/client files were frozen. Active inventory: **30 tools, four prompts and four resources**. Runtime checks: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures, retaining partial/empty statuses.

The deck has 49 slides, including 15 main slides and 34 hidden appendix slides. The evaluation DOCX was rendered and reviewed. Prior artifacts and raw evaluations are retained. Current verification: evaluation/brief-paraphrase-revision/final-validation.json and evidence-manifest.json; package hashes: SHA256SUMS.txt. Existing demo media illustrate the prior .4 revision.
