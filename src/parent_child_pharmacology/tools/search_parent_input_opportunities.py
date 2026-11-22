"""Register the search_parent_input_opportunities tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import search_parent_input_opportunities


def register(mcp):
    return register_tool(mcp, search_parent_input_opportunities, "parent_resources")
