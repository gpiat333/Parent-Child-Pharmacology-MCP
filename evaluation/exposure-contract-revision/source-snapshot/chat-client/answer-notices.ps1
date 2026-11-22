$script:AnswerNoticePolicy = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) 'server/core/output_notices.json') | ConvertFrom-Json

function Get-RequiredAnswerNotices([string[]]$ToolNames, [switch]$Blocked) {
    if ($Blocked) { return @() }
    foreach ($notice in $script:AnswerNoticePolicy.notices) {
        if (@($ToolNames | Where-Object { $_ -cin $notice.tools }).Count) {
            [pscustomobject]@{id=$notice.id;text=$notice.text;origin=$script:AnswerNoticePolicy.origin;display_required=$true}
        }
    }
}

function Add-RequiredAnswerNotices([string]$Answer, $Notices) {
    $lines = @($Answer -split '\r?\n' | ForEach-Object { $_.Trim() })
    $missing = @($Notices | Where-Object { $_.text -cnotin $lines } | ForEach-Object { $_.text })
    if ($missing.Count) { return $Answer.TrimEnd() + "`n`nApplication limits:`n" + ($missing -join "`n") }
    return $Answer
}
