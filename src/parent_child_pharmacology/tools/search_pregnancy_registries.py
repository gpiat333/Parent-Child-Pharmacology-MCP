"""Register the search_pregnancy_registries tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import search_pregnancy_registries


def register(mcp):
    return register_tool(mcp, search_pregnancy_registries, "parent_resources")
