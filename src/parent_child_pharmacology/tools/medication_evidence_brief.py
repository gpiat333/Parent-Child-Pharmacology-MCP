"""Register the medication_evidence_brief tool; domain behavior lives in services.composite."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.composite import medication_evidence_brief


def register(mcp):
    return register_tool(mcp, medication_evidence_brief, "composite")
