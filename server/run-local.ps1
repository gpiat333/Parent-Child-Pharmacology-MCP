param([switch]$Test)
$ErrorActionPreference='Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  if ($Test) { uv run --locked --group dev pytest tests -q }
  else { $env:MCP_TRANSPORT='streamable-http'; $env:USE_LAKEHOUSE='false'; uv run --locked python main.py }
  if ($LASTEXITCODE) { throw 'Run failed' }
} finally { Pop-Location }
