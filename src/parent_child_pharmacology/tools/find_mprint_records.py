"""Register the find_mprint_records tool; domain behavior lives in services.mprint."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.mprint import find_mprint_records


def register(mcp):
    return register_tool(mcp, find_mprint_records, "mprint")
