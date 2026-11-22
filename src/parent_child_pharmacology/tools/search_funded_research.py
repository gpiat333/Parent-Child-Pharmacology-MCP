"""Register the search_funded_research tool; domain behavior lives in services.literature."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.literature import search_funded_research


def register(mcp):
    return register_tool(mcp, search_funded_research, "literature")
