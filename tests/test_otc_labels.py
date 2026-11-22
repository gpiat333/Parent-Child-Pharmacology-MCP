import asyncio

import httpx
import pytest

from parent_child_pharmacology.mc import sources


@pytest.mark.parametrize("title", ["", "<title>If pregnant or breast-feeding:</title>"])
def test_otc_combined_warning_retains_scope(title):
    xml = f"""<document xmlns="urn:hl7-org:v3"><section>
    <code code="53414-9"/>{title}<text><paragraph>Pregnancy warning.</paragraph>
    <paragraph>Breastfeeding warning.</paragraph></text></section>
    <section><code code="34068-7"/><title>Directions</title><text>Dose instructions.</text></section>
    </document>"""
    result = sources.parse_dailymed_sections(xml)
    assert set(result) == {"pregnancy_lactation"}
    assert "Pregnancy warning." in result["pregnancy_lactation"]
    assert "Breastfeeding warning." in result["pregnancy_lactation"]
    assert "Dose instructions" not in str(result)


def test_conflicting_title_is_not_otc_warning():
    xml = '<document xmlns="urn:hl7-org:v3"><section><code code="53414-9"/><title>Directions</title><text>Other text.</text></section></document>'
    assert sources.parse_dailymed_sections(xml) == {}


def test_empty_heading_is_not_evidence():
    xml = '<document xmlns="urn:hl7-org:v3"><section><title>Pregnancy</title><text/></section></document>'
    assert sources.parse_dailymed_sections(xml) == {}


def test_otc_lookup_returns_product_and_missing_sections(monkeypatch):
    async def request(method, url, **kwargs):
        if url.endswith("spls.json"):
            return httpx.Response(
                200, json={"data": [{"setid": "test-set", "title": "Example tablet"}]}
            )
        return httpx.Response(
            200,
            text='<document xmlns="urn:hl7-org:v3"><section><code code="53414-9"/><text>Combined warning.</text></section></document>',
        )

    monkeypatch.setattr(sources.http, "request", request)
    result = asyncio.run(sources.dailymed_label("example"))
    assert result["title"] == "Example tablet"
    assert result["url"].endswith("setid=test-set")
    assert result["sections"] == {"pregnancy_lactation": "Combined warning."}
    assert result["missing_standalone_sections"] == ["pregnancy", "lactation", "pediatric_use"]
    assert "not all formulations" in result["selection_note"]
