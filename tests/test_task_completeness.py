"""Source-completeness regressions; no network or clinical correctness claims."""

import asyncio

import httpx
import pytest

from parent_child_pharmacology.clients import dailymed, lactmed, reporter
from parent_child_pharmacology.core.evidence_axes import build_axes
from parent_child_pharmacology.core.output_notices import format_required_notices


@pytest.mark.parametrize("limit", [500, 6000, 16000, 20000])
def test_long_exposure_section_does_not_crowd_out_other_lactmed_sections(limit):
    sections = {h: (h + " source sentence. ") * 1000 for h in lactmed.EXPECTED_CLINICAL_SECTIONS}
    out = lactmed.lactmed_payload(sections, limit)
    assert len(out["text"]) <= limit
    assert set(out["sections_returned"]) == set(sections)
    assert not out["sections_omitted_by_limit"]
    assert all(v["truncated"] for v in out["section_status"].values())
    for h, piece in out["sections"].items():
        assert sections[h].startswith(piece) and piece
        assert out["section_status"][h]["characters_returned"] == len(piece)


def test_short_sections_return_unused_budget_to_long_sections():
    sections = {
        lactmed.EXPECTED_CLINICAL_SECTIONS[0]: "Brief summary.",
        lactmed.EXPECTED_CLINICAL_SECTIONS[1]: "X" * 3000,
    }
    out = lactmed.lactmed_payload(sections, 500)
    assert len(out["text"]) == 500
    assert out["sections"][lactmed.EXPECTED_CLINICAL_SECTIONS[0]] == "Brief summary."
    assert not out["section_status"][lactmed.EXPECTED_CLINICAL_SECTIONS[0]]["truncated"]
    assert set(out["sections_missing"]) == set(lactmed.EXPECTED_CLINICAL_SECTIONS[2:])


def test_too_small_budget_never_emits_a_partial_heading_or_invented_section():
    out = lactmed.lactmed_payload(
        {h: "A source sentence." for h in lactmed.EXPECTED_CLINICAL_SECTIONS}, 5
    )
    assert out["text"] == "" and not out["sections"]
    assert len(out["sections_omitted_by_limit"]) == 4


def test_lactation_axes_use_section_boundaries_not_long_exposure_text():
    row = {
        "lactmed": lactmed.lactmed_payload(
            {
                "Drug Levels": "Milk concentration was measured in breastfed infant exposure studies. "
                * 500,
                "Effects on Lactation and Breastmilk": "Maternal prolactin increased.",
                "Effects in Breastfed Infants": "No adverse outcomes were reported.",
            },
            500,
        )
    }
    axes, _ = build_axes(row, "lactation")
    a = {x["axis"]: x for x in axes}
    assert a["maternal_effects"]["items"][0]["text"] == "Maternal prolactin increased."
    assert all("Milk concentration" not in x["text"] for x in a["maternal_effects"]["items"])
    assert a["fetal_infant_exposure"]["items"]


@pytest.mark.parametrize(
    "text",
    [
        "Lactating women provided milk samples; infant serum concentrations were measured.",
        "Maternal treatment was associated with reported infant outcomes.",
    ],
)
def test_offspring_endpoints_do_not_become_maternal_effects(text):
    axes, _ = build_axes(
        {"literature": {"articles": [{"pmid": "1", "abstract": text}]}}, "lactation"
    )
    maternal = next(x for x in axes if x["axis"] == "maternal_effects")
    assert not maternal["items"] and maternal["empty_message"]


def test_actual_maternal_pk_survives_shared_mother_infant_sentence():
    axes, pk = build_axes(
        {
            "literature": {
                "articles": [
                    {
                        "pmid": "1",
                        "abstract": "Maternal plasma concentrations and infant serum concentrations were measured.",
                    }
                ]
            }
        },
        "pregnancy",
    )
    assert axes[0]["items"] and pk["items"]


def test_planned_trial_measurements_are_context_not_observed_exposure():
    axes, pk = build_axes(
        {
            "literature": {
                "articles": [
                    {
                        "pmid": "1",
                        "publication_types": ["Clinical Trial Protocol"],
                        "abstract": "This study will measure maternal clearance and fetal concentrations.",
                    }
                ]
            }
        },
        "pregnancy",
    )
    assert not axes[0]["items"] and not axes[1]["items"]
    assert axes[1]["context_only"][0]["study_context"] == "protocol_not_results"
    assert pk["no_data_found"]


