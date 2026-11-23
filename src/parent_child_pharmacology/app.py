"""Thin application entry point for local clients and sandbox hosts."""

import logging
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from parent_child_pharmacology import clients as src
from parent_child_pharmacology.clients import (
    lakehouse as lh,
)
from parent_child_pharmacology.clients import (
    mprint_data,
    nichd,
    pediatric_labels,
)
from parent_child_pharmacology.clients import (
    parent_resources as parents,
)
from parent_child_pharmacology.core import config as cfg
from parent_child_pharmacology.core import safety as parent_safety
from parent_child_pharmacology.core.audit import LibraryPrivacyFilter
from parent_child_pharmacology.core.auth import auth_configuration
from parent_child_pharmacology.core.instructions import INSTRUCTIONS
from parent_child_pharmacology.core.registration import ToolCatalog
from parent_child_pharmacology.prompts import register_prompts
from parent_child_pharmacology.resources import register_resources
from parent_child_pharmacology.routes import register_routes
from parent_child_pharmacology.tools import register_tools

logging.basicConfig(level=logging.INFO)
for handler in logging.getLogger().handlers:
    handler.addFilter(LibraryPrivacyFilter())


def transport_settings():
    port = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    mode = "streamable-http" if port else os.getenv("MCP_TRANSPORT", "stdio")
    if mode not in {"stdio", "streamable-http"}:
        raise ValueError("MCP_TRANSPORT must be stdio or streamable-http")
    return (
        mode,
        os.getenv("MCP_HOST", "0.0.0.0" if port else "127.0.0.1"),
        int(port or os.getenv("MCP_PORT", "8000")),
    )


# Hosted DNS names are explicit operator configuration, never tool arguments.
hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
hosted_url = os.getenv("DATABRICKS_APP_URL", "")
if hosted_url:
    from urllib.parse import urlsplit

    host = urlsplit(hosted_url if "://" in hosted_url else "https://" + hosted_url).hostname
    if host and host.endswith(".databricksapps.com"):
        hosts.append(host)
hosts += [h.strip() for h in os.getenv("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
verifier, auth_settings = auth_configuration(*transport_settings()[:2])
catalog = ToolCatalog(auth_required=verifier is not None)
globals().update(register_tools(catalog))
mcp = FastMCP(
    "Parent-child Pharmacology MCP",
    instructions=INSTRUCTIONS,
    tools=catalog,
    token_verifier=verifier,
    auth=auth_settings,
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
    ),
)
register_prompts(mcp)
register_resources(mcp)
register_routes(mcp)


def main():
    mode, host, port = transport_settings()
    if mode == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn

        from parent_child_pharmacology.core.auth import (
            DatabricksGatewayGuard,
            databricks_gateway_mode,
        )

        app = mcp.streamable_http_app()
        if databricks_gateway_mode():
            app = DatabricksGatewayGuard(app)
        uvicorn.run(app, host=host, port=port, access_log=False)


if __name__ == "__main__":
    main()
