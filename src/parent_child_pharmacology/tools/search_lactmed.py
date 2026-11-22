"""Register the search_lactmed tool; domain behavior lives in services.lactation."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.lactation import search_lactmed


def register(mcp):
    return register_tool(mcp, search_lactmed, "lactation")
