# Isolated Databricks unit tests

`submit-tests.py` uploads a frozen source/test archive to a **new** workspace directory and submits a one-time serverless notebook. It does not deploy or modify an App, change permissions, or schedule monitoring. The archive includes public MPRINT snapshots and the two saved public regression fixtures required by the tests. Workspace files are split below the API upload limit and reassembled only after upload; SHA-256 binds the notebook to the archive.

Configure `DATABRICKS_CONFIG_PROFILE` and optionally `DATABRICKS_CLI_PATH`, then run from the repository root:

```sh
uv run python eval/databricks/submit-tests.py --workspace-dir /Users/your-workspace-user/mcp-tests-unique-run --output evaluation/my-new-notebook-run
```

The notebook creates an ephemeral Python 3.13 environment from `uv.lock`. It installs checksum-pinned PowerShell 7.7.0 for client parity tests on Linux ARM64 or x64. Network access to the official Python, PyPI and Microsoft/GitHub release endpoints is required. No token is written to source or artifacts. Test execution may incur compute charges.

Inspect the returned Jobs run, retrieve its task output, and verify `returncode == 0` and zero failures/errors/skips. A job state alone is insufficient evidence for archived older notebook attempts. Current receipts include all attempts and explicitly distinguish setup failures from the final successful test run. Keep the workspace directory restricted and follow your retention policy; the utility does not change ACLs or delete evidence automatically.
