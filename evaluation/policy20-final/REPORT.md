# Policy .20 evaluation (November 23, 2026)

Current source 0.19.0, policy 2026-11-23.20. Answers were generated fresh with the local MCP server (loopback HTTP) and the Databricks model gateway (`system.ai.gpt-5-6-luna`), graded by the same model family, and logged to Databricks MLflow. The questions, reference answers and grading rubric are unchanged from .14. No App deployment, public release or official submission occurred.

| Measure | Result | Interpretation |
|---|---|---|
| Application tests | **884 local** (PowerShell tests included); 884 Databricks | No failures, errors or skips |
| Grader unit tests | **33 passed** | Separate evaluator contracts |
| Fresh chats | **28/28 completed** | 21 research and seven stop cases |
| Expected routes and tool checks | **28/28 routes; 28/28 tools** | Trace contract checks |
| Fixed stops | **7/7** | No downstream evidence or model calls |
| Research answers | **19/21 fidelity; 21/21 tasks fulfilled** | Was 17/21 and 21/21 in .14 |
| Paired tasks | **MCP 7/7; plain 0/6 scored** | One plain answer could not be graded (below) |
| Paired fidelity pass / fail / N/A | **MCP 7/0/0; plain 1/3/2**, 1 unscored | N/A is not a fidelity pass |
| Citation checks | **21/21 URL membership** | URL membership does not establish claim support |
| MLflow readback | **Research 21 and stops 7 rows verified**; paired 13 of 14 rows | The unscored row has a recorded grader error |
| Fixed-snapshot benchmark | **10/10 exact answers; 10/10 completed** | Was 9/10 in .14 |

MLflow: [parent run](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/f256db6a7543438f9c9cfb2522c999cc) · [research](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/c5b909753bb14cdd820409c7c23c9625) · [stops](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/eaeb3f91a7ce457cada397f085318cc1) · [paired](https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/ba6080c094184e86a38ed36506899cd2) · [benchmark summary](benchmark/summary.json) · [chat summary](chat-summary.json)

## The benchmark: 9/10 to 10/10

In .14, B09 found the correct study but copied the DOI of a different candidate. The client that runs the benchmark now requires the model to select the record from the original candidate set before copying a field, and copies the DOI directly from that selected record rather than from the model's own text. B04's count now comes from deterministic filtering and distinct-PMID counting. These are client utilities, not MCP tools. The ten questions and reference answers are unchanged, and reference answers are never shown to the answering model.

This run answered all ten exactly, including B09 (`10.1016/j.ejogrb.2008.02.003`). It is one run on ten known questions: it shows the B09 failure no longer reproduced here, not that it cannot recur. The .13 run also scored 10/10 before .14 scored 9/10.

## The two research fidelity failures

Both answers fulfilled the task, and in both the grader found the facts themselves supported. Each failed on one attribution: the answer credited a statement to "MCP guidance" (D05) or "the MCP implementation" (R08). The statement came from a tool notice, but no source by that name appears in the reference evidence. These answers were kept as generated. A client instruction to attribute notices to the returning tool by name would address this, but it was not changed after seeing these scores.

## The unscored plain-model answer

The grader failed to produce a validly grounded assessment for the plain-model (no tools) R04 answer in three attempts. Following the .14 procedure, that record was archived in `failed-attempts/` and the unchanged answer was graded again. The second grading also failed in three attempts, so R04-plain is reported as unscored rather than retried until a score appeared. The first paired MLflow run's records are archived in `failed-attempts/first-paired-mlflow/`. Because of this row, the paired MLflow readback stops at the recorded grader error; the other 13 rows carry valid scores.

## Not run

The MCP Inspector protocol check was not repeated (Node is not installed on this machine). The .14 result was 9/9.

## Limitations

These are the same known development cases, one retained answer per case and arm, graded by a fallible model of the same family with no clinician review. Fidelity means support in the captured references, not clinical accuracy. The plain arm has no retrieval tools, so 0/6 can reflect an honest inability to look things up rather than fabricated answers. Several runtime and client changes happened together since .14, so no score change can be credited to a single fix. Some harness run labels still read ".16"; they are inherited text in the frozen harness, and the run design file records version 0.19.0 and policy .20.
