"""Register the check_evidence_coverage tool; domain behavior lives in services.discovery."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.discovery import check_evidence_coverage


def register(mcp):
    return register_tool(mcp, check_evidence_coverage, "discovery")
