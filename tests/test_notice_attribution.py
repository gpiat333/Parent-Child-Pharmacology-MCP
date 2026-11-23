"""Server notices name their author, and MPRINT can be checked for updates on request."""

import asyncio

import pytest
from pydantic import ValidationError

from parent_child_pharmacology.core.audit import NOTICE_ATTRIBUTION, audited
from parent_child_pharmacology.core.instructions import INSTRUCTIONS
from parent_child_pharmacology.models.inputs import FindMprintRecordsInput


def test_every_tool_result_says_who_wrote_its_notices():
    @audited
    async def sample_tool(drug: str = "sertraline"):
        return {"source": "test", "continuity_of_care_notice": "Stopping can also carry risks."}

    out = asyncio.run(sample_tool())
    assert out["notice_attribution"] == NOTICE_ATTRIBUTION
    assert "written by this MCP server" in NOTICE_ATTRIBUTION
    assert "not quoted from the cited sources" in NOTICE_ATTRIBUTION


def test_server_instructions_tell_clients_how_to_attribute_notices():
    assert "notice_attribution" in INSTRUCTIONS


def test_mprint_update_check_needs_no_drug():
    assert FindMprintRecordsInput(check_for_updates=True).check_for_updates is True
    with pytest.raises(ValidationError):
        FindMprintRecordsInput()


def test_mprint_update_check_reports_upstream_status(monkeypatch):
    from parent_child_pharmacology.core import freshness
    from parent_child_pharmacology.services import mprint

    async def fake_upstream():
        return {
            "status": "newer_upstream_data_available",
            "meaning": "MPRINT has published changes.",
        }

    monkeypatch.setattr(freshness, "check_upstream", fake_upstream)
    out = asyncio.run(mprint.find_mprint_records(check_for_updates=True))
    assert out["upstream_check"]["status"] == "newer_upstream_data_available"
    assert out["data_freshness"]["dataset"] == "MPRINT"
    assert "read-only" in out["update_process"]
