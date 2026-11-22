"""End-to-end smoke test against a running server (local or Databricks App).

  python smoke_test.py http://localhost:8000/mcp sertraline
  (set DATABRICKS_TOKEN first for a deployed app)
"""
import asyncio
import json
import os
import sys

import httpx
from mcp import ClientSession

try:  # newer mcp releases
    from mcp.client.streamable_http import streamable_http_client as _connect
    _NEW = True
except ImportError:  # older mcp releases
    from mcp.client.streamable_http import streamablehttp_client as _connect
    _NEW = False


def connect(url: str, headers: dict):
    if _NEW:
        client = httpx.AsyncClient(headers=headers, timeout=60) if headers else None
        return _connect(url, http_client=client) if client else _connect(url)
    return _connect(url, headers=headers)


async def main(url: str, drug: str) -> None:
    token = os.getenv("DATABRICKS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with connect(url, headers) as streams:
        async with ClientSession(streams[0], streams[1]) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("TOOLS:", [t.name for t in tools])
            for name, args in [("normalize_drug", {"name": drug}),
                               ("search_lactmed", {"drug": drug}),
                               ("get_label_sections", {"drug": drug}),
                               ("medication_evidence_brief", {"drug": drug, "population": "lactation"})]:
                res = await s.call_tool(name, args)
                body = res.content[0].text if res.content else ""
                print(f"\n=== {name} (isError={res.isError}) ===\n{body[:700]}")
                try:
                    d = json.loads(body)
                    if "error" in d:
                        print("  !! tool reported error:", d["error"])
                except json.JSONDecodeError:
                    pass


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "sertraline"))
