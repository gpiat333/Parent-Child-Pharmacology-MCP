"""Fail-closed remote JWT verification and explicit per-tool scopes.

Public verification keys are operator configuration, never request inputs.
The issuer, resource audience, expiry and subject are mandatory; only RS256 is
accepted. Key rotation requires updating configuration and restarting the app.
"""

import os
from urllib.parse import urlsplit

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings


class JWTVerifier:
    def __init__(self, public_key, issuer, audience):
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience

    async def verify_token(self, token):
        try:
            data = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
            if not isinstance(data["sub"], str) or not data["sub"].strip():
                return None
            scopes = data.get("scope", "")
            if not isinstance(scopes, str):
                return None
            return AccessToken(
                token=token,
                client_id=data["sub"],
                subject=data["sub"],
                scopes=scopes.split(),
                expires_at=int(data["exp"]),
                resource=self.audience,
            )
        except (jwt.PyJWTError, ValueError, TypeError, KeyError):
            return None


# Headers the Databricks Apps front door sets after a user signs in to the workspace.
GATEWAY_IDENTITY_HEADERS = (b"x-forwarded-email", b"x-forwarded-user")


def databricks_gateway_mode(env=None):
    """True only when explicitly enabled AND actually running inside Databricks Apps.

    In this mode Databricks' own workspace sign-in is the access control, the same pattern
    Databricks uses for MCP servers hosted on Databricks Apps. Every MCP request must carry the
    identity headers the Databricks front door adds; tool scopes are not checked.
    """
    env = os.environ if env is None else env
    return (
        env.get("MCP_AUTH_MODE", "") == "databricks_apps"
        and bool(env.get("DATABRICKS_APP_PORT"))
        and bool(env.get("DATABRICKS_APP_NAME") or env.get("DATABRICKS_APP_URL"))
    )


class DatabricksGatewayGuard:
    """Reject MCP requests that did not come through the Databricks Apps sign-in."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path", "").startswith("/mcp"):
            headers = dict(scope.get("headers") or [])
            if not any(headers.get(h, b"").strip() for h in GATEWAY_IDENTITY_HEADERS):
                body = b'{"error":"databricks_sign_in_required"}'
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return
        await self.app(scope, receive, send)


def auth_configuration(mode, host):
    remote = mode == "streamable-http" and host not in {"127.0.0.1", "localhost", "::1"}
    if remote and databricks_gateway_mode():
        return None, None
    required = remote or os.getenv("MCP_AUTH_REQUIRED", "false").lower() == "true"
    if not required:
        return None, None
    key = os.getenv("MCP_AUTH_PUBLIC_KEY", "").replace("\\n", "\n")
    issuer = os.getenv("MCP_AUTH_ISSUER", "")
    audience = os.getenv("MCP_AUTH_AUDIENCE", "")
    if not key or any(
        urlsplit(u).scheme != "https" or not urlsplit(u).hostname for u in [issuer, audience]
    ):
        raise ValueError(
            "Remote MCP requires a public RS256 key and HTTPS issuer/audience configuration"
        )
    # Validate configuration before accepting any connection.
    loaded = load_pem_public_key(key.encode())
    if not isinstance(loaded, RSAPublicKey) or loaded.key_size < 2048:
        raise ValueError("Remote MCP verification requires an RSA public key of at least 2048 bits")
    return JWTVerifier(key, issuer, audience), AuthSettings(
        issuer_url=issuer,
        resource_server_url=audience,
        required_scopes=["mcp:connect"],
        validate_token_resource=True,
    )


def authorize_tool(name, required):
    if not required:
        return
    token = get_access_token()
    if token is None or "mcp:connect" not in token.scopes or f"tool:{name}" not in token.scopes:
        raise PermissionError(
            "Tool scope denied; request the named tool permission from the operator"
        )
