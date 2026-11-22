"""Security boundaries and protocol behavior, including denied retrieval."""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpcore
import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from mcp.server.auth.middleware.auth_context import auth_context_var
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from mcp.server.fastmcp import FastMCP

from parent_child_pharmacology.core.auth import JWTVerifier, auth_configuration
from parent_child_pharmacology.core.egress import PinnedBackend, PinnedTransport, public_ip
from parent_child_pharmacology.core.http import UpstreamUnavailable
from parent_child_pharmacology.core.pagination import add_pagination
from parent_child_pharmacology.core.registration import ToolCatalog
from parent_child_pharmacology.models.inputs import INPUT_MODELS
from parent_child_pharmacology.tools import register_tools


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "10.0.0.1",
        "169.254.169.254",
        "100.100.100.200",
        "0.0.0.0",
        "224.0.0.1",
        "192.0.2.1",
        "::1",
        "fe80::1",
        "fc00::1",
        "::ffff:127.0.0.1",
        "::ffff:8.8.8.8",
        "2002:0808:0808::",
        "64:ff9b:1::1",
    ],
)
def test_non_public_and_transition_addresses_denied(ip):
    assert not public_ip(ip)


class FakeStream(httpcore.AsyncNetworkStream):
    def __init__(self, peer="8.8.8.8"):
        self.peer, self.closed, self.sni, self.written = peer, False, None, b""

    def get_extra_info(self, key):
        return (self.peer, 443) if key == "server_addr" else None

    async def aclose(self):
        self.closed = True

    async def start_tls(self, ssl_context, server_hostname=None, timeout=None):
        assert ssl_context.check_hostname
        self.sni = server_hostname
        return self

    async def write(self, buffer, timeout=None):
        self.written += buffer

    async def read(self, max_bytes, timeout=None):
        return b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}"


class FakeBackend:
    def __init__(self, stream=None):
        self.stream, self.connected = stream or FakeStream(), []

    async def connect_tcp(self, host, port, *args):
        self.connected.append((host, port))
        return self.stream


@pytest.mark.parametrize("answers", [[], ["8.8.8.8", "127.0.0.1"], ["169.254.169.254"], ["::1"]])
def test_entire_dns_answer_set_checked_before_connect(answers):
    async def run():
        async def resolver(*args):
            return answers

        backend = FakeBackend()
        with pytest.raises(UpstreamUnavailable):
            await PinnedBackend(resolver, backend).connect_tcp("api.fda.gov", 443)
        assert not backend.connected

    asyncio.run(run())


def test_real_httpcore_transport_pins_ip_preserves_host_and_tls_sni():
    async def run():
        resolutions = []

        async def resolver(*args):
            resolutions.append(args)
            return ["8.8.8.8"] if len(resolutions) == 1 else ["127.0.0.1"]

        backend = FakeBackend()
        transport = PinnedTransport(PinnedBackend(resolver, backend))
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.get("https://api.fda.gov/test")
            assert response.json() == {}
        assert len(resolutions) == 1
        assert backend.connected == [("8.8.8.8", 443)]
        assert backend.stream.sni == "api.fda.gov"
        assert b"Host: api.fda.gov" in backend.stream.written

    asyncio.run(run())


def test_peer_mismatch_closes_socket():
    async def run():
        async def resolver(*args):
            return ["8.8.8.8"]

        backend = FakeBackend(FakeStream("127.0.0.1"))
        with pytest.raises(UpstreamUnavailable):
            await PinnedBackend(resolver, backend).connect_tcp("api.fda.gov", 443)
        assert backend.stream.closed

    asyncio.run(run())


@pytest.fixture(scope="module")
def key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.mark.parametrize(
    "change", [{}, {"exp": 1}, {"aud": "wrong"}, {"iss": "wrong"}, {"sub": ""}, {"scope": []}]
)
def test_remote_signed_token_validation(key, change):
    now = int(time.time())
    data = (
        dict(
            iss="https://issuer.example",
            aud="https://resource.example/mcp",
            sub="evaluation",
            iat=now,
            exp=now + 60,
            scope="mcp:connect tool:normalize_drug",
        )
        | change
    )
    token = jwt.encode(data, key, algorithm="RS256")
    verifier = JWTVerifier(
        key.public_key(), "https://issuer.example", "https://resource.example/mcp"
    )
    result = asyncio.run(verifier.verify_token(token))
    assert bool(result) is (not change)


def test_bad_signature_and_unsigned_token_denied(key):
    verifier = JWTVerifier(
        key.public_key(), "https://issuer.example", "https://resource.example/mcp"
    )
    for token in ["not-a-token", jwt.encode({"sub": "evaluation"}, "", algorithm="none")]:
        assert asyncio.run(verifier.verify_token(token)) is None


