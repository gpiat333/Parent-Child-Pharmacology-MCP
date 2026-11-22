$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
foreach ($case in $cases) { & (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -OutputPrefix ('broad-routing-'+$case.id) | Out-Null; Write-Host ('Finished '+$case.id) }
