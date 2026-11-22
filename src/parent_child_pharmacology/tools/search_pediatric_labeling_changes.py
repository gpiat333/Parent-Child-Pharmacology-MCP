"""Register the search_pediatric_labeling_changes tool; domain behavior lives in services.labels_safety."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.labels_safety import search_pediatric_labeling_changes


def register(mcp):
    return register_tool(mcp, search_pediatric_labeling_changes, "labels_safety")