@pytest.mark.parametrize("name", list(INPUT_MODELS))
def test_each_tool_denies_missing_scope_before_retrieval(name, monkeypatch):
    from mcp.server.fastmcp.exceptions import ToolError

    catalog = ToolCatalog(auth_required=True)
    register_tools(catalog)
    tool = next(t for t in catalog if t.name == name)
    # Call the registered protocol callback directly to isolate authorization from
    # input validation. No arguments are necessary: denial MUST precede retrieval.
    token = AccessToken(token="synthetic", client_id="evaluation", scopes=["mcp:connect"])
    marker = auth_context_var.set(AuthenticatedUser(token))
    try:
        with pytest.raises(PermissionError):
            asyncio.run(tool.fn())
    finally:
        auth_context_var.reset(marker)


def test_authorized_tool_works_but_other_tool_is_denied():
    catalog = ToolCatalog(auth_required=True)
    register_tools(catalog)
    server = FastMCP(tools=catalog)
    token = AccessToken(
        token="synthetic",
        client_id="evaluation",
        scopes=["mcp:connect", "tool:route_parent_question"],
    )
    marker = auth_context_var.set(AuthenticatedUser(token))
    try:
        result = asyncio.run(
            server.call_tool("route_parent_question", {"question": "my little white pill"})
        )
        assert result[1]["allow_research"] is False
        from mcp.server.fastmcp.exceptions import ToolError

        with pytest.raises(ToolError):
            asyncio.run(server.call_tool("normalize_drug", {"name": "sertraline"}))
    finally:
        auth_context_var.reset(marker)


def test_remote_bind_cannot_disable_auth(monkeypatch):
    for name in ["MCP_AUTH_PUBLIC_KEY", "MCP_AUTH_ISSUER", "MCP_AUTH_AUDIENCE"]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("MCP_AUTH_REQUIRED", "false")
    with pytest.raises(ValueError):
        auth_configuration("streamable-http", "0.0.0.0")
    assert auth_configuration("stdio", "127.0.0.1") == (None, None)


def test_valid_remote_configuration(key, monkeypatch):
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    monkeypatch.setenv(
        "MCP_AUTH_PUBLIC_KEY",
        key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode(),
    )
    monkeypatch.setenv("MCP_AUTH_ISSUER", "https://issuer.example")
    monkeypatch.setenv("MCP_AUTH_AUDIENCE", "https://resource.example/mcp")
    verifier, settings = auth_configuration("streamable-http", "0.0.0.0")
    assert verifier and settings.validate_token_resource


def test_http_missing_and_expired_token_denied(key):
    from mcp.server.auth.settings import AuthSettings

    async def run():
        issuer, audience = "https://issuer.example", "https://resource.example/mcp"
        server = FastMCP(
            token_verifier=JWTVerifier(key.public_key(), issuer, audience),
            auth=AuthSettings(
                issuer_url=issuer,
                resource_server_url=audience,
                required_scopes=["mcp:connect"],
                validate_token_resource=True,
            ),
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=server.streamable_http_app()),
            base_url="http://127.0.0.1",
        ) as client:
            for token in [
                None,
                "invalid",
                jwt.encode(
                    dict(iss=issuer, aud=audience, sub="evaluation", iat=1, exp=2),
                    key,
                    algorithm="RS256",
                ),
            ]:
                headers = {"Authorization": "Bearer " + token} if token else {}
                response = await client.post("/mcp", json={}, headers=headers)
                assert response.status_code == 401

    asyncio.run(run())


def test_markdown_preserves_structured_safety_notices():
    from parent_child_pharmacology.app import mcp

    result = asyncio.run(
        mcp.call_tool(
            "route_parent_question",
            {"question": "my little white pill", "response_format": "markdown"},
        )
    )
    assert result.structuredContent["allow_research"] is False
    assert "required_display_notices" in result.content[0].text
    assert result.structuredContent["disclaimer"] in result.content[0].text


def test_pubmed_continuation_and_unknown_completeness():
    from parent_child_pharmacology.clients.pubmed import pubmed_search_params

    assert pubmed_search_params("sertraline", offset=20)["retstart"] == 20
    result = add_pagination(
        {"source": "live:pubmed", "results": [1], "search_metadata": {"count": "40"}},
        "search_literature",
        {"offset": 20, "max_results": 10},
    )
    assert result["pagination"]["next_offset"] == 30
    assert add_pagination({}, "search_trials", {})["pagination"]["has_more"] is None


def test_staged_entrypoint_without_editable_install(tmp_path):
    root = Path(__file__).parents[1]
    shutil.copy(root / "main.py", tmp_path / "main.py")
    # A sentinel package proves the entrypoint resolves staged src, not the
    # repository's editable installation or its current working directory.
    package = tmp_path / "src/parent_child_pharmacology"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "app.py").write_text("def main(): print('STAGED_SOURCE_SELECTED')")
    result = subprocess.run(
        [sys.executable, "-I", str(tmp_path / "main.py")],
        cwd=tmp_path.parent,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "STAGED_SOURCE_SELECTED"
