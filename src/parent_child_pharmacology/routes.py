"""Dependency-free health and version endpoints adapted from the GSA template."""

from starlette.responses import JSONResponse

from parent_child_pharmacology import __version__
from parent_child_pharmacology.core.safety import POLICY_VERSION


def register_routes(mcp):
    @mcp.custom_route("/health", methods=["GET"])
    async def health(request):
        return JSONResponse({"status": "healthy", "service": "parent-child-pharmacology-mcp"})

    @mcp.custom_route("/version", methods=["GET"])
    async def version(request):
        return JSONResponse(
            {"version": __version__, "policy_version": POLICY_VERSION, "prototype": True}
        )
