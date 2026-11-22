"""Register the get_lactmed_record tool; domain behavior lives in services.lactation."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.lactation import get_lactmed_record


def register(mcp):
    return register_tool(mcp, get_lactmed_record, "lactation")
