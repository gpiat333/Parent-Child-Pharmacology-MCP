"""'Can I take X?' gets what is known plus a clear handoff; real decisions still stop."""

import pytest

from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "question",
    [
        "Can I take sertraline while breastfeeding?",
        "Could I take ibuprofen while pregnant?",
        "Can I take ibuprofen?",
        "Can I still take lamotrigine while nursing?",
    ],
)
def test_can_i_take_gets_evidence_with_a_decision_handoff(question):
    out = route(question)
    assert out["route"] == "evidence" and out["allow_research"] is True
    assert out["personal_question"] is True
    assert "can't tell you whether to take it" in out["message"]
    assert "clinician or pharmacist" in out["message"]
    assert "Never answer yes or no" in out["answer_framing"]


def test_pregnancy_or_breastfeeding_self_question_adds_mothertobaby():
    out = route("Can I take sertraline while breastfeeding?")
    assert "866-626-6847" in out["message"]
    assert out["referrals"][0]["call"] == "866-626-6847"


def test_general_self_question_has_no_mothertobaby():
    out = route("Can I take ibuprofen?")
    assert "MotherToBaby" not in out["message"]


@pytest.mark.parametrize(
    "question",
    [
        "Can I take sertraline? What dose should I use?",
        "Should I stop my sertraline now that I am pregnant?",
        "How much ibuprofen can I give my 2 year old?",
        "Can I give my baby Tylenol?",
        "Can I take double my dose tonight?",
        "Should I switch from sertraline to another medicine?",
    ],
)
def test_real_treatment_decisions_still_stop(question):
    out = route(question)
    assert out["route"] == "clinician_or_pharmacist" and out["allow_research"] is False
    assert "personal_question" not in out


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("I want to harm myself. Can I take sertraline?", "mental_health_support"),
        ("Can I take my little white pill while breastfeeding?", "confirm_identity"),
        ("My baby is having a seizure. Can I take lamotrigine?", "urgent_help"),
        ("Puedo tomar sertralina durante la lactancia", "language_support"),
    ],
)
def test_stop_routes_take_priority_and_drop_the_personal_framing(question, expected):
    out = route(question)
    assert out["route"] == expected
    assert "personal_question" not in out
