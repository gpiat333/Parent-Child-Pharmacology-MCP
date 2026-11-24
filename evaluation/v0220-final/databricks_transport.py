"""Evaluation-only local transport and pinned existing Databricks authentication."""
import json,ssl,subprocess,os
from urllib.parse import urlsplit
import httpx
import truststore

ENDPOINT=os.environ.get('DATABRICKS_MCP_ENDPOINT','')
HOST=os.environ.get('DATABRICKS_HOST','').rstrip('/')
CLI=os.environ.get('DATABRICKS_CLI_PATH','databricks')
PROFILE=os.environ.get('DATABRICKS_CONFIG_PROFILE','')

def oauth_token():
    if not PROFILE:raise ValueError('DATABRICKS_CONFIG_PROFILE required')
    result=subprocess.run([CLI,'auth','token','--profile',PROFILE,'--output','json'],capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError('Existing Databricks CLI authentication unavailable')
    token=json.loads(result.stdout).get('access_token')
    if not token:raise RuntimeError('Databricks OAuth token unavailable')
    return token

def make_mcp_client(endpoint):
    target=urlsplit(endpoint)
    if target.username or target.password or target.query or target.fragment or target.path!='/mcp':
        raise ValueError('Invalid MCP endpoint')
    if target.hostname in {'127.0.0.1','localhost','::1'} and target.scheme=='http':
        return httpx.Client(timeout=180,trust_env=False,follow_redirects=False,headers={'Accept':'application/json, text/event-stream'})
    if target.scheme!='https' or endpoint!=ENDPOINT:raise ValueError('Credential destination is not the authorized MCP app')
    return httpx.Client(timeout=180,trust_env=False,follow_redirects=False,
        verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
        headers={'Accept':'application/json, text/event-stream','Authorization':'Bearer '+oauth_token()})
