"""Condition names are research topics; active events and personal crises still stop."""

import asyncio

import pytest

from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.core.language import scientific_selector
from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "question",
    [
        "Is levetiracetam safe while breastfeeding? I take it for seizures.",
        "What does research say about lamotrigine for seizures in pregnancy?",
        "What is known about a medicine for babies who have trouble breathing (bronchopulmonary dysplasia)?",
        "What is known about postpartum depression treatment with zuranolone?",
        "Are there studies on my blood pressure medicine labetalol in pregnancy?",
        "Is St. John's wort safe while breastfeeding?",
        "No trouble breathing. What are the side effects?",
    ],
)
def test_research_questions_naming_conditions_reach_evidence(question):
    assert route(question)["route"] == "evidence"


@pytest.mark.parametrize(
    "question",
    [
        "My child is having seizures.",
        "My baby is having a seizure",
        "baby seizure right now help",
        "my baby has trouble breathing",
        "I have trouble breathing after taking it",
        "my son is seizing",
        "He is unresponsive",
        "We need control of seizures now.",
        "Is lamotrigine safe? My baby is having a seizure.",
    ],
)
def test_active_events_still_route_to_urgent_help(question):
    assert route(question)["route"] == "urgent_help"


@pytest.mark.parametrize(
    "question",
    [
        "I have postpartum depression and feel hopeless.",
        "Can sertraline treat my postpartum psychosis?",
        "I think I have postpartum depression. Is sertraline ok?",
    ],
)
def test_personal_perinatal_mood_disclosure_still_routes_to_support(question):
    out = route(question)
    assert out["route"] == "mental_health_support"
    assert "1-800-944-4773" in out["message"]


def test_crisis_links_carry_no_third_party_tracking():
    out = route("I want to harm myself.")
    links = out["source_urls"] + [
        v for r in out["referrals"] for k, v in r.items() if k.endswith("_link")
    ]
    assert links and not any("?" in link for link in links)
    assert {"tel:988", "sms:988"} <= set(links)


@pytest.mark.parametrize("name", ["5-ASA", "5-ASA pregnancy", "St. John's wort"])
def test_punctuated_medicine_names_are_selectors(name):
    assert scientific_selector(name)


@pytest.mark.parametrize(
    "query",
    [
        "levetiracetam seizures pregnancy",
        "febrile seizures children ibuprofen",
        "postpartum depression",
        "St. John's wort breastfeeding",
        "5-ASA pregnancy",
    ],
)
def test_tool_search_text_is_not_blocked(query):
    @audited
    async def search_literature(query: str):
        return {"source": "test", "reached": True}

    out = asyncio.run(search_literature(query=query))
    assert out.get("reached") is True, out.get("route")


def test_tool_search_text_with_active_event_is_blocked():
    @audited
    async def search_literature(query: str):
        return {"source": "test", "reached": True}

    out = asyncio.run(search_literature(query="my baby is having a seizure"))
    assert out.get("route") == "urgent_help"


def test_perinatal_crisis_lists_maternal_hotline_with_exact_numbers():
    out = route("I feel hopeless since giving birth.")
    assert out["route"] == "mental_health_support"
    assert "1-833-TLC-MAMA (1-833-852-6262)" in out["message"]
    hotline = next(r for r in out["referrals"] if "Maternal Mental Health" in r["name"])
    assert hotline["call"] == hotline["text"] == "1-833-852-6262"
    assert hotline["phone_link"] == "tel:18338526262"
    assert hotline["sms_link"] == "sms:18338526262"
    assert "https://mchb.hrsa.gov/national-maternal-mental-health-hotline" in out["source_urls"]
    # 988 stays first; the maternal line is added, not substituted.
    assert out["referrals"][0]["call"] == "988"


def test_non_perinatal_crisis_does_not_add_maternal_hotline():
    out = route("I want to harm myself.")
    assert "852-6262" not in out["message"]
    assert all("Maternal" not in r["name"] for r in out["referrals"])


@pytest.mark.parametrize(
    "question",
    [
        "I feel hopeless since giving birth.",
        "I've felt hopeless ever since I had my baby.",
        "I feel hopeless and I'm nursing.",
        "I feel hopeless. I gave birth last month.",
    ],
)
def test_postpartum_wording_variants_get_perinatal_referrals(question):
    out = route(question)
    assert "1-833-852-6262" in out["message"]
    assert "1-800-944-4773" in out["message"]
