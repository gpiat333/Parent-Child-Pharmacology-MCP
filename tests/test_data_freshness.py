"""Bundled MPRINT data must always say how old it is and how to check for newer data."""

import asyncio
import json
from datetime import datetime, timedelta

import pytest

from parent_child_pharmacology.core import freshness
from parent_child_pharmacology.core.http import APPROVED_HOSTS, UpstreamUnavailable


def test_fresh_copy_reports_date_revision_and_how_to_check():
    out = freshness.mprint_freshness()
    assert out["mode"] == "saved_copy"
    assert out["revision"][:7] in out["how_to_check"]
    assert out["saved_on"] in out["display_note"]
    assert "github.com/langli-lab/mprint-kp-data" in out["how_to_check"]


def test_old_copy_is_flagged_for_checking():
    saved = datetime.fromisoformat(freshness._manifest()["retrieved_at_utc"])
    later = saved + timedelta(days=freshness.CHECK_AFTER_DAYS + 1)
    out = freshness.mprint_freshness(now=later)
    assert out["status"] == "check_recommended"
    assert "past the recommended check date" in out["display_note"]


@pytest.mark.parametrize(
    ("latest", "expected"),
    [("abc", "up_to_date"), ("def", "newer_upstream_data_available"), (None, "unable_to_check")],
)
def test_upstream_comparison(latest, expected):
    assert freshness.compare_upstream(latest, "2026-01-01", "abc") == expected


def test_failed_upstream_check_never_reads_as_up_to_date(monkeypatch):
    from parent_child_pharmacology.core import http as http_module

    async def fail(*a, **k):
        raise UpstreamUnavailable("HTTP 503")

    monkeypatch.setattr(http_module.http, "request", fail)
    out = asyncio.run(freshness.check_upstream())
    assert out["status"] == "unable_to_check"
    assert "unknown" in out["meaning"]


def test_newer_upstream_commit_is_reported(monkeypatch):
    from parent_child_pharmacology.core import http as http_module

    class Response:
        def json(self):
            return [{"sha": "f" * 40, "commit": {"committer": {"date": "2027-01-01T00:00:00Z"}}}]

    async def newer(*a, **k):
        return Response()

    monkeypatch.setattr(http_module.http, "request", newer)
    out = asyncio.run(freshness.check_upstream())
    assert out["status"] == "newer_upstream_data_available"
    assert out["latest_upstream_date"] == "2027-01-01T00:00:00Z"


def test_upstream_check_host_is_allowlisted():
    assert "api.github.com" in APPROVED_HOSTS


def test_every_mprint_result_carries_freshness():
    from parent_child_pharmacology.services.mprint import find_mprint_records, get_mprint_details

    found = asyncio.run(find_mprint_records(pmid="39626074", resolve_names=False))
    details = asyncio.run(get_mprint_details(pmid="39626074"))
    for out in (found, details):
        assert out["data_freshness"]["dataset"] == "MPRINT"
        assert out["data_freshness"]["display_note"]


def test_snapshot_resource_includes_live_check(monkeypatch):
    from parent_child_pharmacology.app import mcp
    from parent_child_pharmacology.core import http as http_module

    async def fail(*a, **k):
        raise UpstreamUnavailable("offline")

    monkeypatch.setattr(http_module.http, "request", fail)
    contents = asyncio.run(mcp.read_resource("parent-child://mprint-snapshot"))
    data = json.loads(list(contents)[0].content)
    assert data["data_freshness"]["dataset"] == "MPRINT"
    assert data["upstream_check"]["status"] == "unable_to_check"
