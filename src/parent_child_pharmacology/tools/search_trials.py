"""Register the search_trials tool; domain behavior lives in services.literature."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.literature import search_trials


def register(mcp):
    return register_tool(mcp, search_trials, "literature")
