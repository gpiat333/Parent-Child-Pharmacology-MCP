"""Policy .22: vaccine names, adult and off-label sources, PRGLAC list, Spanish and supplement resources."""

import asyncio

import pytest

from parent_child_pharmacology.clients.dailymed import parse_approved_use_sections
from parent_child_pharmacology.clients.lactmed import VACCINE_TITLES, snapshot_title_match
from parent_child_pharmacology.core.referrals import (
    OFF_LABEL_CONTEXT,
    PRGLAC_CONTEXT,
    SPANISH_RESOURCES,
)
from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "name,title",
    [
        ("flu vaccine", "Influenza Vaccines"),
        ("flu shot", "Influenza Vaccines"),
        ("Tdap", "Diphtheria-Tetanus-Pertussis Vaccines"),
        ("MMR vaccine", "Measles-Mumps-Rubella Vaccine"),
        ("covid shot", "COVID-19 Vaccines"),
        ("RSV vaccine", "Respiratory Syncytial Virus Vaccine"),
        ("sertraline", "Sertraline"),
        ("Fenugreek", "Fenugreek"),
    ],
)
def test_common_names_match_lactmed_titles(name, title):
    assert snapshot_title_match(name) == title


def test_every_vaccine_alias_points_to_a_bundled_lactmed_record():
    for title in set(VACCINE_TITLES.values()):
        assert snapshot_title_match(title) == title


def test_unknown_names_do_not_match():
    assert snapshot_title_match("Tylenol") is None
    assert snapshot_title_match("") is None


def test_search_lactmed_uses_the_matched_title(monkeypatch):
    from parent_child_pharmacology.services import lactation

    seen = []

    async def fake(term, n):
        seen.append(term)
        return [{"id": "1", "title": term}]

    monkeypatch.setattr(lactation.src, "lactmed_search", fake)
    out = asyncio.run(lactation.search_lactmed("flu vaccine", 3))
    assert seen == ["Influenza Vaccines"]
    assert out["matched_lactmed_title"] == "Influenza Vaccines"


def test_rxnorm_explains_vaccine_names(monkeypatch):
    from parent_child_pharmacology.clients import rxnorm

    class R:
        def __init__(self, body):
            self.body = body

        def json(self):
            return self.body

    async def fake(method, url, params=None, ttl=None):
        return R({"idGroup": {}} if url.endswith("rxcui.json") else {"approximateGroup": {}})

    monkeypatch.setattr(rxnorm.http, "request", fake)
    out = asyncio.run(rxnorm.rxnorm_normalize("flu vaccine"))
    assert out["found"] is False
    assert "brand name on the vaccine record" in out["note"]


def test_approved_use_sections_parse_indications_and_studies():
    xml = """<document xmlns="urn:hl7-org:v3"><component><structuredBody>
    <component><section><code code="34067-9"/><title>1 INDICATIONS AND USAGE</title>
    <text>Exampledrug is indicated for major depressive disorder in adults.</text></section></component>
    <component><section><code code="34092-7"/><title>14 CLINICAL STUDIES</title>
    <text>Two trials in adults.</text></section></component>
    </structuredBody></component></document>"""
    out = parse_approved_use_sections(xml)
    assert "indicated" in out["indications_and_usage"]["text"]
    assert out["clinical_studies"]["text"] == "Two trials in adults."


def test_off_label_context_points_to_bpca_priority_list_without_recommending():
    urls = [s.get("url") for s in OFF_LABEL_CONTEXT["where_to_look"]]
    assert "https://www.nichd.nih.gov/research/supported/bpca/recent-priority-lists" in urls
    assert "does not establish a dose" in OFF_LABEL_CONTEXT["not_a_recommendation"]


def test_prglac_context_lists_fifteen_recommendations_with_source():
    recs = PRGLAC_CONTEXT["recommendations"]
    assert len(recs) == 15
    assert [r.split(".")[0] for r in recs] == [str(i) for i in range(1, 16)]
    assert PRGLAC_CONTEXT["recommendations_source"].endswith("/PRGLAC/recommendations")


@pytest.mark.parametrize(
    "question",
    ["¿Puedo tomar ibuprofeno durante el embarazo?", "¿Es seguro amamantar con sertralina?"],
)
def test_spanish_questions_stop_but_get_spanish_services(question):
    r = route(question)
    assert r["route"] == "language_support" and r["allow_research"] is False
    names = [x["name"] for x in r["referrals"]]
    assert "MotherToBaby (Spanish service)" in names
    assert any("988" in n for n in names)
    assert r["spanish_resources"] == SPANISH_RESOURCES


def test_spanish_crisis_gets_spanish_988():
    r = route("Quiero morir")
    assert r["route"] == "mental_health_support"
    assert any(x.get("text") == "AYUDA to 988" for x in r["referrals"])


def test_french_question_stops_without_spanish_referrals():
    r = route("Puis-je prendre du paracétamol pendant la grossesse?")
    assert r["allow_research"] is False
    assert "spanish_resources" not in r


@pytest.mark.parametrize(
    "question",
    ["Can I drink chamomile tea while pregnant?", "Is this herbal supplement safe while nursing?"],
)
def test_supplement_questions_get_supplement_context(question):
    r = route(question)
    assert r["allow_research"] is True
    assert "LactMed covers many herbs" in r["supplement_context"]["note"]
