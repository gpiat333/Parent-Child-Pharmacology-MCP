# Local quickstart

This is a GSA hackathon prototype, not an official NIH tool or a production-ready clinical service. Use public or synthetic questions only. See [security boundaries](SECURITY.md).

Install Python 3.13 and [uv](https://docs.astral.sh/uv/). From the repository root:

```sh
uv sync --locked --group dev
uv run --locked python main.py
```

The default transport is **stdio**, for an MCP client to launch as a subprocess. Configure the client with command `uv`, arguments `run --locked --directory /absolute/path/to/repository python main.py`, and its own absolute repository path. Do not send terminal prose into the JSON-RPC stream. The server exposes 31 tools, four prompts and four resources.

For loopback HTTP in PowerShell:

```powershell
$env:MCP_TRANSPORT='streamable-http'
$env:MCP_PORT='8000'
$env:USE_LAKEHOUSE='false'
uv run --locked python main.py
```

On a POSIX shell use `MCP_TRANSPORT=streamable-http MCP_PORT=8000 USE_LAKEHOUSE=false uv run --locked python main.py`. The MCP endpoint is `http://127.0.0.1:8000/mcp`; `/health` and `/version` are unauthenticated local liveness/version checks. Local HTTP has no authentication and must remain loopback. A hosted runtime needs an authenticated gateway and an explicit allowed hostname; the application does not supply user authentication itself.

Copy `.env.example` to `.env` if needed. Environment variables take precedence. Do not commit credentials. Public-source retrieval works without Databricks or a model. Set your NCBI contact email for live NCBI use. Bundled MPRINT snapshots are dated; semantic LactMed search explicitly returns not_enabled.

```sh
uv run --locked --group dev pytest tests -q
uv run --locked --group dev ruff check src tests main.py
uv run --locked --group dev ruff format --check src tests main.py
uv build
```

For chat evaluations and Databricks MLflow, see [eval/README.md](eval/README.md). Those tests require separately authorized model access and generate costs. Every client must enforce the preflight and required-display contracts. An arbitrary MCP client may not do so.


Remote HTTP now requires application-verified RS256 tokens and individual tool scopes in addition to platform access controls. See SECURITY.md and .env.example. Default stdio and optional loopback HTTP remain suitable for local public-data development. No new App deployment is included.
