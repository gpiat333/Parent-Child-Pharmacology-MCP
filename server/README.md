# Compatibility launchers and historical ingestion utilities

Current application code is in `../src/parent_child_pharmacology`; tests are in `../tests`. Run from the repository root using [QUICKSTART.md](../QUICKSTART.md). `server.py` and `app_start.py` remain thin compatibility wrappers. The `requirements.lock` is the runtime pin list used by the root Dockerfile; `uv.lock` is the canonical complete project lock.

The ingestion/vector-index scripts are optional historical infrastructure utilities, not required for local snapshot mode and not executed by tests or CI. Review their configuration and permissions before using them. The vector search tool returns `not_enabled` when inactive. Deployment guidance is in `../deploy/databricks/README.md`; no deployment is triggered by installation or CI.
