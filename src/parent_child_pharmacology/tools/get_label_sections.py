"""Register the get_label_sections tool; domain behavior lives in services.labels_safety."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.labels_safety import get_label_sections


def register(mcp):
    return register_tool(mcp, get_label_sections, "labels_safety")
