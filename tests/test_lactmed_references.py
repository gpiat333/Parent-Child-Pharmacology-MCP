"""LactMed records from the official package carry citation links; blocks are reported honestly."""

import asyncio
import importlib.util
from pathlib import Path

import pytest

from parent_child_pharmacology.clients import lactmed
from parent_child_pharmacology.core.freshness import lactmed_freshness

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts/build_lactmed_snapshot.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<book-part-wrapper id="LM999"><book-part><book-part-meta><title-group><title>Exampledrug</title></title-group>
<date date-type="revised"><day>15</day><month>08</month><year>2026</year></date></book-part-meta>
<body><sec><title>Drug Levels and Effects</title>
<sec><title>Summary of Use during Lactation</title><p>Amounts in milk are low.[<xref>1</xref>]</p></sec>
<sec><title>Drug Levels</title><sec><title>Maternal Levels.</title><p>Milk 45 mcg/L.[<xref>1-3</xref>]</p></sec>
<sec><title>Infant Levels.</title><p>Undetectable.[<xref>4</xref>]</p></sec></sec>
<sec><title>Effects on Lactation and Breastmilk</title><p>A French database study found no added risk.[<xref>5</xref>]</p></sec>
</sec></body>
<back><ref-list><title>References</title>
<ref id="r1"><label>1</label><mixed-citation>Smith A, <etal/>. Study one. J 2001;1:1.<pub-id pub-id-type="pmid">111</pub-id></mixed-citation></ref>
<ref id="r5"><label>5</label><mixed-citation>Trenque T. French study. Drug Saf 2011;34:1161.<pub-id pub-id-type="pmid">22077504</pub-id></mixed-citation></ref>
<ref id="r9"><label>9</label><mixed-citation>Uncited review. 2020.</mixed-citation></ref>
</ref-list></back></book-part></book-part-wrapper>"""


def test_builder_keeps_sections_markers_and_pmids():
    record = build.parse_record(SAMPLE)
    assert record["title"] == "Exampledrug"
    assert record["revised_on"] == "2026-08-15"
    assert "Infant Levels. Undetectable.[4]" in record["sections"]["Drug Levels"]
    assert record["sections"]["Effects on Lactation and Breastmilk"].endswith("[5]")
    first = record["references"][0]
    assert first["pmid"] == "111" and "et al" in first["citation"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a.[1] b.[47-53]", {"1", *map(str, range(47, 54))}),
        ("c.[2,4]", {"2", "4"}),
        ("no refs", set()),
    ],
)
def test_citation_markers_expand(text, expected):
    assert lactmed.cited_numbers(text) == expected


def test_only_cited_references_are_linked():
    record = build.parse_record(SAMPLE)
    text = " ".join(record["sections"].values())
    links = lactmed.reference_links(text, record["references"])
    assert [r["number"] for r in links] == ["1", "5"]
    assert links[1]["url"] == "https://pubmed.ncbi.nlm.nih.gov/22077504/"


def test_bundled_snapshot_has_sertraline_with_french_study():
    record = lactmed.snapshot_record("LM328")
    assert record["title"] == "Sertraline"
    ref = next(r for r in record["references"] if r["number"] == "54")
    assert ref["pmid"] == "22077504"


def test_record_tool_uses_snapshot_and_returns_links(monkeypatch):
    class R:
        def json(self):
            return {
                "result": {
                    "4573436": {
                        "id": "lactmed/chapter/LM328/PMC",
                        "accessionid": "NBK501191",
                        "title": "Sertraline",
                    }
                }
            }

    async def fake_ncbi(*a, **k):
        return R()

    async def no_page(*a, **k):
        raise AssertionError("snapshot records must not fetch the web page")

    monkeypatch.setattr(lactmed, "_ncbi", fake_ncbi)
    monkeypatch.setattr(lactmed.http, "request", no_page)
    out = asyncio.run(lactmed.lactmed_record("4573436", 20000))
    assert out["source"] == "snapshot:lactmed"
    assert out["url"] == "https://www.ncbi.nlm.nih.gov/books/NBK501191/"
    assert any(r["pmid"] == "22077504" for r in out["references"])
    assert out["data_freshness"]["record_revised_on"] == out["record_revised_on"]


def test_browser_check_is_reported_not_parsed_as_empty(monkeypatch):
    class Summary:
        def json(self):
            return {
                "result": {
                    "1": {
                        "id": "lactmed/chapter/NOTBUNDLED/PMC",
                        "accessionid": "NBK1",
                        "title": "X",
                    }
                }
            }

    class Page:
        text = "<html><title>Checking your browser - reCAPTCHA</title></html>"

    async def fake_ncbi(*a, **k):
        return Summary()

    async def page(*a, **k):
        return Page()

    monkeypatch.setattr(lactmed, "_ncbi", fake_ncbi)
    monkeypatch.setattr(lactmed.http, "request", page)
    out = asyncio.run(lactmed.lactmed_record("1"))
    assert out["error"] == "source_blocked_by_browser_check"
    assert "does not bypass" in out["note"]


def test_lactmed_freshness_flags_old_package():
    from datetime import datetime, timedelta, timezone

    later = datetime.now(timezone.utc) + timedelta(days=400)
    assert lactmed_freshness("2026-08-15", now=later)["status"] == "check_recommended"
