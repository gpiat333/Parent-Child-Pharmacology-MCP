"""Behavioral safeguards for the post-review protocol, including adversarial wrappers."""

import asyncio
import json
from pathlib import Path

import pytest

from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.core.population import registry_band_matches
from parent_child_pharmacology.core.response import normalize
from parent_child_pharmacology.core.safety import route
from parent_child_pharmacology.models.inputs import INPUT_MODELS


@pytest.mark.parametrize(
    "question",
    [
        "I am postpartum and feel hopeless. Is sertraline compatible with breastfeeding?",
        "My baby would be better off without me. What about my medication?",
        "I want to kill myself with my tablets.",
        "I am afraid I might hurt my baby. Can I take sertraline?",
        "I have postpartum depression and cannot go on.",
        "Can sertraline treat my postpartum psychosis?",
        "I hear voices telling me to harm my infant.",
        "I gave birth last week and think my baby is possessed.",
        "How much sertraline would make me never wake up?",
        "I took an intentional overdose. Can I breastfeed?",
        "I am planning to overdose and want medication information.",
        "I want to take all my pills.",
        "I intend to overdose on my medication.",
        "I might shake my baby. Can I take sertraline?",
        "I want to harm my infant but only want the drug evidence.",
    ],
)
def test_crisis_stops_before_retrieval(question):
    calls = []

    @audited
    async def retrieve(drug):
        calls.append(drug)
        return {"results": ["must not happen"]}

    out = asyncio.run(retrieve(question))
    assert calls == []
    assert out["route"] == "mental_health_support"
    assert not out["allow_research"] and not out["allow_model_answer"]
    assert out["clinical_assessment_performed"] is False
    assert "988" in out["message"] and "call or text" in out["message"]
    assert "911" in out["message"]
    assert out["retrieval_provenance"] == []


def test_perinatal_callback_is_not_crisis_line():
    out = route("I have postpartum depression and feel hopeless.")
    assert "1-800-944-4773" in out["message"]
    assert "not a crisis line" in out["message"]


def test_non_us_crisis_does_not_invent_local_numbers():
    out = route("I want to harm myself", country="CA")
    assert not out["allow_research"]
    assert "988" not in out["message"] and "911" not in out["message"]


@pytest.mark.parametrize(
    "q",
    [
        "My infant swallowed my pills",
        "My baby cannot breathe",
        "I took a double dose of my medicine",
    ],
)
def test_urgent_is_actionable_without_triage(q):
    out = route(q)
    assert out["route"] in {"urgent_help", "poison_help"}
    assert "1-800-222-1222" in out["message"] and "911" in out["message"]
    assert out["clinical_assessment_performed"] is False
    assert "severity" not in out and "risk_score" not in out


@pytest.mark.parametrize(
    "q",
    [
        "¿Debo dejar mi medicamento?",
        "Puedo tomar sertralina durante la lactancia",
        "Que dosis debo dar a mi bebe",
        "Je souhaite des informations sur ce médicament",
        "Czy mogę brać ten lek podczas karmienia?",
        "我可以服用这种药吗？",
        "Please show evidence for sertraline. Quiero tomar todas mis pastillas.",
        "xyz qqq zzzz",
    ],
)
def test_language_fails_closed(q):
    out = route(q)
    assert not out["allow_research"]
    assert out["route"] in {"language_support", "mental_health_support"}


def test_detector_failure_fails_closed(monkeypatch):
    from parent_child_pharmacology.core import language

    monkeypatch.setattr(language, "detector", lambda: (_ for _ in ()).throw(RuntimeError()))
    assert route("What evidence supports this medication?")["route"] == "language_support"


@pytest.mark.parametrize(
    "payload",
    [
        {"results": []},
        {"sections": {}},
        {"articles": []},
        {"text": ""},
        {"topics": [], "drug_info": []},
        {"top_reactions": []},
        {"ingredient_evidence": [{"label": {"sections": {}}, "literature": {"results": []}}]},
        {"error": "source_unavailable"},
    ],
)
def test_empty_field_cannot_be_dropped_by_model(payload):
    out = normalize(payload)
    assert out["evidence_status"]["no_evidence_retrieved"] is True
    assert out["evidence_status"]["not_evidence_of_safety"] is True
    assert out["evidence_status"]["message"] == "No evidence retrieved; not evidence of safety."


