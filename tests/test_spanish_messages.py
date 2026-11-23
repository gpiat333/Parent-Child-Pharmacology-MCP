"""Reviewed Spanish safety messages: returned as fixed text when someone writes in Spanish."""

import json
from pathlib import Path

import pytest

from parent_child_pharmacology.core.safety import route

POLICY = json.loads(
    (Path(__file__).parents[1] / "src/parent_child_pharmacology/core/policy.json").read_text(
        encoding="utf-8"
    )
)
ES = POLICY["messages_es"]


def test_spanish_messages_are_enabled_with_a_recorded_review():
    review = POLICY["spanish_referral_review"]
    assert review["new_spanish_safety_strings_enabled"] is True
    assert "native Spanish speaker" in review["review"] and "November 23, 2026" in review["review"]
    assert "Spanish questions still stop" in review["scope"]


def test_every_spanish_message_keeps_the_verified_numbers():
    assert "988 y presione 2" in ES["crisis_us"] and "AYUDA al 988" in ES["crisis_us"]
    assert "1-833-852-6262" in ES["maternal_hotline"]
    assert "1-800-944-4773" in ES["perinatal_support"]
    assert "1-800-222-1222" in ES["poison"] and "911" in ES["urgent"]
    assert "866-626-6847" in ES["mothertobaby"] and "mothertobaby.org/es" in ES["mothertobaby"]
    for text in ES.values():
        assert text.strip() and "TODO" not in text


@pytest.mark.parametrize(
    "question",
    ["¿Puedo tomar ibuprofeno durante el embarazo?", "¿Es seguro amamantar con sertralina?"],
)
def test_spanish_question_stops_with_the_spanish_message(question):
    r = route(question)
    assert r["allow_research"] is False and r["route"] == "language_support"
    assert r["message_es"] == ES["language_support"]
    assert "Este servicio todavía no puede responder preguntas en español" in r["message_es"]
    assert r["disclaimer_es"] == ES["disclaimer"]
    assert r["message"]  # the English message stays alongside


def test_spanish_crisis_gets_the_spanish_crisis_message():
    r = route("Quiero morir")
    assert r["route"] == "mental_health_support"
    assert r["message_es"].startswith(ES["crisis_us"])


def test_spanish_perinatal_crisis_adds_maternal_hotline_in_spanish():
    r = route("Quiero morir, estoy embarazada")
    assert r["route"] == "mental_health_support"
    assert ES["maternal_hotline"] in r["message_es"] and ES["perinatal_support"] in r["message_es"]


def test_english_questions_get_no_spanish_message():
    for q in ["Can I take ibuprofen while breastfeeding?", "I feel hopeless since giving birth."]:
        assert "message_es" not in route(q)


def test_english_messages_use_the_service_voice():
    m = POLICY["messages"]
    for key in [
        "crisis_us",
        "dose_decision",
        "unclear_medicine",
        "personal_question",
        "language_support",
        "vaccine_decision",
        "instruction_override",
        "off_topic",
    ]:
        assert "This service" in m[key], key
        assert not m[key].startswith("I ")
