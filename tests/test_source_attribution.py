"""Source warnings are reported as the source's statements, not as the assistant's instructions."""

from pathlib import Path

from parent_child_pharmacology.core.evidence import SOURCE_ATTRIBUTION_RULE, annotate
from parent_child_pharmacology.core.instructions import INSTRUCTIONS

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_results_carry_the_attribution_rule():
    out = annotate({"source": "test", "sections": {}})
    assert out["framing_contract"]["source_attribution"] == SOURCE_ATTRIBUTION_RULE
    assert "The label states that" in SOURCE_ATTRIBUTION_RULE
    assert "name only the contacts the results name" in SOURCE_ATTRIBUTION_RULE


def test_stopped_results_do_not_get_research_framing():
    out = annotate({"source": "test", "allow_research": False})
    assert "framing_contract" not in out


def test_server_and_shared_client_instructions_include_the_rule():
    assert "The label states that" in INSTRUCTIONS
    shared = (ROOT / "chat-client/exposure-presentation-instructions.txt").read_text(
        encoding="utf-8"
    )
    assert "never restated in your own voice as an instruction to the reader" in shared
    assert "name only the contacts the retrieved results name" in shared


def test_server_notices_say_who_wrote_them_where_they_appear():
    out = annotate({"source": "test", "results": [{"title": "x"}]})
    assert "Written by this MCP server" in out["continuity_of_care_notice_origin"]
    assert "never write that a source states" in out["continuity_of_care_notice_origin"]
    assert 'never introduce one with "the label states"' in SOURCE_ATTRIBUTION_RULE
    stop = annotate({"allow_research": False, "route": "urgent_help"})
    assert "continuity_of_care_notice_origin" not in stop


def test_recall_results_name_only_the_notice_and_a_pharmacist(monkeypatch):
    import asyncio

    import httpx

    from parent_child_pharmacology.clients import parent_resources as p

    async def fake(method, url, **kw):
        return httpx.Response(200, json={"results": [], "meta": {}})

    monkeypatch.setattr(p.http, "request", fake)
    out = asyncio.run(p.recalls("naproxen", "", "NOTREAL-77"))
    contacts = out["verification_contacts"]
    assert contacts["named_in_this_result"] == ["the official FDA recall notice", "a pharmacist"]
    assert "manufacturer" in contacts["rule"] and "name only these" in contacts["rule"]
