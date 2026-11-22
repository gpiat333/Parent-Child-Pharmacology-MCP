function Test-TraceCaptureAllowed($Decision) {
    return [bool]($Decision -and $Decision.route -and $Decision.route -ne 'privacy')
}

function ConvertFrom-McpEvidence($Result) {
    if ($Result.structuredContent) { return $Result.structuredContent }
    foreach ($item in $Result.content) {
        if ($item.type -eq 'text') {
            try { return ($item.text | ConvertFrom-Json -ErrorAction Stop) } catch {}
        }
    }
    throw 'MCP policy response could not be read; research stopped.'
}

function Get-ParentPolicyDecision($Result) {
    $data = ConvertFrom-McpEvidence $Result
    if ($null -eq $data.allow_research) { throw 'MCP policy response has no routing decision; research stopped.' }
    return $data
}

function Format-ParentPolicyMessage($Decision) {
    $text = [string]$Decision.message
    if (-not $text) { throw 'MCP policy response has no message; research stopped.' }
    foreach ($url in $Decision.source_urls) { $text += "`nSource: $url" }
    return $text
}

function Get-EvidenceStopMessage($Result) {
    $data = ConvertFrom-McpEvidence $Result
    if ($data.allow_research -eq $false -and $data.message) { return (Format-ParentPolicyMessage $data) }
    if ($data.requires_confirmation -or $data.safety.requires_identity_confirmation) {
        return 'The medicine identity or product needs confirmation. Please verify the exact name, ingredients and formulation with a pharmacist before continuing. No safety conclusion can be drawn from this tentative match.'
    }
    if ($data.allow_research -eq $false) {
        return 'This request cannot be continued as an evidence lookup. Remove identifying details and ask a general research question; personal treatment decisions belong with your clinician or pharmacist.'
    }
    if ($data.error) {
        return 'The requested source could not be retrieved or the input could not be verified. This does not establish safety or absence of evidence. Consult the original resource or a pharmacist; I cannot fill the gap from memory.'
    }
    return $null
}

function Test-ParentAnswerViolation([string]$Answer) {
    # Narrow output checks supplement, but do not replace, source review.
    $patterns = @(
        '(?i)\byou should (?:take|stop taking|start taking|increase|decrease|switch)\b',
        '(?i)\bgive your (?:baby|child|infant)\b.{0,45}\b\d+(?:\.\d+)?\s*(?:mg|mcg|ml)\b',
        '(?i)\byou (?:are|definitely are) eligible (?:for|to join)\b',
        '(?i)\byour (?:bottle|medicine|medication|product) is (?:definitely )?(?:safe|not recalled|unaffected)\b'
    )
    foreach ($pattern in $patterns) { if ($Answer -match $pattern) { return $true } }
    return $false
}
