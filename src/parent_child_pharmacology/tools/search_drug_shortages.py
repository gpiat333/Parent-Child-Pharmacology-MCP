"""Register the search_drug_shortages tool; domain behavior lives in services.discovery."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.discovery import search_drug_shortages


def register(mcp):
    return register_tool(mcp, search_drug_shortages, "discovery")
