"""Register the search_literature tool; domain behavior lives in services.literature."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.literature import search_literature


def register(mcp):
    return register_tool(mcp, search_literature, "literature")
