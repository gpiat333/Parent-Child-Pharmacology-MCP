"""Register the find_pregnancy_exposure_registries tool; domain behavior lives in services.parent_resources."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.parent_resources import find_pregnancy_exposure_registries


def register(mcp):
    return register_tool(mcp, find_pregnancy_exposure_registries, "parent_resources")
