"""Template entry-point, registration and HTTP metadata contracts."""

import asyncio

import httpx
import pytest

from parent_child_pharmacology.app import mcp, transport_settings


@pytest.mark.parametrize(
    "env,expected",
    [
        ({}, ("stdio", "127.0.0.1", 8000)),
        (
            {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "8999"},
            ("streamable-http", "127.0.0.1", 8999),
        ),
        ({"PORT": "8080"}, ("streamable-http", "0.0.0.0", 8080)),
        ({"DATABRICKS_APP_PORT": "9000", "PORT": "8080"}, ("streamable-http", "0.0.0.0", 9000)),
    ],
)
def test_template_transport_selection(monkeypatch, env, expected):
    for key in ["MCP_TRANSPORT", "MCP_HOST", "MCP_PORT", "PORT", "DATABRICKS_APP_PORT"]:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    assert transport_settings() == expected


def test_invalid_transport_is_rejected(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("DATABRICKS_APP_PORT", raising=False)
    monkeypatch.setenv("MCP_TRANSPORT", "invalid")
    with pytest.raises(ValueError):
        transport_settings()


def test_health_version_and_registered_inventory():
    async def run():
        assert len(await mcp.list_tools()) == 31
        assert len(await mcp.list_prompts()) == 4
        assert len(await mcp.list_resources()) == 4
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=mcp.streamable_http_app()),
            base_url="http://127.0.0.1:8000",
        ) as client:
            health = await client.get("/health")
            version = await client.get("/version")
            assert health.status_code == 200 and health.json()["status"] == "healthy"
            assert version.status_code == 200 and version.json()["version"] == "0.19.0"
            assert version.json()["policy_version"] == "2026-11-23.23"

    asyncio.run(run())
