param([int]$Shard=0)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
$results=@()
for($i=$Shard;$i -lt $cases.Count;$i+=2){
 $c=$cases[$i];$prefix='population-deadline-final-full-'+$c.id
 try {
  & (Join-Path $root 'test-mcp-chat.ps1') -Question $c.question -ToolProfile full -OutputPrefix $prefix -SaveTrace | Out-Null
  $d=Get-Content -Raw (Join-Path $root ('presentation-evidence/'+$prefix+'-results.json')) | ConvertFrom-Json
  $results+=@{id=$c.id;completed=$d.completed;blocked=$d.policy_blocked;repair=$d.citation_repair_attempted;calls=$d.tool_calls.Count}
 }catch{$results+=@{id=$c.id;completed=$false;error_type=$_.Exception.GetType().Name}}
 $results | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot ('execution-'+$Shard+'.json'))
 Write-Host ($prefix+': '+$results[-1].completed)
}


