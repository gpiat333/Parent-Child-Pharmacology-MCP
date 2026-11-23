# Databricks validation

Current source 0.19.0, policy 2026-11-23.26. Policy .15 fixes safety-routing false positives found after evaluation (condition names such as seizures or postpartum depression were treated as emergencies); evaluation results describe .25 ([report](../evaluation/policy25-final/REPORT.md)). Policy .16 adds the HRSA National Maternal Mental Health Hotline (1-833-TLC-MAMA) to perinatal crisis replies and recognizes more postpartum wording. Policy .17 adds a MotherToBaby referral for individual pregnancy and breastfeeding medication questions, a MotherToBaby fact sheet search (NLM Bookshelf, labeled as nonprofit content), PRGLAC research-gap context in pregnancy and lactation briefs, and an NIH-only scope note on funding results. Version 0.19.0 (policy .19) combines that work with the November 22 evidence-display and snapshot-filtering changes, which were developed separately as 0.18.0. Policy .20 lets “Can I take X?” questions receive the public evidence with a fixed message that the decision belongs with a clinician or pharmacist (plus MotherToBaby for pregnancy or breastfeeding); dose, start/stop, switch and taper requests still stop. Policy .21, made after the .20 evaluation, stops role-play, claimed-permission and “ignore your rules” framings; sends decisions for anyone, including “should my patient…” and vaccine decisions, to a clinician; treats yes-or-no and “safe for my baby?” requests like “Can I take X?”; returns an out-of-scope message for unrelated tasks such as ordering food; stops blocking short plain-English questions such as “Do vaccines cause autism?”; and adds the label's description section (chemical name, molecular formula and ingredients). Policy .22 maps common vaccine names (“flu vaccine”, “Tdap”) to LactMed's vaccine records and explains that RxNorm needs a product name; returns the label's approved uses and clinical studies (mostly adults) and, in pediatric briefs, where off-label use is documented, including NICHD's BPCA priority list; adds the 15 PRGLAC recommendations to pregnancy and lactation briefs; gives Spanish questions MotherToBaby's Spanish service, 988 in Spanish and MedlinePlus en español while still stopping them; and adds an NCCIH herbs link to supplement questions. Policy .23 adds a notice_attribution field to every tool result, stating that notices and interpretation rules are written by this MCP server, not quoted from sources (the cause of the two .20 fidelity failures), and lets find_mprint_records check MPRINT's repository live for newer data when a user asks whether it is current. Policy .24 lets short English statements before a question (“I'm breastfeeding. Can I take ibuprofen?”) through the language check by masking medicine names, which had made the detector call them foreign; the benchmark client (runner v7) adds per-group statistics over captured rows. Policy .25 has answers report a source's warnings as that source's statements (“The label states that…”) rather than as instructions in the assistant's own voice, and name only the contacts the results name. Policy .26 adds 15 fixed Spanish safety messages, reviewed by a native Spanish speaker and aligned with official MedlinePlus, 988 and PSI wording, returned as `message_es` when someone writes in Spanish; all safety messages now speak as the service (“This service can't…”). Evaluated locally with Databricks model calls and MLflow tracking; the same frozen source passed in a Databricks serverless notebook. The Databricks App `mcp-mc` runs policy .26 (deployment `01f1e77924a01179b82b6e9b4fe23efd`, November 23, 2026), with workspace sign-in as its access control. No App deployment, public release or official submission occurred.

| Measure | Verified result | Interpretation |
|---|---|---|
| Application tests | **968 local; 968 Databricks** | No failures, errors or skips |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| MCP Inspector | **9/9 (.14; not repeated)** | Protocol, schemas and sampled contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **21/21 fidelity; 21/21 tasks fulfilled** | Separate fallible model judgments |
| Paired tasks | **MCP 7/7; plain 0/7** | Same model and shared instructions; different workflows |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 2/4/1** | N/A is not a fidelity pass |
| Citation and trace checks | **21/21 URL membership; 42 MLflow rows verified** | URL membership does not establish claim support |
| Fixed-snapshot benchmark | **10/10 exact answers; 10/10 completed** | Separate Phoenix task, not the seven-case comparison |


[Verified MLflow run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/a6b8c5b2f9394469af76172510a5b4d6). Notebook run 72360106331552 passed 709 tests.

**Policy .15 re-run (November 22, 2026):** Databricks serverless run 378121935866176 passed **738/738** tests on the frozen .15 source (0 failures, 0 errors, 0 skipped, including the PowerShell parity tests). [Receipt](../evaluation/databricks-validation-2026-11-22-policy15/databricks-job-output.json).

**Policy .16 re-run (November 22, 2026):** Databricks serverless run 214446837417092 passed **754/754** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy16/databricks-job-output.json).

**Policy .17 re-run (November 22, 2026):** Databricks serverless run 466777602936619 passed **768/768** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy17/databricks-job-output.json).

**Version 0.19.0 / policy .19 (November 22, 2026, after merging the evidence-display branch):** Databricks serverless run 725529477134538 passed **848/848** tests, including every PowerShell parity test (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-policy19/databricks-job-output.json).

**LactMed study links (November 22, 2026):** Databricks serverless run 405600821258309 passed **857/857** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-lactmed-refs/databricks-job-output.json).

**MotherToBaby fact sheet text (November 22, 2026):** Databricks serverless run 396432898767817 passed **861/861** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-22-mtb-text/databricks-job-output.json).

**Pediatric evidence briefs (November 23, 2026):** Databricks serverless run 511770629703382 passed **869/869** tests, including the Python/PowerShell pediatric display parity tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-23-pediatric-brief/databricks-job-output.json).

**Policy .20 (November 23, 2026):** Databricks serverless run 968719264495762 passed **884/884** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-23-policy20/databricks-job-output.json).

**Policy .21 (November 23, 2026):** Databricks serverless run 419956253344414 passed **928/928** tests (0 failures, 0 errors, 0 skipped), including 44 new safety-routing tests. [Receipt](../evaluation/databricks-validation-2026-11-23-policy21/databricks-job-output.json).

**Policy .22 (November 23, 2026):** Databricks serverless run 171364700711551 passed **949/949** tests (0 failures, 0 errors, 0 skipped), including 21 new tests for vaccine names, adult and off-label sources, PRGLAC recommendations, and Spanish and supplement resources. [Receipt](../evaluation/databricks-validation-2026-11-23-policy22/databricks-job-output.json).

**Policy .23 (November 23, 2026):** Databricks serverless run 701198736229523 passed **953/953** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-23-policy23/databricks-job-output.json).

**Policy .24 (November 23, 2026):** Databricks serverless run 335241140191974 passed **965/965** tests (0 failures, 0 errors, 0 skipped). [Receipt](../evaluation/databricks-validation-2026-11-23-policy24/databricks-job-output.json).

**Policy .25 (November 23, 2026):** Databricks serverless run 909790976530204 passed **968/968** tests (0 failures, 0 errors, 0 skipped). This is the evaluated final version. [Receipt](../evaluation/databricks-validation-2026-11-23-policy25/databricks-job-output.json).

**Policy .26 (November 23, 2026):** Databricks serverless run 298691906316208 passed **976/976** tests (0 failures, 0 errors, 0 skipped), including the Spanish safety-message tests. [Receipt](../evaluation/databricks-validation-2026-11-23-policy26/databricks-job-output.json).

[Current evidence](policy25-final/REPORT.md) · [.24](policy24-final/REPORT.md) · [Intermediate .23](policy23-final/REPORT.md) · [.20](policy20-final/REPORT.md) · [.14](retrieval-reliability-final/REPORT.md)
