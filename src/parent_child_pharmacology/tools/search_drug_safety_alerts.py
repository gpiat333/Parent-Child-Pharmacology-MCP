"""Register the search_drug_safety_alerts tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import search_drug_safety_alerts


def register(mcp):
    return register_tool(mcp, search_drug_safety_alerts, "parent_resources")
