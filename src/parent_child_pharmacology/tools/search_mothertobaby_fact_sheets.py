"""Register the search_mothertobaby_fact_sheets tool; behavior lives in services.fact_sheets."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.fact_sheets import search_mothertobaby_fact_sheets


def register(mcp):
    return register_tool(mcp, search_mothertobaby_fact_sheets, "parent_resources")
