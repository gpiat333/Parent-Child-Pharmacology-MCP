"""Ask route_parent_question each held-out routing question once and score allow_research.

Usage: python eval/heldout/run_routing.py <mcp-url> <output.json> [--databricks-profile NAME]
No model is involved: the router is deterministic server code.
"""

import asyncio
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

url, out = sys.argv[1], Path(sys.argv[2])
headers = {}
if "--databricks-profile" in sys.argv:
    profile = sys.argv[sys.argv.index("--databricks-profile") + 1]
    token = json.loads(
        subprocess.run(
            ["databricks", "auth", "token", "--profile", profile], capture_output=True, text=True
        ).stdout
    )["access_token"]
    headers = {"Authorization": "Bearer " + token}
cases = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))["routing"]


async def main():
    rows = []
    async with streamablehttp_client(url, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for c in cases:
                res = await s.call_tool("route_parent_question", {"question": c["question"]})
                sc = res.structuredContent or {}
                allow = bool(sc.get("allow_research"))
                rows.append({**c, "route": sc.get("route"), "allow_research": allow,
                             "message_es": "message_es" in sc, "correct": allow == c["expect_allow_research"]})
    by = Counter(); ok = Counter()
    for x in rows:
        by[x["category"]] += 1; ok[x["category"]] += x["correct"]
    summary = {"run_at_utc": datetime.now(timezone.utc).isoformat(), "endpoint_host": url.split("/")[2],
               "total": len(rows), "correct": sum(x["correct"] for x in rows),
               "by_category": {k: f"{ok[k]}/{by[k]}" for k in by}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for x in rows:
        if not x["correct"]:
            print("MISS", x["id"], x["category"], "->", x["route"], "|", x["question"])


asyncio.run(main())
