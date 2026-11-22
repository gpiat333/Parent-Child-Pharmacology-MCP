"""Register the normalize_drug tool; domain behavior lives in services.identity."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.identity import normalize_drug


def register(mcp):
    return register_tool(mcp, normalize_drug, "identity")
