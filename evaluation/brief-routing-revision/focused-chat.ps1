$ErrorActionPreference='Stop'
$packageDir='C:\Users\piatkowskigs\Desktop\Parent-child Pharmacology MCP - Submission - 2026-11-20'
$runDir=Join-Path $packageDir 'evaluation\brief-routing-revision'
$case=Get-Content -LiteralPath (Join-Path $runDir 'cases.json') -Raw | ConvertFrom-Json | Where-Object {$_.id -eq 'E01-gap'}
& (Join-Path $packageDir 'chat-client\test-mcp-chat.ps1') -Question $case.question -McpEndpoint 'http://127.0.0.1:18080/mcp' -OutputDirectory (Join-Path $runDir 'chats') -OutputPrefix $case.id -ToolProfile full -SaveTrace | Out-Null
$result=Get-Content -LiteralPath (Join-Path $runDir 'chats\E01-gap-results.json') -Raw | ConvertFrom-Json
if (-not $result.completed -or $result.tool_calls[0].tool -ne 'medication_evidence_brief') { throw 'Focused composite workflow failed' }
[ordered]@{case=$case.id;completed=$result.completed;first_tool=$result.tool_calls[0].tool;tools=@($result.tool_calls.tool);workflow=$result.requested_workflow} | ConvertTo-Json -Depth 5
