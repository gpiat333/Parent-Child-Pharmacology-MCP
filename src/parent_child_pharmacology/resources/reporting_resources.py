def register(mcp):
    @mcp.resource("parent-child://reporting-resources")
    def reporting_resources() -> str:
        """Official FDA MedWatch and NIH/FDA public-involvement links (fixed navigation list)."""
        import json

        from parent_child_pharmacology.clients import parent_resources as parents

        return json.dumps(parents.reporting_resources())
