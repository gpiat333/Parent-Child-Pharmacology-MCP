"""Parent-child Pharmacology MCP: thin app entry point."""
import os
import logging
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from core import config as cfg
from core.audit import LibraryPrivacyFilter
from tools import register
# Compatibility module aliases for existing clients/tests.
import clients as src
from clients import lakehouse as lh, pediatric_labels, mprint_data, nichd, parent_resources as parents
from core import safety as parent_safety
logging.basicConfig(level=logging.INFO)
for handler in logging.getLogger().handlers: handler.addFilter(LibraryPrivacyFilter())
# Databricks Apps terminates OAuth before /mcp; local deployments retain host checks.
_databricks = bool(os.getenv('DATABRICKS_APP_NAME') or os.getenv('DATABRICKS_APP_PORT'))
mcp=FastMCP('Parent-child Pharmacology MCP',stateless_http=True,json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=not _databricks,
        allowed_hosts=['127.0.0.1:*', 'localhost:*', '[::1]:*'],
        allowed_origins=['http://127.0.0.1:*', 'http://localhost:*', 'http://[::1]:*']))
globals().update(register(mcp))
if __name__=='__main__':
    uvicorn.run(mcp.streamable_http_app(),host=('0.0.0.0' if _databricks else os.getenv('HOST','127.0.0.1')),port=int(os.getenv('DATABRICKS_APP_PORT',os.getenv('PORT','8000'))))
