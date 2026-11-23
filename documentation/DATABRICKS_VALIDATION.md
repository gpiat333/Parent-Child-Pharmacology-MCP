# Databricks validation

Current source 0.19.0, policy 2026-11-22.19. Policy .15 fixes safety-routing false positives found after evaluation (condition names such as seizures or postpartum depression were treated as emergencies); evaluation results describe .14. Policy .16 adds the HRSA National Maternal Mental Health Hotline (1-833-TLC-MAMA) to perinatal crisis replies and recognizes more postpartum wording. Policy .17 adds a MotherToBaby referral for individual pregnancy and breastfeeding medication questions, a MotherToBaby fact sheet search (NLM Bookshelf, labeled as nonprofit content), PRGLAC research-gap context in pregnancy and lactation briefs, and an NIH-only scope note on funding results. Version 0.19.0 (policy .19) combines that work with the November 22 evidence-display and snapshot-filtering changes, which were developed separately as 0.18.0. Evaluated locally with Databricks model calls and MLflow tracking; the same frozen source passed in a Databricks serverless notebook. The existing App remains .9. No App deployment, public release or official submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **709 local; 709 Databricks** | No failures, errors or skips |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| MCP Inspector | **9/9** | Protocol, schemas and sampled contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **17/21 fidelity; 21/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 1/5/1** | N/A is not a fidelity pass |
| Citation and trace checks | **21/21 URL membership; 42 MLflow rows verified** | URL membership does not establish claim support |
| Fixed-snapshot benchmark | **9/10 exact answers; 10/10 final answers** | Separate Phoenix task, not the seven-case comparison |


[Verified MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a6b8c5b2f9394469af76172510a5b4d6). Notebook run 72360106331552 passed 709 tests.

**Policy .15 re-run (November 22, 2026):** Databricks serverless run 378121935866176 passed **738/738** tests on the frozen .15 source (0 failures, 0 errors, 0 skipped, including the PowerShell parity tests). [Receipt](../evaluation/databricks-validation-2026-11-22-policy15/databricks-job-output.json).

**Policy .16 re-run (November 22, 2026):** Databricks serverless run 214446837417092 passed **754/754** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy16/databricks-job-output.json).

**Policy .17 re-run (November 22, 2026):** Databricks serverless run 466777602936619 passed **768/768** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy17/databricks-job-output.json).

**Version 0.19.0 / policy .19 (November 22, 2026, after merging the evidence-display branch):** Databricks serverless run 725529477134538 passed **848/848** tests, including every PowerShell parity test (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy19/databricks-job-output.json).

**LactMed study links (November 22, 2026):** Databricks serverless run 405600821258309 passed **857/857** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-lactmed-refs/databricks-job-output.json).

**MotherToBaby fact sheet text (November 22, 2026):** Databricks serverless run 396432898767817 passed **861/861** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-mtb-text/databricks-job-output.json).

**Pediatric evidence briefs (November 23, 2026):** Databricks serverless run 511770629703382 passed **869/869** tests, including the Python/PowerShell pediatric display parity tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-23-pediatric-brief/databricks-job-output.json).

[Current evidence](../evaluation/retrieval-reliability-final/REPORT.md)
