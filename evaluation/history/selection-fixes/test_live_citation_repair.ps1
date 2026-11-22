$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
. (Join-Path $root 'citation-output.ps1')
$d=Get-Content -Raw (Join-Path $root 'presentation-evidence/selection-fix-parent-E03-results.json') | ConvertFrom-Json
$catalog=New-EvidenceCitationCatalog $d.tool_calls
$cli='C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'
$token=& $cli auth token --profile gsa-mcp-hackathon --output json | ConvertFrom-Json
$headers=@{Authorization='Bearer '+$token.access_token;Accept='application/json'}
try{
 $r=Resolve-EvidenceCitationsWithRepair 'FDA pregnancy registry directory: https://example.invalid/invented-registry' $catalog {
  param($invalid)
  $payload=@{model='models.ai.gpt-5-6-luna';max_tokens=300;reasoning_effort='low';messages=@(@{role='system';content='Repair only the citation. Return the label FDA pregnancy registry directory followed by the matching [[source:Snumber]] ID from this catalog. No literal URLs, additional facts or invented IDs. Catalog: '+($catalog|ConvertTo-Json -Compress)},@{role='user';content=$invalid})}
  $out=Invoke-RestMethod -Uri 'https://dbc-aae0ba16-8727.cloud.databricks.com/ai-gateway/mlflow/v1/chat/completions' -Method Post -Headers $headers -ContentType 'application/json' -Body ($payload|ConvertTo-Json -Depth 12) -TimeoutSec 180
  $out.choices[0].message.content
 }
 @{passed=($r.repair_attempted -and $r.answer -match 'www.fda.gov/consumers/pregnancy-exposure-registries/list-pregnancy-exposure-registries');repair_attempted=$r.repair_attempted;answer=$r.answer;fixture='Deliberately corrupted synthetic citation; source catalog from saved registry lookup'}|ConvertTo-Json|Set-Content (Join-Path $PSScriptRoot 'citation-live-repair.json')
 Write-Host 'Live citation repair completed'
}finally{$headers.Clear();$token=$null}
