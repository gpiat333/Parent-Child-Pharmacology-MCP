"""Register the route_parent_question tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import route_parent_question


def register(mcp):
    return register_tool(mcp, route_parent_question, "parent_resources")
