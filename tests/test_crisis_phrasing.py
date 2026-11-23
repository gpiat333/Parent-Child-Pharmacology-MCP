"""Crisis wording found in hands-on probing that earlier patterns let through as research."""

import pytest

from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "question",
    [
        "I keep thinking about hurting my baby",
        "I feel like harming my baby",
        "i dont want to be alive anymore",
        "I do not want to be here anymore",
        "thinking about ending things",
        "I am thinking of ending it all",
    ],
)
def test_crisis_wording_routes_to_support(question):
    result = route(question)
    assert result["route"] == "mental_health_support"
    assert result["allow_research"] is False
    assert "988" in result["message"]


@pytest.mark.parametrize(
    "question",
    ["quiero hacerme daño", "quiero matar a mi bebé", "quiero matar a mi bebe"],
)
def test_spanish_crisis_wording_gets_the_crisis_route_and_spanish_message(question):
    result = route(question)
    assert result["route"] == "mental_health_support"
    assert result["allow_research"] is False
    assert "988" in result["message_es"]


@pytest.mark.parametrize(
    "question",
    [
        "What lactation evidence is available for sertraline?",
        "Does stopping sertraline at the end of pregnancy change infant outcomes?",
        "What studies report on ending breastfeeding early because of a medicine?",
        "Is there research on sertraline and infant sleep?",
    ],
)
def test_research_questions_still_reach_evidence(question):
    result = route(question)
    assert result["route"] == "evidence"
    assert result["allow_research"] is True


@pytest.mark.parametrize(
    "question",
    [
        "sertraline",
        "lamotrigine breastfeeding levels",
        "antidepressants in milk",
        "Zoloft nursing",
        "codeine infants",
        "levetiracetam pregnancy pharmacokinetics",
        "flu vaccine breastfeeding",
    ],
)
def test_short_english_topic_phrases_are_not_language_blocked(question):
    result = route(question)
    assert result["route"] == "evidence" and result["allow_research"] is True


@pytest.mark.parametrize(
    "question",
    [
        "sertralina lactancia",
        "ibuprofeno embarazo",
        "Ibuprofen Stillzeit",
        "médicament grossesse",
        "tomar sertralina",
        "Puedo tomar sertralina durante la lactancia",
    ],
)
def test_short_foreign_phrases_still_stop(question):
    result = route(question)
    assert result["route"] == "language_support" and result["allow_research"] is False
