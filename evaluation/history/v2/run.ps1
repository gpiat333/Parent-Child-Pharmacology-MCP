param()
$ErrorActionPreference='Stop'
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'gold-questions.json') | ConvertFrom-Json
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
foreach ($case in $cases) {
 & (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -PromptMode production -OutputPrefix ('gold-v2-production-'+$case.id) | Out-Null
 Write-Host ('Completed v2 '+$case.id)
}
foreach ($repeat in 2..3) {
 $case=$cases | Where-Object id -eq 'G06'
 & (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -PromptMode production -OutputPrefix ('gold-v2-timeline-r'+$repeat) | Out-Null
 Write-Host ('Completed timeline repeat '+$repeat)
}
