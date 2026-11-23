"""Dependency-free health and version endpoints adapted from the GSA template."""

from starlette.responses import HTMLResponse, JSONResponse

from parent_child_pharmacology import __version__
from parent_child_pharmacology.core.safety import POLICY_VERSION

LANDING = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parent-child Pharmacology MCP</title>
<style>body{font-family:system-ui,sans-serif;max-width:40rem;margin:3rem auto;padding:0 1rem;line-height:1.5;color:#2b2b3a}
h1{color:#2a296b;font-size:1.6rem}code{background:#eef0fb;padding:.1rem .3rem;border-radius:4px}</style></head>
<body><h1>Parent-child Pharmacology MCP</h1>
<p>This is an MCP server: a service for AI assistants, not a website. It gives assistants public evidence about
medicines in pregnancy, breastfeeding and childhood, from LactMed, FDA labels, PubMed, ClinicalTrials.gov,
NIH and NICHD data, with safety checks before every lookup.</p>
<p>AI clients connect to <code>/mcp</code>. Status: <a href="/health">/health</a> &middot;
<a href="/version">/version</a>.</p>
<p>Hackathon prototype. Not an official NIH product or medical advice.</p></body></html>"""


def register_routes(mcp):
    @mcp.custom_route("/", methods=["GET"])
    async def landing(request):
        return HTMLResponse(LANDING)

    @mcp.custom_route("/health", methods=["GET"])
    async def health(request):
        return JSONResponse({"status": "healthy", "service": "parent-child-pharmacology-mcp"})

    @mcp.custom_route("/version", methods=["GET"])
    async def version(request):
        return JSONResponse(
            {"version": __version__, "policy_version": POLICY_VERSION, "prototype": True}
        )
