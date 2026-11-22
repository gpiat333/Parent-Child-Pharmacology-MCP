. (Join-Path $PSScriptRoot 'portfolio-display.ps1')
. (Join-Path $PSScriptRoot 'axis-display.ps1')
$script:AnswerNoticePolicy = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) 'src/parent_child_pharmacology/core/output_notices.json') | ConvertFrom-Json

function Get-AbstractCoverageNotice([object[]]$ToolCalls) {
    $states = [ordered]@{}
    $searchFailed = $false
    $seen = $false
    $fields = @('with_abstract_pmids','without_abstract_pmids','unreturned_pmids','failed_pmids')
    foreach ($call in $ToolCalls) {
        if ($call.tool -cnotin @('get_abstracts','medication_evidence_brief')) { continue }
        $result = $call.result
        if ($result.structuredContent) { $result = $result.structuredContent }
        elseif ($result.content) {
            foreach ($item in $result.content) {
                if ($item.type -ceq 'text') {
                    try { $parsed = $item.text | ConvertFrom-Json -ErrorAction Stop } catch { continue }
                    if ($parsed -is [pscustomobject]) { $result = $parsed; break }
                }
            }
        }
        if ($result.allow_research -ceq $false -or $result.requires_confirmation) { continue }
        $block = $result.abstract_coverage
        if (-not $block) { continue }
        if ($block.schema_version -ne 1) { throw 'Unsupported abstract coverage schema' }
        if ($block.requested_pmids -isnot [array]) { throw 'Invalid abstract coverage PMIDs' }
        $requested = @($block.requested_pmids)
        foreach ($pmid in $requested) {
            if ($pmid -isnot [string] -or $pmid -cnotmatch '^[1-9][0-9]{0,9}$') { throw 'Invalid abstract coverage PMIDs' }
        }
        $flattened = @()
        foreach ($field in $fields) {
            if ($block.$field -isnot [array]) { throw 'Invalid abstract coverage group' }
            foreach ($pmid in $block.$field) {
                if ($pmid -cnotin $requested -or $pmid -cin $flattened) { throw 'Invalid abstract coverage group' }
                $flattened += $pmid
                $states[$pmid] = $field
            }
        }
        if (@($requested | Select-Object -Unique).Count -ne $flattened.Count) { throw 'Abstract coverage groups must partition requested PMIDs' }
        $searchFailed = $searchFailed -or $block.search_failed -ceq $true
        $seen = $true
    }
    if (-not $seen) { return }
    $groups = @{}
    foreach ($field in $fields) { $groups[$field] = @($states.Keys | Where-Object { $states[$_] -ceq $field }) }
    if ($states.Count -gt 0 -and $groups.with_abstract_pmids.Count -eq $states.Count -and -not $searchFailed) { return }
    $templates = $script:AnswerNoticePolicy.abstract_coverage
    $parts = @()
    if ($states.Count) {
        $parts += $templates.counts.Replace('{found}',[string]$groups.with_abstract_pmids.Count).Replace('{requested}',[string]$states.Count)
        foreach ($field in $fields[1..3]) {
            if ($groups[$field].Count) { $parts += $templates.$field.Replace('{ids}',($groups[$field] -join ', ')) }
        }
    } elseif (-not $searchFailed) { $parts += $templates.no_records }
    if ($searchFailed) { $parts += $templates.search_failed }
    $parts += $templates.limit
    [pscustomobject]@{id='pubmed_abstract_coverage';text=($parts -join ' ');origin='Application retrieval-coverage contract; not a source finding';display_required=$true}
}

function Get-RequiredAnswerNotices([string[]]$ToolNames, [switch]$Blocked, [object[]]$ToolCalls=@()) {
    if ($Blocked) { return @() }
    foreach ($notice in $script:AnswerNoticePolicy.notices) {
        if (@($ToolNames | Where-Object { $_ -cin $notice.tools }).Count) {
            [pscustomobject]@{id=$notice.id;text=$notice.text;origin=$script:AnswerNoticePolicy.origin;display_required=$true}
        }
    }
    Get-AbstractCoverageNotice $ToolCalls
    Get-AxisDisplayNotice $ToolCalls
    Get-PortfolioFilterNotice $ToolCalls
}

function Add-RequiredAnswerNotices([string]$Answer, $Notices) {
    $lines = @($Answer -split '\r?\n' | ForEach-Object { $_.Trim() })
    $missing = @($Notices | Where-Object { if($_.text.Contains("`n")){ -not ("`n"+$Answer.Trim()+"`n").Contains("`n"+$_.text+"`n") } else { $_.text -cnotin $lines } } | ForEach-Object { $_.text })
    if ($missing.Count) { return $Answer.TrimEnd() + "`n`nApplication limits:`n" + ($missing -join "`n") }
    return $Answer
}
