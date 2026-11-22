"""Check public-source reachability from app compute, then start the server."""
import asyncio
import json
import runpy

import httpx

HOSTS = (
    "eutils.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov",
    "api.reporter.nih.gov", "dailymed.nlm.nih.gov", "api.fda.gov",
    "rxnav.nlm.nih.gov", "clinicaltrials.gov", "wsearch.nlm.nih.gov",
    "connect.medlineplus.gov",
)


async def check_egress():
    async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
        async def check(host):
            try:
                response = await client.get(f"https://{host}/")
                result = {"host": host, "http_status": response.status_code}
            except httpx.HTTPError as exc:
                result = {"host": host, "error_type": type(exc).__name__}
            # Infrastructure health only; never queries, headers, or credentials.
            print("EGRESS_CHECK " + json.dumps(result), flush=True)
        await asyncio.gather(*(check(host) for host in HOSTS))


if __name__ == "__main__":
    asyncio.run(check_egress())
    runpy.run_module("server", run_name="__main__")
