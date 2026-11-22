"""Reject an unapproved remote destination before invoking credential tooling."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "endpoint",
    ["https://evil.example/mcp", "https://user@localhost/mcp", "https://localhost/mcp?token=x"],
)
def test_companion_rejects_destination_before_auth(endpoint):
    shell = shutil.which("pwsh")
    if not shell:
        pytest.skip("PowerShell companion requires pwsh; Windows CI covers this test")
    env = dict(
        os.environ,
        DATABRICKS_CLI_PATH="must-not-execute-nonexistent-cli",
        DATABRICKS_HOST="https://example.cloud.databricks.com",
        DATABRICKS_CONFIG_PROFILE="test",
    )
    result = subprocess.run(
        [
            shell,
            "-NoProfile",
            "-File",
            str(ROOT / "chat-client/test-mcp-chat.ps1"),
            "-McpEndpoint",
            endpoint,
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert (
        "Invalid MCP endpoint" in result.stderr
        or "Remote MCP endpoint must exactly match" in result.stderr
    )
    assert "must-not-execute-nonexistent-cli" not in result.stderr
