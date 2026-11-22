param([string]$Model='system.ai.gpt-5-6-luna',[string]$Endpoint='http://127.0.0.1:18080/mcp')
$ErrorActionPreference='Stop'
$packageRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
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
        Write-Output ($case.id+': completed'); Start-Sleep -Seconds 8
    } catch {
        Write-Output ($case.id+': '+$_.Exception.GetType().Name)
    }
} -ThrottleLimit 1
