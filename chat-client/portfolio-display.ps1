function Get-PortfolioFilterNotice([object[]]$ToolCalls) {
    $blocks=[System.Collections.Generic.List[string]]::new()
    $templates=$script:AnswerNoticePolicy.portfolio_filters
    foreach($call in $ToolCalls) {
        if($call.tool -cnotin @('search_funded_research','summarize_research_portfolio')){continue}
        $result=$call.result
        if($result.isError){continue}
        if($result.structuredContent){$result=$result.structuredContent}
        elseif($result.content){
            foreach($item in $result.content){
                if($item.type -ceq 'text'){
                    try{$parsed=$item.text | ConvertFrom-Json -ErrorAction Stop}catch{continue}
                    if($parsed -is [pscustomobject]){$result=$parsed;break}
                }
            }
        }
        if($result.error -or $result.allow_research -ceq $false -or $result.requires_confirmation){continue}
        if($result.query_criteria -isnot [pscustomobject] -and $result.query_criteria -isnot [System.Collections.IDictionary]){$block=$templates.missing}
        else {
            $data=ConvertTo-Json -InputObject $result.query_criteria -Depth 30 -Compress
            if($data.Length -gt $templates.max_chars){$block=$templates.oversized}
            else{$block='```json'+"`n"+$data+"`n"+'```'}
        }
        $blocks.Add(('Query '+($blocks.Count+1)+' ('+$call.tool+")`n"+$block))
    }
    if($blocks.Count){[pscustomobject]@{id='reporter_query_filters';text=($templates.title+"`n"+($blocks -join "`n"));origin='Application display of source query metadata; not a research finding';display_required=$true}}
}
