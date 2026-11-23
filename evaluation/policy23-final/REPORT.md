# Policy .23 evaluation (November 23, 2026): intermediate, superseded by .24

Source 0.19.0, policy 2026-11-23.23, benchmark runner v6. Retained as run; the final results are in [../policy24-final](../policy24-final/REPORT.md).

| Measure | Result |
|---|---|
| Fresh chats; routes; tools; fixed stops | 28/28; 28/28; 28/28; 7/7 (E01 retried once after HTTP 429, failed capture archived) |
| Research answers | 20/21 fidelity; 21/21 tasks (R04 graded "caplets" versus "tablets" as unsupported) |
| Paired tasks | MCP 6/6 scored, 1 unscored (R03); plain 0/6 scored, 1 unscored (E02) |
| Benchmark | 9/10 (B06 copied the wrong exposure label; B02 retried once after a gateway JSON error, failed capture archived) |
| Application tests | 953 local; 953 Databricks (run 701198736229523) |

This run confirmed the `notice_attribution` fix: D05 and R08, which failed in .20, passed. It also showed the B06 failure mode that runner v7 addresses. Three paired grades that could not be validly grounded were archived and regraded once; two remained unscored. Paired MLflow readback stops at the recorded grader errors.

MLflow: [parent](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/90fbac0e1ef44358a3368e79c4520057) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/2eaf5de44a814545b940fec0baab00f4) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/74035d5d7ba84245b77242b1a0d7f2b5) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/2f92137dc28c4e7dae058af63cdbdad9)
