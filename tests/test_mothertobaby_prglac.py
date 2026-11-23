"""MotherToBaby referral and fact sheets, PRGLAC context, and funder-scope disclosure."""

import asyncio

import pytest

from parent_child_pharmacology.core.referrals import MOTHERTOBABY, PRGLAC_CONTEXT
from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "question",
    [
        "I'm pregnant. Should I stop taking my sertraline?",
        "Can I take ibuprofen while breastfeeding?",
        "What dose of acetaminophen is OK while nursing?",
    ],
)
def test_individual_pregnancy_or_breastfeeding_decisions_get_mothertobaby(question):
    out = route(question)
    assert out["route"] == "clinician_or_pharmacist"
    assert "866-626-6847" in out["message"]
    assert out["referrals"] == [MOTHERTOBABY]
    assert MOTHERTOBABY["phone_link"] == "tel:18666266847"


def test_child_dosing_question_does_not_get_pregnancy_referral():
    out = route("How much ibuprofen should I give my 2 year old?")
    assert out["route"] == "clinician_or_pharmacist"
    assert "MotherToBaby" not in out["message"]
    assert "referrals" not in out


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("I'm pregnant and I want to harm myself.", "mental_health_support"),
        ("I'm pregnant and my baby is not breathing.", "urgent_help"),
        ("I'm breastfeeding. What is my little white pill?", "confirm_identity"),
    ],
)
def test_mothertobaby_never_offered_on_stop_routes(question, expected):
    out = route(question)
    assert out["route"] == expected
    assert "866-626-6847" not in (out["message"] or "")


def _fake_ncbi(summary):
    class R:
        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    async def fake(endpoint, **params):
        if endpoint == "esearch":
            assert params["term"].endswith("AND mtb[book]")
            return R({"esearchresult": {"idlist": list(summary)}})
        return R({"result": summary})

    return fake


def test_fact_sheet_search_returns_labeled_sheets(monkeypatch):
    from parent_child_pharmacology.clients import mothertobaby
    from parent_child_pharmacology.services.fact_sheets import search_mothertobaby_fact_sheets

    summary = {
        "1": {
            "id": "mtb/chapter/sertraline-en/PMC",
            "chapteraccessionid": "NBK582954",
            "pubdate": "2025/08/01 00:00",
            "bookinfo": '<Parent id="sertraline-en" role="document" type="chapter"><Title>Sertraline (Zoloft&#xAE;)</Title>',
        },
        "2": {
            "id": "mtb/chapter/sertraline-sp/PMC",
            "chapteraccessionid": "NBK999999",
            "pubdate": "2025/08/01 00:00",
            "bookinfo": '<Self id="sertraline-sp" role="document" type="chapter"><Title>Sertralina</Title>',
        },
        "3": {
            "id": "mtb/chapter/paroxetine-en/PMC",
            "chapteraccessionid": "NBK888888",
            "pubdate": "2025/08/01 00:00",
            "bookinfo": '<Self id="paroxetine-en" role="document" type="chapter"><Title>Paroxetine</Title>',
        },
    }
    monkeypatch.setattr(mothertobaby, "_ncbi", _fake_ncbi(summary))
    out = asyncio.run(search_mothertobaby_fact_sheets("sertraline", "es", include_text=False))
    assert [s["title"] for s in out["fact_sheets"]] == ["Sertralina"]
    assert out["text_included"] is False
    assert "nonprofit" in out["publisher"]
    assert out["specialist_referral"]["call"] == "866-626-6847"
    both = asyncio.run(search_mothertobaby_fact_sheets("sertraline", include_text=False))
    # A sheet that only mentions the medicine in passing (paroxetine) is excluded.
    assert [s["language"] for s in both["fact_sheets"]] == ["en", "es"]
    assert both["fact_sheets"][0] == {
        "title": "Sertraline (Zoloft®)",
        "doc_id": "sertraline-en",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK582954/",
        "accession": "NBK582954",
        "language": "en",
        "bookshelf_date": "2025/08/01",
    }


def test_fact_sheet_no_results_is_not_a_safety_finding(monkeypatch):
    from parent_child_pharmacology.clients import mothertobaby
    from parent_child_pharmacology.services.fact_sheets import search_mothertobaby_fact_sheets

    monkeypatch.setattr(mothertobaby, "_ncbi", _fake_ncbi({}))
    out = asyncio.run(search_mothertobaby_fact_sheets("unknownium"))
    assert out["status"] == "no_results"
    assert "not evidence of safety" in out["no_results_meaning"]


