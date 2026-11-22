param([int]$Shard=0)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
for ($i=$Shard; $i -lt $cases.Count; $i+=2) {
 $c=$cases[$i]
 try { & (Join-Path $root 'test-mcp-chat.ps1') -Question $c.question -OutputPrefix ('case-report-'+$c.id) | Out-Null; Write-Host ('Completed '+$c.id) }
 catch { Write-Host ('Failed '+$c.id+': '+$_.Exception.GetType().Name) }
}
