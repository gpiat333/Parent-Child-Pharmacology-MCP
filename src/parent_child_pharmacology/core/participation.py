"""Navigation tier, never efficacy evidence, ranking, enrollment or recommendation."""

TOOLS = {
    "find_pregnancy_exposure_registries",
    "search_pregnancy_registries",
    "find_recruiting_studies",
    "search_parent_input_opportunities",
}


def tier(payload=None, *, suppressed=False, reason=None):
    payload = dict(payload or {})
    for key in ("results", "studies", "notices"):
        if isinstance(payload.get(key), list):
            payload[key] = (
                []
                if suppressed
                else sorted(
                    payload[key],
                    key=lambda x: str(
                        x.get("registry") or x.get("title") or x.get("medicine") or ""
                    ).casefold(),
                )
            )
    return {
        **payload,
        "tier": "participation",
        "suppressed": suppressed,
        "suppression_reason": reason,
        "display_order": "Alphabetical within each returned list, not clinical suitability. Upstream retrieval limits still apply.",
        "ranked": False,
        "recommended": False,
        "eligibility_determined": False,
        "contact_or_submission_performed": False,
        "non_recommendation_statement": "Directory information only. Listings are not ranked or recommended and do not establish eligibility, safety or benefit. Contact the listed team to verify current details.",
        "required_preflight": "Suppress this entire tier during urgent, crisis, language, privacy, treatment-decision and unconfirmed-identity routes.",
    }
