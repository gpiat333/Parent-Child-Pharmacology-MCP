function Get-EvidenceUrls([string]$Text) {
    foreach ($match in [regex]::Matches($Text, 'https?://[^\s<>"''\\\[\]]+')) {
        $url = [System.Net.WebUtility]::HtmlDecode($match.Value).TrimEnd('.', ',', ';', ':')
        while ($url.EndsWith(')') -and ([regex]::Matches($url, '\)').Count -gt [regex]::Matches($url, '\(').Count)) { $url = $url.Substring(0, $url.Length - 1) }
        $url
    }
}

function Get-EvidenceStrings($Value) {
    if ($Value -is [string]) {
        $Value
        try { $parsed = ConvertFrom-Json -InputObject $Value -ErrorAction Stop; if ($parsed -isnot [string]) { Get-EvidenceStrings $parsed } } catch {}
    } elseif ($Value -is [System.Collections.IDictionary]) {
        foreach ($v in $Value.Values) { Get-EvidenceStrings $v }
    } elseif ($Value -is [System.Collections.IEnumerable]) {
        foreach ($v in $Value) { Get-EvidenceStrings $v }
    } elseif ($null -ne $Value -and $Value -is [pscustomobject]) {
        foreach ($p in $Value.PSObject.Properties) { Get-EvidenceStrings $p.Value }
    }
}

function New-EvidenceCitationCatalog($Calls) {
    $urls = @(foreach ($call in $Calls) { foreach ($s in (Get-EvidenceStrings $call.result)) { Get-EvidenceUrls $s } }) | Sort-Object -Unique
    $catalog = [ordered]@{}
    foreach ($url in $urls) { $catalog['S' + ($catalog.Count + 1)] = $url }
    return $catalog
}

function Resolve-EvidenceCitations([string]$Answer, $Catalog) {
    # IDs are expanded by code, so the model never has to transcribe long revision URLs.
    $resolved = [regex]::Replace($Answer, '\[\[source:(S\d+)\]\]', {
        param($m)
        $key = $m.Groups[1].Value
        if (-not $Catalog.Contains($key)) { throw "Unknown citation identifier: $key" }
        return '[' + $key + '](' + $Catalog[$key] + ')'
    })
    if ($resolved -match '\[\[source:') { throw 'Malformed citation identifier.' }
    $allowed = @($Catalog.Values | ForEach-Object { $_.TrimEnd('/') })
    foreach ($url in (Get-EvidenceUrls $resolved)) {
        if ($url.TrimEnd('/') -cnotin $allowed) { throw 'Answer contains a URL absent from retrieved evidence.' }
    }
    return $resolved
}

function Resolve-EvidenceCitationsWithRepair([string]$Answer, $Catalog, [scriptblock]$Repair) {
    try {
        return @{answer=(Resolve-EvidenceCitations $Answer $Catalog);repair_attempted=$false}
    } catch {
        # One bounded repair; the original allowlist is never expanded or bypassed.
        $candidate = & $Repair $Answer
        if (-not $candidate) { throw 'Citation repair returned no answer.' }
        return @{answer=(Resolve-EvidenceCitations ([string]$candidate) $Catalog);repair_attempted=$true}
    }
}
