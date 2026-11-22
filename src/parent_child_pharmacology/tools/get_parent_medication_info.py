"""Register the get_parent_medication_info tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import get_parent_medication_info


def register(mcp):
    return register_tool(mcp, get_parent_medication_info, "parent_resources")
