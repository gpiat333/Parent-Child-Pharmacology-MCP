# Submission package

The existing **mcp-mc Databricks sandbox app was updated** on November 21, 2026 at the user's request. No GitHub push or official submission occurred. No new cluster, warehouse, model endpoint, permissions or provider settings were created or changed. The evaluation driver ran locally; MCP serving, model calls and MLflow tracking were in Databricks. The 508 unit tests are the prior verified local baseline on unchanged source, not a new remote unit run.

Local unchanged-source baseline: **508 unit tests passed** with no failures, errors or skips. Active Databricks inventory: **30 tools, four prompts and four resources**. All **93 deployed runtime files** match the staged source; all 112 frozen server/client files remain unchanged. Runtime probes: 30 valid schemas, eight invalid inputs rejected and 20 source/workflow captures (including partial/empty statuses).

The PowerPoint has 49 slides (15 main, 34 hidden appendix). The evaluation DOCX is rendered and reviewed alongside it. Prior deck/DOCX and local evidence are retained. See evaluation/databricks-validation-2026-11-21/final-validation.json, evidence-manifest.json and root SHA256SUMS.txt for final verification. Existing video is a labeled predeployment local replay. No clinical validation is claimed.
