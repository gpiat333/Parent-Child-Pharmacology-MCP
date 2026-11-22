"""Register the search_bpca_evidence tool; domain behavior lives in services.nichd."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.nichd import search_bpca_evidence


def register(mcp):
    return register_tool(mcp, search_bpca_evidence, "nichd")
