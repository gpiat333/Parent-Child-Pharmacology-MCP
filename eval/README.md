# Reproducible evaluation

Use Python 3.13, PowerShell 7 (`pwsh`), a signed-in Databricks CLI, and `uv sync --locked --group dev --group eval`. Configure `.env` from `.env.example`: `DATABRICKS_HOST`, `DATABRICKS_CONFIG_PROFILE`, optional `DATABRICKS_CLI_PATH`, `AGENT_MODEL`, `JUDGE_MODEL`, `MLFLOW_EXPERIMENT_ID` and `MCP_EVAL_ENDPOINT`. Start the frozen MCP separately using QUICKSTART. Remote MCP requires an exact `DATABRICKS_MCP_ENDPOINT`; credentials are never sent to loopback. Do not use real patient queries.

From the repository root (choose a NEW output directory):

```sh
uv run --group eval python eval/run.py prepare --output evaluation/my-new-run
uv run --group eval python eval/run.py chats --output evaluation/my-new-run
uv run --group eval python eval/run.py paired --output evaluation/my-new-run
uv run --group eval python eval/run.py grade --output evaluation/my-new-run
uv run --group eval python eval/run.py mlflow --suite research --output evaluation/my-new-run
uv run --group eval python eval/run.py mlflow --suite stops --output evaluation/my-new-run
uv run --group eval python eval/run.py mlflow --suite paired --output evaluation/my-new-run
uv run --group eval python eval/run.py verify --suite research --output evaluation/my-new-run
uv run --group eval python eval/run.py verify --suite stops --output evaluation/my-new-run
uv run --group eval python eval/run.py verify --suite paired --output evaluation/my-new-run
```

The preparation step snapshots the harness and hashes application/client sources and locks. Subsequent steps reject changed frozen source. Each question has one retained completed capture, with failures preserved in its evidence directory. Inspect failures before resuming; never retry based on a low score. MLflow reuses fingerprint-matched diagnostic grades; it does not regenerate successful answers to improve scores. The current report documents all attempts and exclusions.

Run grader unit tests with `PYTHONPATH=eval/harness uv run pytest eval/harness/tests -q` (PowerShell: `$env:PYTHONPATH='eval/harness'`). Inspector requires Node and a local installation of `@modelcontextprotocol/inspector@1.0.6`; set `MCP_INSPECTOR_CLI` to its `cli/build/cli.js` file, optionally `NODE_PATH_EXECUTABLE`, then run `eval/run.py inspector` with the same output directory.

There are 28 known development cases: 21 research, seven fixed stops, plus seven paired questions (14 answers). Fidelity means support in the captured bounded pool; task fulfillment means completion of requested requirements. Both are diagnostic same-family model grades, not clinical adjudication. Grader v3 validates attribution and cache identity, not semantic truth. URL membership is not claim support. Ten synthetic controls are development checks, not held-out validation. Single trials and live-source variability limit causal claims. MCP alone has retrieval, workflow enforcement and required notices; the companion also has an extra review pass absent from the paired runner. No accuracy, speed, safety or general superiority claim follows from these small samples.

Historical evidence directories and their original machine-specific helper copies are immutable audit records, not the current portable harness. Current source is `eval/harness`; current evidence is linked from the root README.


The .12 revision also includes `eval/phoenix/` with a ten-question fixed-snapshot XML/CSV benchmark, dataset registry, versioned prompt and exact matching. Its results stay separate from the 28 development chats and seven paired questions. See that module for local Phoenix setup and its narrower two-tool scope. Source freezing now includes data/policy files, the root entry point and the frozen evaluation harness, not only Python application files.
