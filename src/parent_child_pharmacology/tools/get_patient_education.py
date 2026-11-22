"""Register the get_patient_education tool; domain behavior lives in services.labels_safety."""

from parent_child_pharmacology.core.registration import register_tool
from parent_child_pharmacology.services.labels_safety import get_patient_education


def register(mcp):
    return register_tool(mcp, get_patient_education, "labels_safety")
