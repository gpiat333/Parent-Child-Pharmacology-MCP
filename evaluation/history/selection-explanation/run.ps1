param([int]$Shard=0)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
$results=@()
for($i=$Shard;$i -lt $cases.Count;$i+=2){
 $c=$cases[$i]
 $profiles=if($i%2 -eq 0){@('full','parent')}else{@('parent','full')}
 foreach($profile in $profiles){
  $prefix='selection-'+$profile+'-'+$c.id
  try {
   & (Join-Path $root 'test-mcp-chat.ps1') -Question $c.question -ToolProfile $profile -OutputPrefix $prefix -SaveTrace | Out-Null
   $d=Get-Content -Raw (Join-Path $root ('presentation-evidence/'+$prefix+'-results.json')) | ConvertFrom-Json
   $results+=@{id=$c.id;profile=$profile;completed=$d.completed;blocked=$d.policy_blocked;calls=$d.tool_calls.Count}
  }catch{$results+=@{id=$c.id;profile=$profile;completed=$false;error_type=$_.Exception.GetType().Name}}
  $results | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot ('execution-'+$Shard+'.json'))
  Write-Host ($prefix+': '+$results[-1].completed)
 }
}
