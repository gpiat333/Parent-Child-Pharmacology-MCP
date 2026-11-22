def register(mcp):
    @mcp.resource("parent-child://capabilities")
    def source_capabilities() -> str:
        import json

        from parent_child_pharmacology.core.capabilities import capabilities

        return json.dumps(capabilities())
