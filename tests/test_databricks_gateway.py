"""Databricks Apps hosted mode: workspace sign-in is the access control, only inside Databricks."""

import asyncio

import pytest

from parent_child_pharmacology.core.auth import (
    DatabricksGatewayGuard,
    auth_configuration,
    databricks_gateway_mode,
)

APP_ENV = {
    "MCP_AUTH_MODE": "databricks_apps",
    "DATABRICKS_APP_PORT": "8000",
    "DATABRICKS_APP_NAME": "mcp-mc",
}


def test_gateway_mode_needs_the_explicit_setting_and_a_databricks_app():
    assert databricks_gateway_mode(APP_ENV) is True
    assert databricks_gateway_mode({**APP_ENV, "MCP_AUTH_MODE": ""}) is False
    assert databricks_gateway_mode({"MCP_AUTH_MODE": "databricks_apps"}) is False
    assert (
        databricks_gateway_mode({"MCP_AUTH_MODE": "databricks_apps", "DATABRICKS_APP_PORT": "8000"})
        is False
    )


def test_outside_databricks_remote_still_requires_the_token_issuer(monkeypatch):
    for k in [
        "DATABRICKS_APP_PORT",
        "DATABRICKS_APP_NAME",
        "DATABRICKS_APP_URL",
        "MCP_AUTH_PUBLIC_KEY",
    ]:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("MCP_AUTH_MODE", "databricks_apps")
    with pytest.raises(ValueError):
        auth_configuration("streamable-http", "0.0.0.0")


def test_inside_databricks_gateway_mode_skips_the_token_issuer(monkeypatch):
    for k, v in APP_ENV.items():
        monkeypatch.setenv(k, v)
    assert auth_configuration("streamable-http", "0.0.0.0") == (None, None)


def run(guard, path, headers):
    sent = []

    async def app(scope, receive, send):
        sent.append("passed")

    async def send(msg):
        sent.append(msg)

    async def receive():
        return {"type": "http.request"}

    scope = {"type": "http", "path": path, "headers": headers}
    asyncio.run(DatabricksGatewayGuard(app)(scope, receive, send))
    return sent


def test_mcp_requests_without_databricks_identity_are_rejected():
    sent = run(None, "/mcp", [])
    assert sent[0]["status"] == 401 and b"databricks_sign_in_required" in sent[1]["body"]
    assert run(None, "/mcp", [(b"x-forwarded-email", b"  ")])[0]["status"] == 401


def test_mcp_requests_through_databricks_sign_in_pass():
    assert run(None, "/mcp", [(b"x-forwarded-email", b"user@example.gov")]) == ["passed"]
    assert run(None, "/mcp", [(b"x-forwarded-user", b"12345")]) == ["passed"]


def test_health_checks_pass_without_identity():
    assert run(None, "/health", []) == ["passed"]
