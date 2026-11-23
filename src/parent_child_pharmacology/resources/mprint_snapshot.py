def register(mcp):
    @mcp.resource("parent-child://mprint-snapshot")
    async def mprint_snapshot() -> str:
        """Bundled MPRINT snapshot details, its age, and a live check for newer upstream data."""
        import json

        from parent_child_pharmacology.core.capabilities import snapshot_metadata
        from parent_child_pharmacology.core.freshness import check_upstream, mprint_freshness

        return json.dumps(
            {
                **snapshot_metadata(),
                "data_freshness": mprint_freshness(),
                "upstream_check": await check_upstream(),
            }
        )
