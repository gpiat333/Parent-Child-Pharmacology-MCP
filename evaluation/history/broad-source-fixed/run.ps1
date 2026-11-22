param([int]$Shard=0)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
for ($i=$Shard; $i -lt $cases.Count; $i+=2) {
    $case=$cases[$i]
    try { & (Join-Path $root 'test-mcp-chat.ps1') -Question $case.question -OutputPrefix ('broad-fixed-'+$case.id) | Out-Null; Write-Host ('Finished '+$case.id) }
    catch { Write-Host ('Failed '+$case.id+': '+$_.Exception.GetType().Name) }
}