def test_some_sources_empty_is_not_all_empty():
    out = normalize(
        {
            "ingredient_evidence": [
                {"label": {"sections": {}}, "literature": {"results": [{"pmid": "123"}]}}
            ]
        }
    )
    assert out["evidence_status"]["no_evidence_retrieved"] is False
    assert out["ingredient_evidence"][0]["label"]["evidence_status"]["no_evidence_retrieved"]


@pytest.mark.parametrize("section", ["pregnancy", "lactation", "pediatric_use", "Drug Levels"])
def test_dose_paths_and_old_categories(section):
    out = normalize(
        {
            "sections": {
                section: "Pregnancy Category C. Subjects received 10 mg daily; administration was oral."
            }
        }
    )
    flags = out["content_flags"]
    assert "/sections/" + section in flags["dose_or_administration"]["field_paths"]
    assert flags["removed_pregnancy_letter_categories"]["matches"][0]["category"] == "C"
    assert flags["removed_pregnancy_letter_categories"]["classification_current"] is False
    assert out["sections"][section].startswith("Pregnancy Category C")


@pytest.mark.parametrize("band", ["neonate", "infant", "child", "adolescent"])
def test_population_enum_preserves_band(band):
    from parent_child_pharmacology.core.population import preserve_population

    for name in [
        "search_literature",
        "search_trials",
        "medication_evidence_brief",
        "find_mprint_records",
    ]:
        population = INPUT_MODELS[name].model_json_schema()["properties"]["population"]
        # search_trials allows an omitted population, so its enum sits under anyOf.
        enum = population.get("enum") or population["anyOf"][0]["enum"]
        assert band in enum
    assert preserve_population({}, band)["requested_age_band"] == band
    assert preserve_population({}, band)["population_coverage"]["source_band_confirmed"] is False


def test_preterm_neonate_and_adolescent_not_interchangeable():
    teen = {"minimumAge": "12 Years", "maximumAge": "17 Years", "stdAges": ["CHILD"]}
    newborn = {"minimumAge": "0 Days", "maximumAge": "27 Days", "stdAges": ["CHILD"]}
    assert registry_band_matches(teen, "adolescent")
    assert not registry_band_matches(teen, "neonate")
    assert registry_band_matches(newborn, "neonate")
    assert not registry_band_matches(newborn, "adolescent")
    assert not registry_band_matches({"stdAges": ["CHILD"]}, "infant")


def test_pregnancy_coverage_notice_is_scoped_finding():
    out = normalize({"population": "pregnancy", "results": []})
    assert out["pregnancy_coverage_notice"]["evidence_sources"] == [
        "product labeling",
        "primary literature",
    ]
    assert "prototype" in out["pregnancy_coverage_notice"]["message"]
    assert "pregnancy_coverage_notice" in normalize(
        {"sections": {"pregnancy": "Source label text"}}
    )


def test_faers_counts_have_machine_readable_caveats(monkeypatch):
    from parent_child_pharmacology.services import labels_safety as tool

    async def reactions(*args):
        return [{"term": "HEADACHE", "count": 5}]

    monkeypatch.setattr(tool.src, "faers_top_reactions", reactions)
    out = asyncio.run(tool.get_adverse_event_signals("sertraline"))
    caveat = out["report_count_interpretation"]
    assert not caveat["establishes_causation"] and not caveat["exposure_denominator_available"]
    assert not caveat["incidence_or_risk_calculable"]


def test_spanish_medlineplus_uses_id_and_language(monkeypatch):
    from parent_child_pharmacology.services import labels_safety as tool

    calls = []

    async def drug(rxcui, language="en"):
        calls.append((rxcui, language))
        return [{"title": "Spanish education", "url": "https://medlineplus.gov/spanish/"}]

    async def forbidden(*args):
        raise AssertionError("No free-text Spanish lookup")

    monkeypatch.setattr(tool.src, "medlineplus_drug", drug)
    monkeypatch.setattr(tool.src, "medlineplus_topics", forbidden)
    out = asyncio.run(tool.get_patient_education("sertraline", "36437", "es"))
    assert calls == [("36437", "es")] and out["language"] == "es"
    assert (
        asyncio.run(tool.get_patient_education("sertraline", None, "es"))["error"]
        == "spanish_requires_rxcui"
    )


