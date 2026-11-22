"""Explicit workflow requests, evaluated only after whole-question safety preflight.

This is narrow intent matching, not clinical classification. Source text must never
be passed here as a user request. Clients enforce the returned tool requirement.
"""

import re

BRIEF = r"(?:(?:medication|pregnancy|lactation|pediatric)\s+)?evidence\s+brief"
CREATE = r"(?:prepare|create|compile|build|generate|draft|make|provide|write|give|show|send)"
# Share the object grammar so adding a request verb cannot bypass its negation
# (for example, "give me a brief" versus "don't give me a brief").
BRIEF_OBJECT = rf"(?:me\s+)?(?:(?:an?|the|any)\s+)?{BRIEF}"
NEGATED = re.compile(
    rf"\b(?:(?:do\s+not|don't|dont|never)\s+(?:use|call|{CREATE})|avoid|skip|without|instead\s+of|rather\s+than)"
    rf"\s+(?:using\s+|calling\s+)?{BRIEF_OBJECT}\b",
    re.I,
)
REQUESTED = re.compile(
    rf"\b(?:{CREATE}\s+{BRIEF_OBJECT}|"
    rf"(?:use|using|call)\s+(?:(?:an?|the)\s+)?{BRIEF}\s+tool)\b",
    re.I,
)


def requested_workflow(question):
    """Require the composite for an explicit brief request, not an incidental mention."""
    text = question.replace("’", "'").replace(
        "medication_evidence_brief", "medication evidence brief tool"
    )
    if NEGATED.search(text) or not REQUESTED.search(text):
        return None
    return {
        "name": "medication_evidence_brief",
        "required_tool": "medication_evidence_brief",
        "basis": "explicit_user_request_for_evidence_brief",
        "enforcement": "Call this tool before any optional retrieval or final answer. After its response, additional tools are allowed if needed. Stop on any identity or policy refusal.",
        "scope": "Narrow English request matching, not a clinical decision or a guarantee of answer quality.",
        "client_enforcement_required": True,
    }
