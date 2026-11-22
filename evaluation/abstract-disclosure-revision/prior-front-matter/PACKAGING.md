# Submission package

This revision changes the grader and submission documents only. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Tests and the replay driver ran locally; grader calls and MLflow used the existing Databricks services.

Fresh local tests: **562 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched fidelity and task expectations. These controls are not held-out or clinical validation. All 114 frozen application files are unchanged; 93 runtime files were verified during the prior .9 deployment. The prior inventory of 30 tools, four prompts and four resources is unchanged and was not re-probed this revision.

The deck has 49 slides: 15 main and 34 hidden appendix. The evaluation DOCX was rendered and reviewed. Prior artifacts and raw evaluations are retained. Current verification: evaluation/grader-attribution-revision/final-validation.json and evidence-manifest.json; package hashes: SHA256SUMS.txt. Demo media remain historical .4 captures.
