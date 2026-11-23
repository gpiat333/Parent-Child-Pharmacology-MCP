$script:AxisDisplayPolicy = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) 'src/parent_child_pharmacology/core/axis_display.json') | ConvertFrom-Json
function Get-AxisDisplayNotice([object[]]$ToolCalls) {
 $latest=[ordered]@{}
 foreach($call in $ToolCalls) {
  if($call.tool -cne 'medication_evidence_brief'){continue}
  $result=$call.result
  if($result.structuredContent){$result=$result.structuredContent}
  elseif($result.content){foreach($block in $result.content){if($block.type -ceq 'text'){try{$decoded=$block.text|ConvertFrom-Json -ErrorAction Stop;if($decoded -is [pscustomobject]){$result=$decoded;break}}catch{}}}}
  if($result.error -or $result.allow_research -ceq $false -or $result.requires_confirmation){continue}
  $key=if($result.drug_input){[string]$result.drug_input}else{'brief'}
  $latest[$key]=$result
 }
 if(-not $latest.Count){return}
 $lines=[System.Collections.Generic.List[string]]::new();$lines.Add($script:AxisDisplayPolicy.title);$index=0
 foreach($result in $latest.Values){
  $index++;if($latest.Count -gt 1){$lines.Add("Brief $index")}
  $lines.Add('| Evidence axis | Extracted findings | Context-only passages | Gap statements |');$lines.Add('|---|---|---:|---:|')
  $axisMap=if($result.axis_set -ceq 'pediatric'){$script:AxisDisplayPolicy.pediatric_axes}else{$script:AxisDisplayPolicy.axes}
  foreach($property in $axisMap.psobject.Properties){
   $rows=@($result.evidence_axes | Where-Object {$_.axis -ceq $property.Name});$valid=$rows.Count -eq 1 -and $rows[0].by_ingredient -is [array] -and $rows[0].by_ingredient.Count -gt 0
   $counts=@{items=0;context_only=0;reported_gaps=0}
   if($valid){foreach($group in $rows[0].by_ingredient){foreach($field in @('items','context_only','reported_gaps')){if($group.$field -isnot [array]){$valid=$false}else{$total=$group."$($field)_total";$counts[$field]+=$(if($total -is [int] -or $total -is [long]){[int]$total}else{$group.$field.Count})}}}}
   if($valid){$status=if($counts.items){$script:AxisDisplayPolicy.found.Replace('{n}',[string]$counts.items)}else{$script:AxisDisplayPolicy.empty};$context=[string]$counts.context_only;$gaps=[string]$counts.reported_gaps}
   else{$status=$script:AxisDisplayPolicy.missing;$context='unknown';$gaps='unknown'}
   $lines.Add('| '+$property.Value+' | '+$status+' | '+$context+' | '+$gaps+' |')
  }
 }
 $lines.Add($script:AxisDisplayPolicy.note)
 [pscustomobject]@{id='three_axis_inventory';text=($lines -join "`n");origin='Application structural retrieval inventory; not clinical findings';display_required=$true}
}
