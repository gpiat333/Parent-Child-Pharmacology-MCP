"""Typed result models: what a client can rely on per tool, without breaking stops or errors."""

import asyncio

import pytest
from pydantic import ValidationError

from parent_child_pharmacology import app as server
from parent_child_pharmacology.core.safety import envelope
from parent_child_pharmacology.models.contracts import EvidenceResponse
from parent_child_pharmacology.models.outputs import OUTPUT_MODELS

BASE = {"safety": envelope({}), "disclaimer": "test"}


def registered(name):
    return server.mcp._tool_manager.get_tool(name)


def test_main_tools_advertise_their_own_result_fields():
    shared = set(EvidenceResponse.model_fields)
    expected = {
        "route_parent_question": {"route", "allow_research", "referrals"},
        "normalize_drug": {"found", "rxcui", "ingredients", "requires_confirmation"},
        "get_lactmed_record": {"title", "sections", "exposure_measurements", "references"},
        "search_literature": {"pagination", "query"},
        "get_abstracts": {"articles"},
        "search_trials": {"search_mode", "studies"},
        "medication_evidence_brief": {"detail", "evidence_axes", "queried_ingredients"},
    }
    assert set(OUTPUT_MODELS) == set(expected)
    for name, fields in expected.items():
        schema = registered(name).fn_metadata.output_schema
        assert fields <= set(schema["properties"]) - shared, name
        assert set(schema["required"]) >= {"safety", "disclaimer"}
        assert schema["additionalProperties"] is True
    # Tools without a typed model still share the plain envelope.
    assert (
        set(registered("check_evidence_coverage").fn_metadata.output_schema["properties"]) == shared
    )


@pytest.mark.parametrize("name", sorted(OUTPUT_MODELS))
def test_stops_and_failures_validate_without_tool_fields(name):
    stop = {**BASE, "status": "blocked", "allow_research": False, "route": "urgent_help"}
    error = {**BASE, "status": "error", "error": "upstream_unavailable"}
    for payload in (stop, error):
        dumped = OUTPUT_MODELS[name].model_validate(payload).model_dump(mode="json")
        own = set(OUTPUT_MODELS[name].model_fields) - set(EvidenceResponse.model_fields)
        # Fields the result did not set are left out, not returned as nulls.
        assert not (own & set(dumped)) - set(payload)


def test_wrong_types_in_typed_fields_are_rejected():
    with pytest.raises(ValidationError):
        OUTPUT_MODELS["normalize_drug"].model_validate({**BASE, "ingredients": "sertraline"})
    with pytest.raises(ValidationError):
        OUTPUT_MODELS["search_trials"].model_validate({**BASE, "studies": [{"status": 5}]})
    with pytest.raises(ValidationError):
        OUTPUT_MODELS["medication_evidence_brief"].model_validate(
            {**BASE, "evidence_axes": [{"by_ingredient": []}]}
        )


def test_source_records_keep_fields_the_model_does_not_name():
    out = (
        OUTPUT_MODELS["search_trials"]
        .model_validate(
            {
                **BASE,
                "studies": [{"nct": "NCT00000001", "status": "RECRUITING", "locations": ["A"]}],
            }
        )
        .model_dump(mode="json")
    )
    assert out["studies"][0]["locations"] == ["A"] and "search_mode" not in out


def test_registered_tool_returns_typed_structured_content(monkeypatch):
    async def fake(*a):
        return {"found": True, "rxcui": "123", "ingredients": ["test ingredient"]}

    monkeypatch.setattr(server.src, "rxnorm_normalize", fake)
    _, structured = asyncio.run(
        registered("normalize_drug").run({"name": "test"}, convert_result=True)
    )
    assert structured["ingredients"] == ["test ingredient"] and structured["found"] is True
    assert "route" not in structured and "match_type" not in structured
