import pytest

from parent_child_pharmacology.mc.parent_safety import route


@pytest.mark.parametrize(
    "suffix",
    [
        "Do not give a dose.",
        "Don't give any doses.",
        "Do not provide dosing advice.",
        "Do not include a dosage.",
        "Do not give a taper plan.",
    ],
)
def test_research_excludes_advice_without_refusal(suffix):
    assert route("Compare label side effects with breastfed infant findings. " + suffix)[
        "allow_research"
    ]


@pytest.mark.parametrize(
    "question",
    [
        "Do not give a dose. But what dose should I give my child?",
        "Don't give any doses. Should I stop my medication?",
        "Do not provide dosing advice. My baby is not breathing.",
        "Do not give a dose. I took the wrong medicine.",
        "Do not give a dose. What is my little white pill?",
    ],
)
def test_exclusion_does_not_hide_other_risk(question):
    assert not route(question)["allow_research"]


def test_wrong_medicine_with_article_routes_before_research():
    result = route("I took the wrong medicine")
    assert result["route"] == "poison_help"
    assert not result["allow_research"]


def test_blood_pressure_description_does_not_identify_drug():
    assert route("What is my blood pressure medicine called?")["route"] == "confirm_identity"


def test_named_medicine_research_remains_available():
    assert route("Find breastfeeding evidence for nifedipine")["allow_research"]
