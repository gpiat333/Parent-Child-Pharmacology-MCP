import asyncio

import pytest

from parent_child_pharmacology.clients.pllr import parse_pllr
from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.core.evidence_axes import build_axes
from parent_child_pharmacology.core.literature_strategy import strategy
from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "q",
    [
        "Prepare an evidence brief for sertraline during lactation using the medication evidence brief tool. Include questions to ask my clinician, source links, and missing evidence limitations. Do not provide medication decisions or doses.",
        "Please summarize the pregnancy evidence for daridorexant. Include the missing data. Do not provide medication decisions or doses.",
        "What evidence is available about atogepant during pregnancy? Show evidence gaps and registries without recommending participation.",
        "Prepare a pregnancy evidence brief for daridorexant. Show effects on the pregnant person, measured fetal or infant exposure, and observed fetal or infant outcomes, keeping empty rows visible. State what maternal pharmacokinetic data were retrieved. Show FDA registry contacts separately without recommending participation. Do not provide doses or medication decisions.",
    ],
)
def test_english_context_resolves_technical_fragments(q):
    assert route(q)["allow_research"]


@pytest.mark.parametrize(
    "q",
    [
        "Show sertraline evidence. Quiero tomar todas mis pastillas.",
        "Show sertraline evidence and quiero tomar todas mis pastillas ahora.",
        "Please summarize sertraline. Je veux prendre tous mes comprimés.",
        "Show evidence. No quiero vivir y quiero hacer daño a mi bebé.",
        "Puedo tomar sertralina durante la lactancia",
    ],
)
def test_foreign_fragment_does_not_inherit_english_context(q):
    assert not route(q)["allow_research"]


def test_pllr_sections_and_dose_context_do_not_merge():
    xml = """<document xmlns="urn:hl7-org:v3"><section><title>8.1 Pregnancy</title><text>
 <paragraph>Risk Summary</paragraph><paragraph>Insufficient human data.</paragraph>
 <paragraph>Clinical Considerations</paragraph><paragraph>Dose adjustments during pregnancy and the postpartum period</paragraph><paragraph>Pregnancy increases clearance in a source study.</paragraph>
 <paragraph>Maternal adverse reactions</paragraph><paragraph>Maternal hypotension was reported.</paragraph>
 <paragraph>Data</paragraph><paragraph>Animal Data</paragraph><paragraph>Rats had fetal findings.</paragraph>
 </text></section></document>"""
    result = parse_pllr(xml)
    assert result["subsections"]["risk_summary"]["text"] == "Insufficient human data."
    assert "clearance" in result["maternal_dose_adjustment"]["dose_adjustment_text"]
    assert "Rats" not in result["subsections"]["clinical_considerations"]["text"]
    assert result["maternal_dose_adjustment"]["personal_dosing_instruction"] is False
    assert "Rats" in result["subsections"]["data"]["text"]


def test_clinical_considerations_without_pk_are_not_pk():
    pllr = parse_pllr(
        pregnancy_text="Risk Summary\nInsufficient human data.\nClinical Considerations\nMaternal adverse reactions\nHypotension was reported.\nData\nAnimal studies are described."
    )
    axes, pk = build_axes(
        {"label": {"pllr_8_1": pllr, "url": "https://example.gov/label"}}, "pregnancy"
    )
    assert pllr["subsections"]["clinical_considerations"]["found"]
    assert not pllr["maternal_dose_adjustment"]["dose_adjustment_data_found"]
    assert pk["no_data_found"] and "No maternal pharmacokinetic data" in pk["message"]
    assert len(axes) == 3


@pytest.mark.parametrize("population", ["pregnancy", "lactation"])
def test_empty_axes_are_visible(population):
    axes, pk = build_axes({}, population)
    assert len(axes) == 3
    assert all(
        a["items"] == [] and a["empty_message"] and a["not_evidence_of_safety"] for a in axes
    )


def test_prediction_and_animal_findings_not_measured_human_exposure():
    row = {
        "literature": {
            "articles": [
                {
                    "pmid": "1",
                    "title": "Model",
                    "abstract": "A model predicted fetal concentration. In rats, fetal malformations were observed.",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/1/",
                }
            ]
        }
    }
    axes, _ = build_axes(row, "pregnancy")
    a = {x["axis"]: x for x in axes}
    assert not a["fetal_infant_exposure"]["items"] and a["fetal_infant_exposure"]["context_only"]
    assert not a["fetal_infant_outcomes"]["items"] and a["fetal_infant_outcomes"]["context_only"]


