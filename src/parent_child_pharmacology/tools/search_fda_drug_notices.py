"""Register the search_fda_drug_notices tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import search_fda_drug_notices


def register(mcp):
    return register_tool(mcp, search_fda_drug_notices, "parent_resources")
