"""Register the get_mprint_details tool; domain behavior lives in services.mprint."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.mprint import get_mprint_details


def register(mcp):
    return register_tool(mcp, get_mprint_details, "mprint")
