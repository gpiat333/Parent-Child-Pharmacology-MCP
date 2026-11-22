from parent_child_pharmacology.core import config as cfg


def register(mcp):
    @mcp.resource("parent-child://disclaimer")
    def disclaimer() -> str:
        return cfg.DISCLAIMER
