"""Register the get_adverse_event_signals tool; domain behavior lives in services.labels_safety."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.labels_safety import get_adverse_event_signals


def register(mcp):
    return register_tool(mcp, get_adverse_event_signals, "labels_safety")
