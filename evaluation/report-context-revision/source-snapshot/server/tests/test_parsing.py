"""Offline unit tests for parsers and the audit/error envelope.  Run: pytest -q"""
import asyncio

from mc import config as cfg
from mc.audit import audited
from mc.sources import parse_dailymed_sections, parse_lactmed_html, parse_medlineplus_search, parse_pubmed_xml

PUBMED = """<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article>
<Journal><Title>J Test</Title><JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
<ArticleTitle>Sertraline in <i>lactation</i></ArticleTitle>
<Abstract><AbstractText Label="A">Low levels.</AbstractText><AbstractText>No effects.</AbstractText></Abstract>
</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"""

SPL = """<document xmlns="urn:hl7-org:v3"><component><structuredBody>
<component><section><code code="77290-5"/><text>8.2 Lactation: present in milk.</text></section></component>
<component><section><code code="42228-7"/><text>8.1 Pregnancy: data limited.</text></section></component>
<component><section><code code="00000-0"/><text>ignored</text></section></component>
</structuredBody></component></document>"""

MLP = """<nlmSearchResult><list><document url="https://medlineplus.gov/x.html" rank="0">
<content name="title">Breastfeeding</content>
<content name="FullSummary">&lt;p&gt;Feeding your baby.&lt;/p&gt;</content></document></list></nlmSearchResult>"""


def test_pubmed_parser():
    a = parse_pubmed_xml(PUBMED)[0]
    assert a["pmid"] == "123" and a["title"] == "Sertraline in lactation"
    assert a["abstract"] == "Low levels. No effects." and a["year"] == "2024"


def test_dailymed_sections():
    s = parse_dailymed_sections(SPL)
    assert set(s) == {"lactation", "pregnancy"} and "present in milk" in s["lactation"]


def test_medlineplus_parser():
    d = parse_medlineplus_search(MLP)[0]
    assert d["title"] == "Breastfeeding" and d["url"].endswith("x.html")


def test_audited_adds_disclaimer_and_catches_errors(monkeypatch):
    monkeypatch.setattr(cfg, "USE_LAKEHOUSE", False)

    @audited
    async def ok():
        return {"source": "x"}

    @audited
    async def boom():
        raise ValueError("bad")

    r1, r2 = asyncio.run(ok()), asyncio.run(boom())
    assert r1["disclaimer"] == cfg.DISCLAIMER
    assert "ValueError" in r2["error"] and "disclaimer" in r2


def test_lactmed_html_sections():
    page = """<!doctype html><html><head><style>.hidden {display:none}</style></head>
    <body><header>Bookshelf</header><nav>Contents and navigation</nav>
    <main><h1>Sertraline</h1><div class="body-content">
    <h2>Summary of Use during Lactation</h2>
    <p>Low levels in <em>breastmilk</em> &amp; small infant exposure.</p>
    <script>Ignore this script.</script>
    <h2>Drug Levels</h2><p><b>Maternal Levels.</b> Published milk measurements.</p>
    <h2>Effects in Breastfed Infants</h2><p>No effects reported in this sample.</p>
    <h2>Effects on Lactation and Breastmilk</h2><p>Breastfeeding support may help.</p>
    <h2>Alternate Drugs to Consider</h2><p>Alternative A</p>
    <h2>References</h2><ol><li>Excluded citation.</li></ol>
    </div></main><footer>Copyright and site links</footer></body></html>"""
    assert parse_lactmed_html(page) == {
        "Summary of Use during Lactation": "Low levels in breastmilk & small infant exposure.",
        "Drug Levels": "Maternal Levels. Published milk measurements.",
        "Effects in Breastfed Infants": "No effects reported in this sample.",
        "Effects on Lactation and Breastmilk": "Breastfeeding support may help.",
        "Alternate Drugs to Consider": "Alternative A",
    }
