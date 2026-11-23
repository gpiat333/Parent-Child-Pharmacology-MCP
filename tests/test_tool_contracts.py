"""Check the advertised contract and the real FastMCP validation boundary."""

import asyncio

import pytest
from pydantic import ValidationError

from parent_child_pharmacology import app as server


def registered(name):
    return server.mcp._tool_manager.get_tool(name)


def validate(name, arguments):
    async def capture(**kwargs):
        return kwargs

    return asyncio.run(
        registered(name).fn_metadata.call_fn_with_arg_validation(capture, True, arguments, None)
    )


@pytest.mark.parametrize(
    "name,args",
    [
        ("get_lactmed_record", {"drug": "sertraline", "max_chars": 499}),
        ("get_lactmed_record", {"drug": "sertraline", "max_chars": 20001}),
        ("get_lactmed_record", {"drug": "sertraline", "max_chars": True}),
        ("get_lactmed_record", {"drug": "sertraline", "max_chars": "5000"}),
        ("get_lactmed_record", {"drug": "sertraline", "unexpected": True}),
        ("get_lactmed_record", {"drug": ""}),
        ("get_lactmed_record", {"drug": "   "}),
        ("get_lactmed_record", {"drug": "x" * 201}),
        ("get_lactmed_record", {"drug": 123}),
        ("get_lactmed_record", {}),
        ("search_fda_drug_notices", {"kind": "recalls"}),
        ("search_fda_drug_notices", {"kind": "shortages"}),
        ("search_fda_drug_notices", {"kind": "warnings", "drug": "sertraline"}),
        ("search_fda_drug_notices", {"drug": "sertraline"}),
        ("search_literature", {"query": "sertraline", "population": "adult"}),
        ("get_abstracts", {"pmids": []}),
        ("get_abstracts", {"pmids": ["123"] * 11}),
        ("get_abstracts", {"pmids": ["https://pubmed.ncbi.nlm.nih.gov/123/"]}),
        ("get_abstracts", {"pmids": [123]}),
        ("get_mprint_details", {"pmid": "123", "table": "invalid"}),
        ("get_lactmed_record", {"book_id": "sertraline"}),
        ("get_lactmed_record", {"book_id": "123", "max_chars": 20001}),
        ("get_patient_education", {"topic": "sertraline", "rxcui": "bad"}),
        ("search_nichd_resources", {"source": "dash_studies", "page": 101}),
        ("search_nichd_resources", {"source": "dash_studies", "page": -1}),
        ("search_nichd_resources", {"source": "pubmed"}),
        ("get_mprint_details", {"pmid": "123", "offset": -1}),
        ("route_parent_question", {"question": "x" * 4001}),
    ],
)
def test_invalid_inputs_rejected_before_callback(name, args):
    with pytest.raises(ValidationError):
        validate(name, args)


@pytest.mark.parametrize(
    "name,args",
    [
        ("get_lactmed_record", {"drug": " sertraline ", "max_chars": 20000}),
        ("get_lactmed_record", {"book_id": "4573436"}),
        ("get_abstracts", {"pmids": ["123"] * 10}),
        ("search_nichd_resources", {}),
        (
            "search_nichd_resources",
            {"source": "dash_studies", "network": "mfmu", "page": 100, "max_results": 25},
        ),
        ("find_mprint_records", {"pmid": "123"}),
        ("search_fda_drug_notices", {"kind": "safety_communications"}),
        ("search_fda_drug_notices", {"kind": "reporting_links"}),
        ("search_fda_drug_notices", {"kind": "recalls", "drug": "naproxen", "lot": "ABC123"}),
        ("find_pregnancy_exposure_registries", {}),
    ],
)
def test_valid_boundaries_and_intentional_empty_discovery(name, args):
    validate(name, args)


def test_all_tools_advertise_strict_inputs_and_typed_envelope():
    tools = asyncio.run(server.mcp.list_tools())
    assert len(tools) == 21
    for tool in tools:
        assert tool.inputSchema["additionalProperties"] is False
        assert set(tool.outputSchema["required"]) >= {"safety", "disclaimer"}
        assert tool.outputSchema["additionalProperties"] is True
    schema = registered("get_lactmed_record").parameters
    assert schema["properties"]["max_chars"]["maximum"] == 20000
    assert schema["properties"]["drug"]["maxLength"] == 200


def test_invalid_registered_call_does_not_retrieve(monkeypatch):
    async def forbidden(*a, **kw):
        pytest.fail("Retrieval must not run for invalid input")

    monkeypatch.setattr(server.src, "lactmed_search", forbidden)
    from mcp.server.fastmcp.exceptions import ToolError

    with pytest.raises(ToolError):
        asyncio.run(server.mcp.call_tool("get_lactmed_record", {"drug": "  "}))


def test_protocol_output_preserves_evidence(monkeypatch):
    async def fake(*a):
        return {"found": True, "rxcui": "123", "ingredients": ["test ingredient"]}

    monkeypatch.setattr(server.src, "rxnorm_normalize", fake)
    result = asyncio.run(registered("normalize_drug").run({"name": "test"}, convert_result=True))
    content, structured = result
    assert content
    assert structured["ingredients"] == ["test ingredient"]
    assert structured["safety"]["client_enforcement_required"] is True
    assert structured["disclaimer"]


def test_protocol_failure_has_valid_envelope(monkeypatch):
    async def fail(*a):
        raise RuntimeError("private upstream detail")

    monkeypatch.setattr(server.src, "rxnorm_normalize", fail)
    content, structured = asyncio.run(
        registered("normalize_drug").run({"name": "test"}, convert_result=True)
    )
    assert structured["error"] == "RuntimeError"
    assert "private upstream detail" not in str(structured)
    assert structured["safety"]["evidence_unavailable"] is True


def test_output_contract_rejects_missing_or_mistyped_metadata():
    tool = registered("normalize_drug")
    with pytest.raises(ValidationError):
        tool.fn_metadata.convert_result({"source": "test", "disclaimer": "test"})
    from parent_child_pharmacology.mc.parent_safety import envelope

    safety = envelope({})
    safety["client_enforcement_required"] = "yes"
    with pytest.raises(ValidationError):
        tool.fn_metadata.convert_result({"safety": safety, "disclaimer": "test"})


def test_tool_descriptions_distinguish_goals():
    trials = registered("search_trials").description
    assert "research landscape" in trials and "recruiting_only=true" in trials
    brief = registered("medication_evidence_brief").description
    assert "focused parent questions" in brief and "detail='full'" in brief
    assert "Lactation only" in registered("get_lactmed_record").description


def test_descriptions_are_short_and_results_carry_the_answer_rules(monkeypatch):
    for tool in asyncio.run(server.mcp.list_tools()):
        assert len(tool.description) < 900, tool.name

    async def fake(*a):
        return {"found": True, "rxcui": "123", "ingredients": ["test ingredient"]}

    monkeypatch.setattr(server.src, "rxnorm_normalize", fake)
    result = asyncio.run(server.normalize_drug("test"))
    assert "never silently substitute" in result["answer_rules"]
    stop = asyncio.run(server.normalize_drug("what dose should I take"))
    assert stop["allow_research"] is False and "answer_rules" not in stop
