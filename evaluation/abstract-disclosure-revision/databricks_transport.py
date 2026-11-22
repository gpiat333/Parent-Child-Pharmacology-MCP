"""Evaluation-only local transport and pinned existing Databricks authentication."""
import json,ssl,subprocess
import httpx
import truststore

ENDPOINT='https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp'
HOST='https://dbc-aae0ba16-8727.cloud.databricks.com'
CLI=r'C:/Users/piatkowskigs/Downloads/databricks_cli_1.26.0_windows_amd64/databricks.exe'

def oauth_token():
    result=subprocess.run([CLI,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError('Existing Databricks CLI authentication unavailable')
    token=json.loads(result.stdout).get('access_token')
    if not token:raise RuntimeError('Databricks OAuth token unavailable')
    return token

def make_mcp_client(endpoint):
    if endpoint=='http://127.0.0.1:8770/mcp':
        return httpx.Client(timeout=180,trust_env=False,follow_redirects=False,headers={'Accept':'application/json, text/event-stream'})
    if endpoint!=ENDPOINT:raise ValueError('Credential destination is not the authorized MCP app')
    return httpx.Client(timeout=180,trust_env=False,follow_redirects=False,
        verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
        headers={'Accept':'application/json, text/event-stream','Authorization':'Bearer '+oauth_token()})
