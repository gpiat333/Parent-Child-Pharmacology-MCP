# Gateway bridge uses the OS HTTPS trust store. Credentials stay in this process.
param([string]$Profile=$env:DATABRICKS_CONFIG_PROFILE,[string]$ResponsePath)
$ErrorActionPreference='Stop'
$cli=if($env:DATABRICKS_CLI_PATH){$env:DATABRICKS_CLI_PATH}else{'databricks'}
try {
    $workspace=$env:DATABRICKS_HOST
    $target=[uri]$workspace
    if (-not $Profile -or $target.Scheme -ne 'https' -or $target.UserInfo -or $target.Query -or $target.Fragment -or $target.AbsolutePath -ne '/') { throw 'Invalid configured Databricks workspace/profile.' }
    $requestText=[Console]::In.ReadToEnd()
    $auth=& $cli auth token --profile $Profile --output json 2>$null | ConvertFrom-Json
    if (-not $auth.access_token) { throw 'Databricks authentication unavailable' }
    $headers=@{Authorization='Bearer '+$auth.access_token;Accept='application/json'}
    $response=Invoke-RestMethod -Uri ($workspace.TrimEnd('/')+'/ai-gateway/mlflow/v1/chat/completions') -Method Post -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($requestText)) -MaximumRedirection 0 -TimeoutSec 180
    $responseJson=$response | ConvertTo-Json -Depth 80 -Compress
    if ($ResponsePath) { [IO.File]::WriteAllText($ResponsePath,$responseJson,[Text.UTF8Encoding]::new($false)) }
    else { [Console]::Out.WriteLine($responseJson) }
} catch {
    $errorRecord=@{gateway_error=$true;exception_type=$_.Exception.GetType().Name;http_status=if($_.Exception.Response){[int]$_.Exception.Response.StatusCode}else{$null};expired_credential=($_.ErrorDetails.Message -match 'expired_secret_key')}
    $errorJson=$errorRecord | ConvertTo-Json -Compress
    if ($ResponsePath) { [IO.File]::WriteAllText($ResponsePath,$errorJson,[Text.UTF8Encoding]::new($false)) }
    else { [Console]::Out.WriteLine($errorJson) }
    exit 1
} finally {
    if ($headers) {$headers.Clear()}
    $auth=$null
}
