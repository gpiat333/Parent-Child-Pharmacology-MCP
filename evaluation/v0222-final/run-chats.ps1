param([string]$Model=$env:AGENT_MODEL,[string]$Endpoint=$env:MCP_EVAL_ENDPOINT)
$ErrorActionPreference='Stop'
$packageRoot=$env:MCP_REPO_ROOT
if (-not $packageRoot -or -not $Model -or -not $Endpoint) { throw 'Run via eval/run.py with configured model and endpoint.' }
$clientPath=Join-Path $packageRoot 'chat-client/test-mcp-chat.ps1'
$outputPath=Join-Path $PSScriptRoot 'chats'
[System.IO.Directory]::CreateDirectory($outputPath) | Out-Null
$cases=Get-Content -Raw (Join-Path $PSScriptRoot 'cases.json') | ConvertFrom-Json
$cases | ForEach-Object -Parallel {
    $case=$_
    $existing=Join-Path $using:outputPath ($case.id+'-results.json')
    if ((Test-Path -LiteralPath $existing) -and (Get-Content -LiteralPath $existing -Raw | ConvertFrom-Json).completed) {
        Write-Output ($case.id+': retained completed current-run answer')
        return
    }
    try {
        & $using:clientPath -Question $case.question -Model $using:Model -McpEndpoint $using:Endpoint -OutputDirectory $using:outputPath -OutputPrefix $case.id -ToolProfile full -SaveTrace | Out-Null
        Write-Output ($case.id+': completed'); Start-Sleep -Seconds 2
    } catch {
        Write-Output ($case.id+': '+$_.Exception.GetType().Name)
    }
} -ThrottleLimit 1
