def register(mcp):
    @mcp.resource("parent-child://mprint-snapshot")
    def mprint_snapshot() -> str:
        import json

        from parent_child_pharmacology.core.capabilities import snapshot_metadata

        return json.dumps(snapshot_metadata())
