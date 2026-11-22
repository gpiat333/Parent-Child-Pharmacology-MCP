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


def auth_configuration(mode, host):
    remote = mode == "streamable-http" and host not in {"127.0.0.1", "localhost", "::1"}
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
