import asyncio

import pytest

from parent_child_pharmacology.mc import nichd as n

BPCA = '<a href="/sites/default/files/inline-files/BPCAStudySummaryAcyclovir.pdf">Acyclovir</a><a href="https://pediatrictrials.org/summary.pdf">PTN summary</a><a href="https://evil.example/summary.pdf">Unrelated</a>'
DASH = """<span class="results-count">1 Total Results</span><div class="dash-data-item" data-study-id="42"><h3><a href="/study/42">Study &amp; trial</a></h3><div class="metadata-item"><strong>Study Description:</strong>Observed outcome. No causal claim.</div><div class="metadata-item"><strong>NICHD Research Networks and Initiatives:</strong><span>Neonatal Research Network</span></div><div class="field-row"><label>Publication URLs:</label><span><a href="https://pubmed.ncbi.nlm.nih.gov/123/">Paper</a><a href="javascript:alert(1)">bad</a></span></div></div>"""


def test_bpca_links_and_scope():
    rows = n.parse_bpca(BPCA)
    assert len(rows) == 2
    assert rows[0]["url"].startswith("https://www.nichd.nih.gov/")
    assert "not retrieved" in rows[0]["content_retrieved"]


def test_dash_metadata_and_publications():
    rows, total = n.parse_dash(DASH)
    assert total == 1 and rows[0]["title"] == "Study & trial"
    assert rows[0]["description"] == "Observed outcome. No causal claim."
    assert rows[0]["publication_urls"] == ["https://pubmed.ncbi.nlm.nih.gov/123/"]
    assert rows[0]["network"] == "Neonatal Research Network"
    assert rows[0]["doi"] is None


def test_empty_dash():
    assert n.parse_dash('<span class="results-count">0 Total Results</span>') == ([], 0)


@pytest.mark.parametrize(
    "html", ["<html>Sign in</html>", '<span class="results-count">1 Total Results</span>']
)
def test_dash_schema_drift(html):
    with pytest.raises(ValueError):
        n.parse_dash(html)


def test_bpca_schema_drift():
    with pytest.raises(ValueError):
        n.parse_bpca('<a href="/unrelated.pdf">Noise</a>')


@pytest.mark.parametrize("query,limit", [("x" * 201, 10), ("", 0), ("", 26)])
def test_validation(query, limit):
    with pytest.raises(ValueError):
        n.validate(query, limit)


@pytest.mark.parametrize("network,page", [("unknown", 0), ("any", -1), ("any", 101)])
def test_dash_validation(network, page):
    with pytest.raises(ValueError):
        asyncio.run(n.search_dash(network=network, page=page))


def test_network_query_and_limit(monkeypatch):
    calls = []

    async def request(*args, **kwargs):
        calls.append(kwargs["params"])
        return type("Response", (), {"text": DASH})()

    monkeypatch.setattr(n.http, "request", request)
    r = asyncio.run(n.search_dash(network="neonatal", max_results=1))
    assert calls[0]["network[Neonatal Research Network]"] == "Neonatal Research Network"
    assert r["results"][0]["study_id"] == "42" and "no participant data" in r["access_note"]
    assert not r["results_truncated"]
    r = asyncio.run(n.search_dash(network="mfmu"))
    assert not r["results"]  # never infer MFMU membership from title


def test_bpca_token_matching(monkeypatch):
    async def request(*args, **kwargs):
        return type("Response", (), {"text": BPCA})()

    monkeypatch.setattr(n.http, "request", request)
    assert len(asyncio.run(n.search_bpca("ACYCLOVIR"))["results"]) == 1
    assert not asyncio.run(n.search_bpca("acyclo"))["results"]


def test_server_tools_are_wired(monkeypatch):
    from parent_child_pharmacology import app as server

    async def bpca(*args):
        return {"source": "test", "results": []}

    async def dash(*args):
        return {"source": "test", "results": []}

    monkeypatch.setattr(n, "search_bpca", bpca)
    monkeypatch.setattr(n, "search_dash", dash)
    assert asyncio.run(server.search_bpca_evidence.__wrapped__())["source"] == "test"
    assert asyncio.run(server.search_nichd_studies.__wrapped__())["source"] == "test"
