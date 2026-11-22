"""Explicit search bands; source ages and prematurity must never be inferred."""

BANDS = {
    "neonate": (0, 28 / 365.25),
    "infant": (28 / 365.25, 2),
    "child": (2, 12),
    "adolescent": (12, 18),
}
DEFINITIONS = {
    "neonate": "birth to under 28 days",
    "infant": "28 days to under 2 years",
    "child": "2 to under 12 years",
    "adolescent": "12 to under 18 years",
}


def preserve_population(out, population):
    return {
        **out,
        "population": population,
        "requested_age_band": population if population in BANDS else None,
        "population_coverage": {
            "requested_band": population,
            "search_band_definition": DEFINITIONS.get(population),
            "source_age_and_prematurity_must_be_preserved": True,
            "source_band_confirmed": False,
            "notice": "Search bands are prototype conventions, not clinical equivalence. Preserve actual source ages, gestational age and prematurity. A broad pediatric record does not establish evidence for the requested band.",
        },
    }


def registry_band_matches(elig, population):
    from parent_child_pharmacology.clients.trial_navigation import (
        age_year_bounds,
        pediatric_population,
    )

    if population == "pediatric":
        return pediatric_population(elig)["status"] == "pediatric_included"
    if population not in BANDS:
        return True
    minimum = age_year_bounds(elig.get("minimumAge"))
    maximum = age_year_bounds(elig.get("maximumAge"))
    if not minimum or not maximum or minimum[0] > maximum[1]:
        return False
    low, high = BANDS[population]
    return (
        minimum[1] < high
        and maximum[0] >= low
        and pediatric_population(elig)["status"] == "pediatric_included"
    )
