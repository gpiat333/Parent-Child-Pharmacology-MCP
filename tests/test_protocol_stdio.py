"""Real stdio protocol smoke check without any upstream request."""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_local_stdio_client_can_initialize_discover_and_stop_before_retrieval():
    async def run():
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(Path(__file__).resolve().parents[1] / "main.py")],
            env={"USE_LAKEHOUSE": "false", "MCP_TRANSPORT": "stdio"},
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                assert len((await session.list_tools()).tools) == 30
                assert len((await session.list_prompts()).prompts) == 4
                assert len((await session.list_resources()).resources) == 4
                result = await session.call_tool(
                    "route_parent_question", {"question": "What is my little white pill?"}
                )
                assert result.structuredContent["allow_research"] is False
                assert result.structuredContent["requires_confirmation"]

    asyncio.run(run())