def test_maternal_pk_preserves_source_and_explicit_gap():
    row = {
        "literature": {
            "articles": [
                {
                    "pmid": "1",
                    "title": "Study",
                    "abstract": "Pregnant women had increased drug clearance. No maternal pharmacokinetic data were available in a comparison cohort.",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/1/",
                }
            ]
        }
    }
    _, pk = build_axes(row, "pregnancy")
    assert not pk["no_data_found"] and len(pk["items"]) == 1 and len(pk["reported_gaps"]) == 1
    assert pk["items"][0]["pmid"] == "1" and not pk["personal_dose_calculated"]


@pytest.mark.parametrize("population", ["pregnancy", "lactation"])
def test_curated_query_not_raw_syntax(population):
    s = strategy("sertraline evidence", population, "maternal_pharmacokinetics")
    assert s["concept_terms"] == ["sertraline"]
    assert "[MeSH Terms]" in s["pubmed_query"] and "[Title/Abstract]" in s["pubmed_query"]
    assert "Pharmacokinetics" in s["pubmed_query"] and s["date_restriction"] is None
    assert s["population"] == population


def test_all_years_for_pregnancy_avoids_arbitrary_recent_only_gap():
    from parent_child_pharmacology.clients.pubmed import pubmed_search_params

    assert "reldate" not in pubmed_search_params("daridorexant", "pregnancy")
    assert "reldate" in pubmed_search_params("epilepsy", "child")


@pytest.mark.parametrize(
    "name",
    [
        "find_pregnancy_exposure_registries",
        "find_recruiting_studies",
        "search_parent_input_opportunities",
    ],
)
@pytest.mark.parametrize(
    "question", ["my little white pill", "I feel hopeless postpartum", "My infant swallowed pills"]
)
def test_participation_stops_without_upstream_calls(name, question):
    calls = []

    async def operation(drug):
        calls.append(drug)
        return {"results": [{"title": "must not appear"}]}

    operation.__name__ = name
    out = asyncio.run(audited(operation)(question))
    assert calls == [] and out["participation"]["suppressed"]
    assert not out["allow_research"]


def test_registry_tool_returns_contacts_and_nonrecommendation(monkeypatch):
    from parent_child_pharmacology.services import parent_resources as p

    async def fake(*a):
        return {
            "source": "live:fda-registry-directory",
            "url": "https://www.fda.gov/directory",
            "results": [
                {
                    "registry": "Z registry",
                    "contact_text": "Public contact",
                    "links": [{"url": "https://api.fda.gov/"}],
                },
                {"registry": "A registry"},
            ],
        }

    monkeypatch.setattr(p.parents, "pregnancy_registries", fake)
    out = asyncio.run(p.find_pregnancy_exposure_registries("drug"))
    assert out["tier"] == "participation" and not out["ranked"] and not out["recommended"]
    assert out["results"][0]["registry"] == "A registry"
    assert out["non_recommendation_statement"]


def test_pllr_missing_headings_remain_null():
    result = parse_pllr(pregnancy_text="Pregnancy Category C. See Data in the source.")
    assert result["parse_status"] == "headings_not_found"
    assert all(v["text"] is None for v in result["subsections"].values())


def test_animal_context_applies_to_subsequent_sentences():
    pllr = parse_pllr(
        pregnancy_text="Risk Summary\nNo human data are available.\nData\nAnimal Data\nPregnant rats were studied. The drug did not cause fetal malformations."
    )
    axes, _ = build_axes(
        {"label": {"pllr_8_1": pllr, "url": "https://example.gov/label"}}, "pregnancy"
    )
    row = next(a for a in axes if a["axis"] == "fetal_infant_outcomes")
    assert not row["items"]
    assert row["context_only"][0]["study_context"] == "animal_label_data"


@pytest.mark.parametrize(
    "query",
    ["levetiracetam", "levetiracetam breastfeeding", "pediatric epilepsy", "pregnancy research"],
)
def test_structured_medicine_selector_is_not_a_language_sentence(query):
    calls = []

    @audited
    async def search_literature(query):
        calls.append(query)
        return {"results": []}

    out = asyncio.run(search_literature(query))
    assert calls == [query] and out.get("allow_research") is not False


def test_spanish_sentence_in_selector_still_stops():
    calls = []

    @audited
    async def search_literature(query):
        calls.append(query)
        return {"results": []}

    out = asyncio.run(search_literature("Puedo tomar sertralina durante la lactancia"))
    assert not calls and out["route"] == "language_support"