def test_combination_fans_out_all_sources(monkeypatch):
    from parent_child_pharmacology.services import composite as c

    calls = {key: [] for key in ["label", "literature", "faers", "trials", "education", "lactmed"]}

    async def norm(*args):
        return {
            "found": True,
            "requires_confirmation": False,
            "ingredients": ["amoxicillin", "clavulanate"],
        }

    monkeypatch.setattr(c.src, "rxnorm_normalize", norm)
    for key, name in [
        ("label", "get_label_sections"),
        ("literature", "search_literature"),
        ("faers", "get_adverse_event_signals"),
        ("trials", "search_trials"),
        ("education", "get_patient_education"),
        ("lactmed", "search_lactmed"),
    ]:

        def factory(k):
            async def fake(drug, *args):
                calls[k].append(drug)
                return {"results": []}

            return fake

        monkeypatch.setattr(c, name, factory(key))
    out = asyncio.run(c.medication_evidence_brief("Augmentin"))
    assert all(
        len(v) == 2 and v[0].startswith("amoxicillin") and v[1].startswith("clavulanate")
        for v in calls.values()
    )
    assert out["ingredient_coverage"]["all_normalized_ingredients_queried"]
    assert out["evidence_status"]["no_evidence_retrieved"]
    assert len(out["questions_to_ask_clinician"]) >= 4


def test_protocol_has_two_mprint_tools_and_clinician_prompt():
    from parent_child_pharmacology.app import mcp

    tools = {x.name for x in asyncio.run(mcp.list_tools())}
    assert len(tools) == 21
    assert {x for x in tools if "mprint" in x} == {"find_mprint_records", "get_mprint_details"}
    assert "medication_evidence_brief" in tools and "medication_safety_brief" not in tools
    prompts = {x.name for x in asyncio.run(mcp.list_prompts())}
    assert len(prompts) == 4 and "questions_to_ask_clinician" in prompts
    assert "search_parent_input_opportunities" not in tools


@pytest.mark.parametrize(
    "table,kind",
    [("gold_outcomes", "any"), ("gold_PE_CT", "PE_CT"), ("gold_PK_summary", "PK_summary")],
)
def test_mprint_table_dispatch(monkeypatch, table, kind):
    from parent_child_pharmacology.services import mprint

    calls = []

    async def gold(*args):
        calls.append(args)
        return {"outcomes": []}

    monkeypatch.setattr(mprint.mprint_data, "gold_outcomes", gold)
    out = asyncio.run(mprint.get_mprint_details("123", table, 5, 0))
    assert calls == [("123", kind, 5, 0)] and out["requested_table"] == table


def test_mprint_silver_is_distinct(monkeypatch):
    from parent_child_pharmacology.services import mprint

    calls = []

    async def silver(pmids):
        calls.append(pmids)
        return {"classifications": []}

    monkeypatch.setattr(mprint.mprint_data, "silver_classifications", silver)
    out = asyncio.run(mprint.get_mprint_details("123", "silver_classifications"))
    assert calls == [["123"]] and out["requested_table"] == "silver_classifications"


def test_negative_compound_advice_exclusion_does_not_trigger_refusal():
    q = "What evidence exists for sertraline during breastfeeding? Do not provide medication decisions or doses."
    assert route(q, language_required=False)["allow_research"]
    assert not route(q + " But what dose should I give?", language_required=False)["allow_research"]


def test_direct_spanish_sentence_cannot_hide_in_drug_argument():
    calls = []

    @audited
    async def retrieve(drug):
        calls.append(drug)
        return {"results": []}

    out = asyncio.run(retrieve("Puedo tomar sertralina durante la lactancia"))
    assert not calls and out["route"] == "language_support"


def test_untriggered_policy_reference_not_added_as_retrieved_source():
    out = normalize(route("I feel hopeless since giving birth"))
    assert not any("fda.gov" in url for url in out["source_urls"])
    assert out["retrieval_provenance"] == []


def test_short_ambiguous_technical_phrase_is_conservatively_blocked():
    assert route("Patient education about sertraline")["route"] == "language_support"
