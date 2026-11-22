. (Join-Path $PSScriptRoot '../../parent-chat-policy.ps1')
if(Test-TraceCaptureAllowed $null){throw 'Preflight failure must not save a trace'}
if(Test-TraceCaptureAllowed @{}){throw 'Missing route must not save a trace'}
if(Test-TraceCaptureAllowed @{route='privacy'}){throw 'Privacy route must not save a trace'}
if(-not(Test-TraceCaptureAllowed @{route='evidence'})){throw 'Synthetic evidence traces must remain available'}
'4 trace-capture checks passed.'
