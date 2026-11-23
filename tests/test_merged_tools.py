"""The merged tools keep each original lookup reachable through one goal-level call."""

import asyncio

from parent_child_pharmacology.clients import parent_resources as parents
from parent_child_pharmacology.services import lactation, parent_resources


def test_lactmed_record_is_found_and_read_from_a_drug_name(monkeypatch):
    async def search(drug, n):
        return {"source": "test", "results": [{"id": "111", "title": "Sertraline"}]}

    async def record(book_id, max_chars):
        return {"book_id": book_id, "text": "Summary of Use during Lactation: text"}

    monkeypatch.setattr(lactation, "search_lactmed", search)
    monkeypatch.setattr(lactation.src, "lactmed_record", record)
    out = asyncio.run(lactation.get_lactmed_record(drug="sertraline"))
    assert out["book_id"] == "111" and out["matched_record"]["title"] == "Sertraline"


def test_several_lactmed_matches_return_candidates_without_guessing(monkeypatch):
    async def search(drug, n):
        return {
            "source": "test",
            "results": [
                {"id": "1", "title": "Estradiol"},
                {"id": "2", "title": "Ethinyl Estradiol"},
                {"id": "3", "title": "Estradiol Valerate"},
            ],
        }

    async def forbidden(*args):
        raise AssertionError("No record may be fetched before one is selected")

    monkeypatch.setattr(lactation, "search_lactmed", search)
    monkeypatch.setattr(lactation.src, "lactmed_record", forbidden)
    out = asyncio.run(lactation.get_lactmed_record(drug="estrogen"))
    assert out["requires_record_selection"] and len(out["results"]) == 3


def test_exact_title_wins_among_several_lactmed_matches(monkeypatch):
    async def search(drug, n):
        return {
            "source": "test",
            "results": [
                {"id": "2", "title": "Ethinyl Estradiol"},
                {"id": "1", "title": "Estradiol"},
            ],
        }

    async def record(book_id, max_chars):
        return {"book_id": book_id, "text": "x"}

    monkeypatch.setattr(lactation, "search_lactmed", search)
    monkeypatch.setattr(lactation.src, "lactmed_record", record)
    out = asyncio.run(lactation.get_lactmed_record(drug="estradiol"))
    assert out["book_id"] == "1" and len(out["other_candidates"]) == 1


def test_no_lactmed_match_is_not_reported_as_safe(monkeypatch):
    async def search(drug, n):
        return {"source": "test", "results": []}

    monkeypatch.setattr(lactation, "search_lactmed", search)
    out = asyncio.run(lactation.get_lactmed_record(drug="zzzz"))
    assert out["results"] == [] and "not evidence of safety" in out["note"]


def test_fda_notice_kinds_reach_their_own_lookup(monkeypatch):
    seen = []

    def fake(kind):
        async def call(*args):
            seen.append((kind, args))
            return {"source": kind, "results": []}

        return call

    monkeypatch.setattr(parents, "recalls", fake("recalls"))
    monkeypatch.setattr(parents, "safety_alerts", fake("alerts"))
    notices = parent_resources.search_fda_drug_notices
    assert asyncio.run(notices("recalls", "naproxen", lot="L1"))["source"] == "recalls"
    assert asyncio.run(notices("safety_communications"))["source"] == "alerts"
    assert seen[0] == ("recalls", ("naproxen", "", "L1", 10))
    links = asyncio.run(notices("reporting_links"))
    assert links["notice_kind"] == "reporting_links" and "error" not in links
    missing = asyncio.run(notices("shortages"))
    assert missing["error"] == "drug_required"


def test_registry_lookup_lists_the_directory_without_a_drug(monkeypatch):
    async def registries(drug, n):
        return {
            "source": "test",
            "results": [{"registry": "B"}, {"registry": "A"}],
            "args": [drug, n],
        }

    monkeypatch.setattr(parents, "pregnancy_registries", registries)
    out = asyncio.run(parent_resources.find_pregnancy_exposure_registries())
    assert out["args"] == ["", 20] and out["tier"] == "participation" and not out["ranked"]
    assert [r["registry"] for r in out["results"]] == ["A", "B"]