def test_prglac_context_is_factual_and_linked():
    assert "21st Century Cures Act" in PRGLAC_CONTEXT["summary"]
    assert "15 recommendations" in PRGLAC_CONTEXT["summary"]
    assert all(u.startswith("https://www.nichd.nih.gov/") for u in PRGLAC_CONTEXT["links"])


def test_funding_tools_disclose_nih_only_scope(monkeypatch):
    from parent_child_pharmacology.services import literature

    async def fake_reporter(*a, **k):
        return []

    monkeypatch.setattr(literature.src, "reporter_search", fake_reporter)
    out = asyncio.run(literature.search_funded_research("breastfeeding medication"))
    assert "NIH RePORTER only" in out["funder_scope"]


def test_funders_question_reaches_research_not_a_stop():
    out = route("Who are the major funders of breastfeeding and medication research?")
    assert out["route"] == "evidence"
    assert "requested_workflow" not in out


def test_fact_sheet_text_is_verbatim_whole_answers_with_attribution():
    from parent_child_pharmacology.clients.mothertobaby import snapshot_sheet
    from parent_child_pharmacology.services.fact_sheets import _attach_text

    record = snapshot_sheet("sertraline-en")
    assert record["qa"][0]["question"] == "What is sertraline?"
    sheets = _attach_text([{"doc_id": "sertraline-en"}], 1500)
    text = sheets[0]["text"]
    assert "CC BY-NC-ND 3.0" in text["attribution"] and "OTIS" in text["attribution"]
    originals = {qa["question"]: qa["answer"] for qa in record["qa"]}
    for qa in text["questions_and_answers"]:
        assert qa["answer"] == originals[qa["question"]]
    kept = {qa["question"] for qa in text["questions_and_answers"]}
    assert kept | set(text["questions_omitted_by_length_limit"]) == set(originals)
    assert text["questions_omitted_by_length_limit"]


def test_unknown_sheet_has_no_text_and_says_so():
    from parent_child_pharmacology.services.fact_sheets import _attach_text

    sheet = _attach_text([{"doc_id": "not-a-sheet-en"}], 8000)[0]
    assert sheet["text"] is None and "open the link" in sheet["text_note"]


def test_search_falls_back_to_bundled_package_when_ncbi_search_fails(monkeypatch):
    from parent_child_pharmacology.clients import mothertobaby
    from parent_child_pharmacology.services.fact_sheets import search_mothertobaby_fact_sheets

    async def down(*a, **k):
        raise RuntimeError("NCBI unavailable")

    monkeypatch.setattr(mothertobaby, "_ncbi", down)
    from parent_child_pharmacology.services import fact_sheets

    monkeypatch.setattr(fact_sheets, "fact_sheet_search", mothertobaby.fact_sheet_search)
    out = asyncio.run(search_mothertobaby_fact_sheets("sertraline", "es", 1))
    assert out["search_mode"] == "snapshot_fallback"
    assert out["fact_sheets"][0]["title"].startswith("Sertralina")
    assert out["fact_sheets"][0]["text"]["questions_and_answers"]


def test_builder_reads_question_answer_pairs():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "scripts/build_mothertobaby_snapshot.py"
    spec = importlib.util.spec_from_file_location("mtb_build", path)
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    xml = (
        b"<book-part-wrapper><book-part-meta><title-group><title>Drugx</title></title-group>"
        b"<permissions><copyright-statement>Copyright by OTIS, May 2025</copyright-statement></permissions>"
        b"</book-part-meta><question-wrap-group><question-preamble><p>About drugx.</p></question-preamble>"
        b"<question-wrap><question><p><bold>What is drugx?</bold></p></question>"
        b"<answer><p>A medicine.</p><p>Second paragraph.</p></answer></question-wrap>"
        b"</question-wrap-group></book-part-wrapper>"
    )
    sheet = build.parse_sheet(xml)
    assert sheet["title"] == "Drugx" and sheet["copyright"] == "Copyright by OTIS, May 2025"
    assert sheet["qa"] == [
        {"question": "What is drugx?", "answer": "A medicine. Second paragraph."}
    ]
