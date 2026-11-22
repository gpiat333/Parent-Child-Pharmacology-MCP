param([switch]$Test)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
 if (-not (Test-Path '.venv/Scripts/python.exe')) { python -m venv .venv; if ($LASTEXITCODE) { throw 'venv failed' } }
 & .venv/Scripts/python.exe -m pip install -r requirements.lock
 if ($LASTEXITCODE) { throw 'Dependency installation failed' }
 $env:USE_LAKEHOUSE='false'
 if ($Test) { & .venv/Scripts/python.exe -m pytest tests -q } else { & .venv/Scripts/python.exe server.py }
 if ($LASTEXITCODE) { throw 'Run failed' }
} finally { Pop-Location }
