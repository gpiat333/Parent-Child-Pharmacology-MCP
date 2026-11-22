"""Register the get_abstracts tool; domain behavior lives in services.literature."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.literature import get_abstracts


def register(mcp):
    return register_tool(mcp, get_abstracts, "literature")