def test_label_tool_retains_adult_and_population_sections_from_same_spl(monkeypatch):
    xml = (
        '<document xmlns="urn:hl7-org:v3"><section><title>8.2 Lactation</title><text>Lactation warning.</text></section><section><title>6 Adverse reactions</title><text>Adult adverse finding.</text></section><section><title>5 Warnings and precautions</title><text>'
        + ("W" * 4100)
        + "</text></section></document>"
    )

    async def request(method, url, **kwargs):
        return (
            httpx.Response(200, text=xml)
            if url.endswith(".xml")
            else httpx.Response(
                200, json={"data": [{"setid": "same-source", "title": "Selected product"}]}
            )
        )

    monkeypatch.setattr(dailymed.http, "request", request)
    out = asyncio.run(dailymed.dailymed_label("medicine"))
    assert out["sections"]["lactation"] == "Lactation warning."
    assert out["medicine_taker_sections"]["adverse_reactions"]["text"] == "Adult adverse finding."
    assert out["medicine_taker_sections"]["warnings_and_precautions"]["truncated"]
    assert "boxed_warning" in out["medicine_taker_sections_missing"]
    assert out["medicine_taker_sections_truncated"]
    assert out["setid"] == "same-source"


@pytest.mark.parametrize("complete", [True, False])
def test_absent_requested_year_count_is_explicit_and_portfolio_unknown_when_capped(
    monkeypatch, complete
):
    async def page(criteria, offset, n):
        return [
            {
                "appl_id": 1,
                "project_num": "P1",
                "core_project_num": "P",
                "fiscal_year": 2025,
                "ic_code": "HD",
                "institute": "NICHD",
                "award_amount_usd": 12,
                "direct_cost_usd": 8,
            }
        ], {"total": 1 if complete else 20}

    monkeypatch.setattr(reporter, "reporter_page", page)
    out = asyncio.run(reporter.research_portfolio("topic", "HD", [2024, 2025], max_projects=1))
    g = next(x for x in out["groups"] if x["fiscal_year"] == 2024)
    assert g["project_records"] == 0 and g["distinct_core_projects"] == 0
    assert all(x is None for x in g["totals_usd"].values())
    assert g["portfolio_project_records"] == (0 if complete else None)
    assert len(out["requested_year_coverage"]) == 2 and out["retrieved_project_records"] == 1
    assert (
        next(x for x in out["groups"] if x["fiscal_year"] == 2025)["totals_usd"]["award_amount_usd"]
        == 12
    )


def test_any_ic_does_not_invent_an_administering_institute_for_empty_year(monkeypatch):
    async def page(*args):
        return [], {"total": 0}

    monkeypatch.setattr(reporter, "reporter_page", page)
    out = asyncio.run(reporter.research_portfolio("topic", fiscal_years=[2024, 2024]))
    assert out["groups"] == [] and len(out["requested_year_coverage"]) == 1
    assert out["requested_year_coverage"][0]["retrieved_project_records"] == 0


def test_faers_population_notice_survives_empty_model_caveats_but_not_policy_stop():
    answer, ids = format_required_notices("Captured report counts.", ["get_adverse_event_signals"])
    assert "faers_population_scope" in ids and "cannot be generalized to all infants" in answer
    assert format_required_notices("Fixed stop.", ["get_adverse_event_signals"], blocked=True) == (
        "Fixed stop.",
        [],
    )


@pytest.mark.parametrize("value", ["0.69 mg/L", "0.4\u20132.3 mcg/L", "<2.5 \u00b5g/mL"])
def test_exposure_values_preserve_exact_concentration_units_and_ranges(value):
    source = "Maternal Levels. Milk concentration was " + value + "."
    out = lactmed.exposure_measurements(source)
    assert out["concentration_passages"][0]["concentration_values_as_reported"] == [value]
    assert out["concentration_passages"][0]["source_passage"] in source
    assert not out["exhaustive"]


def test_exposure_extractor_does_not_convert_regimens_or_relative_doses_to_concentrations():
    out = lactmed.exposure_measurements(
        "Mothers took 500 mg twice daily. Estimated infant dose was 0.1 mg/kg/day, or 2% of maternal dose."
    )
    assert out["concentration_passages"] == []
    assert out["status"] == "no_quantitative_concentrations_extracted"
    assert not out["infant_level_section_present_in_returned_text"]


def test_absent_published_infant_levels_remain_explicit_source_text_not_zero():
    out = lactmed.exposure_measurements(
        "Maternal Levels. Milk concentration was 0.69 mg/L. Infant Levels. Relevant published information was not found as of the revision date."
    )
    assert out["infant_level_section_present_in_returned_text"]
    assert (
        out["infant_level_excerpt"]
        == "Relevant published information was not found as of the revision date."
    )


