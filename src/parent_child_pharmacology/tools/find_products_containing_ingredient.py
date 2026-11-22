"""Register the find_products_containing_ingredient tool; domain behavior lives in services.discovery."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.discovery import find_products_containing_ingredient


def register(mcp):
    return register_tool(mcp, find_products_containing_ingredient, "discovery")
