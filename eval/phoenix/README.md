# Fixed-answer Phoenix evaluation

This adapts the GSA Phoenix module to the already-authorized Databricks model gateway. It uses a small explicit MCP tool loop instead of LangChain, and exact answer comparison instead of another LLM judge. Existing MLflow development-chat grades remain separate. Expected answers never enter the model prompt. The benchmark exposes only the two MPRINT evidence tools after preflight, with live name resolution disabled, and uses the versioned public snapshot. These are limitations as well as reproducibility controls.

Install `uv sync --locked --group dev --group eval --group phoenix`. Start the frozen loopback MCP as described in QUICKSTART. Configure the same environment as `eval/README.md`. Launch Phoenix locally with `PHOENIX_HOST=127.0.0.1`, `PHOENIX_PORT=6062`, and a private local `PHOENIX_WORKING_DIR`, then `arize-phoenix serve`. This does not deploy an App.

Run `python eval/phoenix/create_dataset.py --dry-run`, then `python eval/phoenix/run_experiment.py --evidence-directory evaluation/<new-run>`. That directory must already contain the frozen standard harness from `eval/run.py prepare`. Each answer and its raw tool trace are saved once. Existing captures cause an error; never rerun a case because its score was low. Phoenix dataset/experiment IDs, server readback, exact comparisons and method hashes are saved beside the captures.

The XML, CSV and independent read-only verification traces live together under `eval/benchmark/datasets/mprint-v1/`. `datasets.yaml` records the mapping. Prompts are versioned. A single run on ten known questions does not establish general accuracy, comparative superiority, source completeness or clinical validity. No clinician adjudication is implied by exact matching of snapshot fields.