def test_concentration_context_does_not_invent_a_milk_or_infant_specimen():
    out = lactmed.exposure_measurements(
        "Maternal plasma was sampled. The concentration was 4 ng/mL. Milk samples were not collected."
    )
    passage = out["concentration_passages"][0]
    assert passage["preceding_context"] == "Maternal plasma was sampled."
    assert "specimen" not in passage
    assert passage["concentration_values_as_reported"] == ["4 ng/mL"]


def test_measurement_extraction_does_not_recover_hidden_text_beyond_returned_budget():
    out = lactmed.lactmed_payload(
        {"Drug Levels": ("Earlier source context. " * 200) + "Milk concentration was 9 mg/L."}, 500
    )
    assert out["truncated"] and "9 mg/L" not in out["text"]
    assert not out["exposure_measurements"]["concentration_passages"]


def test_concentration_passage_limit_discloses_additional_material():
    out = lactmed.exposure_measurements(
        " ".join(f"Milk concentration was {i} ng/mL." for i in range(1, 14))
    )
    assert len(out["concentration_passages"]) == 12
    assert out["additional_passages_omitted"]


def test_reference_marker_does_not_merge_a_concentration_with_the_next_dose_sentence():
    out = lactmed.exposure_measurements(
        "Milk concentration was 0.69 mg/L.[2] Estimated infant dosage was 0.1 mg/kg daily."
    )
    passage = out["concentration_passages"][0]
    assert passage["concentration_values_as_reported"] == ["0.69 mg/L"]
    assert passage["source_passage"] == "Milk concentration was 0.69 mg/L."
    assert "dosage" not in passage["source_passage"]


def test_spontaneous_reports_remain_visible_without_becoming_observed_outcomes():
    source = {
        "cohort": "pregnancy",
        "url": "https://example.test/query",
        "cohort_scope": "Query subset only",
        "queried_at_utc": "2026-11-21T00:00:00Z",
        "top_reactions": [
            {
                "reaction": "NEONATAL HYPOTONIA",
                "reports": 9,
                "population_context": {"source_population": "not_established"},
            }
        ],
    }
    axes, _ = build_axes({"adverse_events": source}, "pregnancy")
    outcome = axes[2]
    assert not outcome["items"] and not outcome["outcome_or_effect_passages_retrieved"]
    assert outcome["state"] == "report_context_only" and not outcome["no_evidence_retrieved"]
    assert outcome["not_evidence_of_safety"] and "retrieved separately" in outcome["empty_message"]
    context = outcome["report_only_context"][0]
    assert context["reported_terms"] == source["top_reactions"]
    assert context["url"] == source["url"] and context["queried_at_utc"] == source["queried_at_utc"]
    assert not context["source_population_confirmed"] and not context["confirmed_clinical_outcomes"]
    assert not context["establishes_causation"] and not context["exposure_denominator_available"]
    assert not context["incidence_or_risk_calculable"]
    assert all(not axis["report_only_context"] for axis in axes[:2])
    context["reported_terms"][0]["reports"] = 99
    assert source["top_reactions"][0]["reports"] == 9


@pytest.mark.parametrize(
    "source",
    [
        {},
        {"top_reactions": []},
        {"error": "source_unavailable", "top_reactions": [{"reaction": "STALE", "reports": 9}]},
    ],
)
def test_absent_or_failed_report_retrieval_does_not_invent_signal_context(source):
    axes, _ = build_axes({"adverse_events": source}, "pregnancy")
    outcome = axes[2]
    assert not outcome["report_only_context"] and outcome["no_evidence_retrieved"]
    assert outcome["state"] == "none_retrieved" and outcome["not_evidence_of_safety"]


def test_report_counts_and_observed_passages_remain_distinct_when_both_returned():
    row = {
        "lactmed": {"sections": {"Effects in Breastfed Infants": "One infant developed sedation."}},
        "adverse_events": {
            "cohort": "any",
            "top_reactions": [{"reaction": "HEADACHE", "reports": 4}],
        },
    }
    axes, _ = build_axes(row, "lactation")
    outcome = axes[2]
    assert outcome["items"][0]["text"] == "One infant developed sedation."
    assert outcome["report_only_context"][0]["reported_terms"][0]["reports"] == 4
    assert outcome["report_only_context"][0]["query_cohort"] == "any"
    assert outcome["report_only_context"][0]["requested_population"] == "lactation"
    assert not outcome["report_only_context"][0]["source_population_confirmed"]
    assert not outcome["no_evidence_retrieved"] and outcome["empty_message"] is None
