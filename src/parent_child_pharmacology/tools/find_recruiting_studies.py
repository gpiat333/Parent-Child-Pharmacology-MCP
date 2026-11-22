"""Register the find_recruiting_studies tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import find_recruiting_studies


def register(mcp):
    return register_tool(mcp, find_recruiting_studies, "parent_resources")
