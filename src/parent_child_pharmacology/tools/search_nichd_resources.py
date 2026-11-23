"""Register the search_nichd_resources tool; domain behavior lives in services.nichd."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.nichd import search_nichd_resources


def register(mcp):
    return register_tool(mcp, search_nichd_resources, "nichd")
