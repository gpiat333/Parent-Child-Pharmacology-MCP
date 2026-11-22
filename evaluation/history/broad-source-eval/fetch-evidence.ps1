param(
    [string]$CliPath = 'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe',
    [string]$Profile = 'gsa-mcp-hackathon'
)
$ErrorActionPreference = 'Stop'
$endpoint = 'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp'
$token = & $CliPath auth token --profile $Profile --output json | ConvertFrom-Json
if (-not $token.access_token) { throw 'Sign in to the Databricks CLI first.' }
$headers = @{ Authorization = 'Bearer ' + $token.access_token; Accept = 'application/json, text/event-stream' }
$script:requestId = 0
$results = [System.Collections.Generic.List[object]]::new()
function Invoke-Mcp($method, $parameters, [switch]$Notification) {
    $payload = @{jsonrpc='2.0';method=$method;params=$parameters}
    if (-not $Notification) { $script:requestId++; $payload.id = $script:requestId }
    $response = Invoke-RestMethod -Uri $endpoint -Method Post -Headers $headers -ContentType 'application/json' -Body ($payload | ConvertTo-Json -Depth 30 -Compress) -TimeoutSec 180
    if ($response.error) { throw ('MCP protocol error ' + $response.error.code) }
    return $response.result
}
function Test-Tool($name, $arguments) {
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-Mcp 'tools/call' @{name=$name;arguments=$arguments}
    $body = ($response.content | Where-Object type -eq text | Select-Object -First 1).text | ConvertFrom-Json
    $nestedErrors = @()
    foreach ($property in $body.PSObject.Properties) {
        if ($property.Value -is [pscustomobject] -and $property.Value.error) { $nestedErrors += $property.Name }
    }
    $ok = -not $response.isError -and -not $body.error -and $nestedErrors.Count -eq 0 -and [bool]$body.disclaimer
    $row = [pscustomobject]@{tool=$name;arguments=$arguments;passed=$ok;latency_ms=$timer.ElapsedMilliseconds;isError=[bool]$response.isError;nested_error_sections=$nestedErrors;response=$body}
    $results.Add($row)
    Write-Host "$name : passed=$ok, $($timer.ElapsedMilliseconds) ms, source=$($body.source), nestedErrors=$($nestedErrors -join ',')"
    return $body
}
try {
    $init = Invoke-Mcp 'initialize' @{protocolVersion='2025-03-26';capabilities=@{};clientInfo=@{name='mc-windows-smoke';version='1.0'}}
    $headers['MCP-Protocol-Version'] = $init.protocolVersion
    Invoke-Mcp 'notifications/initialized' @{} -Notification | Out-Null
    $tools = Invoke-Mcp 'tools/list' @{}
    $prompts = Invoke-Mcp 'prompts/list' @{}
    $resources = Invoke-Mcp 'resources/list' @{}
    Write-Host "Connected: $($tools.tools.Count) tools; $($prompts.prompts.Count) prompts; $($resources.resources.Count) resources."
    $evidence=@{}
    $evidence['pubmed_known']=Test-Tool 'get_abstracts' @{pmids=@('38841362','30116895','39626074','38811474')}
    $queries=@('metformin pregnancy','lamotrigine breastfeeding','levetiracetam breastfeeding','ibuprofen breastfeeding')
    for ($i=0;$i -lt $queries.Count;$i++) {
        $hit=Test-Tool 'search_literature' @{query=$queries[$i];population='any';max_results=2;mode='keyword'}
        $evidence['pubmed_search_'+$i]=$hit
        if ($hit.results.Count -gt 0) { $evidence['pubmed_abstract_'+$i]=Test-Tool 'get_abstracts' @{pmids=@([string]$hit.results[0].pmid)} }
    }
    $queries=@('sertraline postpartum','metformin gestational diabetes','levetiracetam pregnancy','lamotrigine pregnancy','ibuprofen pediatric','adalimumab pediatric','fluoxetine adolescent','lithium pregnancy')
    for ($i=0;$i -lt $queries.Count;$i++) { $evidence['trial_'+$i]=Test-Tool 'search_trials' @{condition_or_drug=$queries[$i];population='any';max_results=2} }
    $evidence['gold_sertraline']=Test-Tool 'search_mprint_gold' @{drug='sertraline';max_results=3}
    $evidence['gold_outcome']=Test-Tool 'get_mprint_gold_outcomes' @{pmid='551926';kind='PE_CT';max_results=2}
    $evidence['old_abstract']=Test-Tool 'get_abstracts' @{pmids=@('551926')}
    $evidence['augmentin']=Test-Tool 'normalize_drug' @{name='Augmentin'}
    $evidence['label_fluoxetine']=Test-Tool 'search_pediatric_labeling_changes' @{drug='fluoxetine';max_results=2}
    $hit=Test-Tool 'search_lactmed' @{drug='sertraline';max_results=1}
    $evidence['lactmed_search']=$hit
    if ($hit.results.Count -gt 0) { $evidence['lactmed_record']=Test-Tool 'get_lactmed_record' @{book_id=[string]$hit.results[0].id;max_chars=20000} }
    $evidence['empty_pubmed']=Test-Tool 'search_literature' @{query='notarealdrugxyz';population='any';max_results=2;mode='keyword'}
    $evidence['faers']=Test-Tool 'get_adverse_event_signals' @{drug='ibuprofen';cohort='infant';max_results=3}
    $evidence['unknown_drug']=Test-Tool 'normalize_drug' @{name='notarealdrugxyz'}
    $evidence | ConvertTo-Json -Depth 70 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'evidence.json') -Encoding utf8
} finally { $headers.Clear(); $token=$null }
