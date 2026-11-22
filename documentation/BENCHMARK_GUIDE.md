# What the ten-question MPRINT benchmark measures

The **3/10** number was the historical .12 result on ten precise questions about the bundled, versioned MPRINT research tables. It was not a clinical-accuracy score, a ten-patient trial, or the seven-question MCP-versus-plain-model comparison. The later .14 run scored **9/10**. See the [current evaluation index](../evaluation/README.md) for the newest retained run.

Each question requires a single exact answer, such as a selected record's DOI, a classification count, a cohort value or a calculated difference. The runner checks the answer against a frozen reference value. Formatting matters: a wrong identifier or number fails even if much of the lookup was correct. No model judge assigns these exact-match scores.

## Why the original result was low

| Historical cases | Failure | Correction introduced after .12 |
|---|---|---|
| B06, B09 | Technical English was mistaken for unsupported language | Bounded recognition of English data-analysis clauses; foreign and mixed-language stop tests retained |
| B10 | A study's aggregate seizure-control outcome was mistaken for an active personal symptom | Distinguish aggregate outcome wording while retaining personal/acute stops |
| B01 | Incorrect arithmetic | Bounded decimal calculator using retrieved numbers |
| B04 | Incorrect count after joining classifications and exported outcome rows | Joined metadata, then deterministic condition filtering and distinct-PMID counting |
| B07, B08 | Wrong or incomplete candidate inspection | Joined metadata, pagination and instructions to preserve the requested cohort and tie-break rules |

In .14, B09 retrieved the correct candidate but copied another candidate's DOI. Intermediate .15 fixed that case with exact source-field copying, but scored 9/10 because B04 returned the unfiltered candidate count instead of the count satisfying every condition.

The current .16 client adds deterministic metadata filtering, exclusion rules, pagination checks, distinct-PMID counting and PMID ordering. The source-copy utility binds a scalar to its captured record. These operations cannot make a wrongly selected filter or field correct. Arithmetic, filtering and source copying are **three local client utilities**, not additional registered MCP tools; the server remains at 30 tools.

The final evaluation repeats the same ten questions three times using the same frozen source. All 30 answers are retained, including failures. See the [current report](../evaluation/display-contract-revision/REPORT.md) and [repeatability results](../evaluation/display-contract-revision/repeatability/summary.json). Thirty attempts are not 30 independent questions or a held-out benchmark.

## Why it differs from the other numbers

| Evaluation | Questions | What a pass means |
|---|---:|---|
| Research chat | 21 research questions, plus seven fixed-stop checks | Separate model grades assess source fidelity and fulfillment of requested tasks |
| Paired comparison | Seven questions answered with MCP and without retrieval tools | Compares two workflows using the same model and shared instructions; a plain-model abstention may be incomplete without being fabricated |
| MPRINT benchmark | Ten fixed-snapshot questions | Exact agreement with one reference value after filtering, joining, selecting or calculating from the snapshot |

## What the results cannot establish

The ten cases are known development questions, not a held-out set. Several use related tables or cohorts. Multiple client and retrieval changes occurred between versions, so the score difference cannot isolate one change's effect. A single run does not establish stability across repetitions. Exact snapshot agreement says nothing by itself about clinical truth, data completeness, patient safety, the other tools, or performance on new questions.

The questions and reference answers remain unchanged. Reference answers are supplied to the scorer, never to the answering model. Captures, failures and prior versions are retained; a better earlier score is not substituted for the latest run. The .13 run's 10/10 and .14 run's 9/10 demonstrate why one perfect result is insufficient.

[Frozen question dataset](../eval/benchmark/datasets/mprint-v1/dataset.csv) · [Dataset verification](../eval/benchmark/datasets/mprint-v1/verification.json) · [Runner](../eval/phoenix/agent.py) · [Exact scorer](../eval/phoenix/run_experiment.py).
