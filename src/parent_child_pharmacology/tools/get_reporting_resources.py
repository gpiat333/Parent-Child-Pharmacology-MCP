"""Register the get_reporting_resources tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import get_reporting_resources


def register(mcp):
    return register_tool(mcp, get_reporting_resources, "parent_resources")
