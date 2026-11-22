$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'gold-questions.json') | ConvertFrom-Json
foreach ($i in 1..3) {
 $case=$cases | Where-Object id -eq 'G06'
 & (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -OutputPrefix ('gold-v2-final-timeline-r'+$i) | Out-Null
 Write-Host ('Final timeline '+$i+' completed')
}
$case=$cases | Where-Object id -eq 'G07'
& (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -OutputPrefix 'gold-v2-final-G07' | Out-Null
