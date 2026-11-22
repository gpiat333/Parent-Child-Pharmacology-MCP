import asyncio
import json
import logging

import httpx
import pytest

from parent_child_pharmacology.mc import audit, config, sources


def test_exception_query_never_reaches_response_logs_or_audit(monkeypatch, caplog):
    marker = "SYNTHETIC_PRIVATE_QUERY"
    captured = []
    monkeypatch.setattr(config, "USE_LAKEHOUSE", True)

    async def log_call(*args):
        captured.append(args)

    monkeypatch.setattr(audit.lakehouse, "log_call", log_call)

    @audit.audited
    async def fail():
        raise ValueError("https://source.example/?query=" + marker)

    async def run():
        result = await fail()
        await asyncio.sleep(0)
        return result

    with caplog.at_level(logging.WARNING, logger="mc"):
        result = asyncio.run(run())
    assert marker not in json.dumps(result)
    assert marker not in caplog.text
    assert marker not in repr(captured)
    assert result["error"] == "ValueError" and result["error_id"]
    assert captured[0][-2:] == (False, "ValueError")


def test_empty_drug_is_rejected_before_network(monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError("Must not call upstream")

    monkeypatch.setattr(sources.http, "request", forbidden)
    result = asyncio.run(sources.rxnorm_normalize(" \t "))
    assert result["found"] is False and result["error"] == "empty_drug_name"


def test_combination_lists_only_atomic_ingredients(monkeypatch):
    async def request(method, url, **kwargs):
        if url.endswith("/rxcui.json"):
            data = {"idGroup": {"rxnormId": ["151392"]}}
        elif url.endswith("/properties.json"):
            data = {"properties": {"name": "Augmentin", "tty": "BN"}}
        else:
            data = {
                "relatedGroup": {
                    "conceptGroup": [
                        {
                            "tty": "IN",
                            "conceptProperties": [{"name": "amoxicillin"}, {"name": "clavulanate"}],
                        },
                        {
                            "tty": "MIN",
                            "conceptProperties": [{"name": "amoxicillin / clavulanate"}],
                        },
                    ]
                }
            }
        return httpx.Response(200, json=data)

    monkeypatch.setattr(sources.http, "request", request)
    result = asyncio.run(sources.rxnorm_normalize("Augmentin"))
    assert result["ingredients"] == ["amoxicillin", "clavulanate"]


def test_lactmed_heading_end_and_record_boundary():
    page = """<h2>Summary of Use during Lactation</h2>Clinical summary.
    <h3>Drug Levels</h3>Clinical levels.
    <h3>Alternate Drugs to Consider</h3>Alternative A.
    <h3>References</h3>1. Citation.<h2>Related information</h2>Sidebar drug.
    <h3>Drug Levels</h3>Unrelated record. <div>Copyright Notice</div>Footer."""
    result = sources.parse_lactmed_html(page)
    assert result["Summary of Use during Lactation"] == "Clinical summary."
    assert result["Drug Levels"] == "Clinical levels."
    assert result["Alternate Drugs to Consider"] == "Alternative A."
    assert "Sidebar" not in str(result) and "Unrelated" not in str(result)


def test_lactmed_stops_at_substance_metadata():
    page = "<h3>Drug Levels</h3><p>Clinical data.</p><h3>Substance Identification</h3><p>Metadata</p><h3>Drug Levels</h3><p>Noise</p>"
    assert sources.parse_lactmed_html(page) == {"Drug Levels": "Clinical data."}


def test_lactmed_no_raw_html_fallback(monkeypatch):
    async def ncbi(*args, **kwargs):
        return httpx.Response(
            200, json={"result": {"123": {"accessionid": "NBK123", "title": "Example"}}}
        )

    async def request(*args, **kwargs):
        return httpx.Response(
            200, text="<html><body>Challenge or unrelated navigation</body></html>"
        )

    monkeypatch.setattr(sources, "_ncbi", ncbi)
    monkeypatch.setattr(sources.http, "request", request)
    result = asyncio.run(sources.lactmed_record("123"))
    assert result["text"] == "" and result["error"] == "clinical_sections_unavailable"


def test_audit_failure_log_omits_exception_text(monkeypatch, caplog):
    async def failed_log(*args):
        raise RuntimeError("SYNTHETIC_PRIVATE_QUERY")

    monkeypatch.setattr(audit.lakehouse, "log_call", failed_log)
    with caplog.at_level(logging.WARNING, logger="mc"):
        asyncio.run(audit._safe_log("tool", "source", 1, True, None))
    assert "SYNTHETIC_PRIVATE_QUERY" not in caplog.text


def test_library_filter_scrubs_formatted_args_and_tracebacks():
    record = logging.LogRecord(
        "mcp.server", logging.ERROR, "", 1, "request=%s", ("PRIVATE_MARKER",), None
    )
    record.exc_text = "PRIVATE_MARKER traceback"
    record.stack_info = "PRIVATE_MARKER stack"
    assert audit.LibraryPrivacyFilter().filter(record)
    assert "PRIVATE_MARKER" not in logging.Formatter().format(record)


def test_trial_relevance_fields(monkeypatch):
    async def request(*args, **kwargs):
        return httpx.Response(
            200,
            json={
                "studies": [
                    {
                        "protocolSection": {
                            "identificationModule": {"nctId": "NCT123", "briefTitle": "Example"},
                            "statusModule": {"overallStatus": "COMPLETED"},
                            "conditionsModule": {"conditions": ["Gestational diabetes"]},
                            "armsInterventionsModule": {
                                "interventions": [{"type": "DRUG", "name": "Metformin"}]
                            },
                            "descriptionModule": {
                                "briefSummary": "Study of metformin in pregnancy."
                            },
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr(sources.http, "request", request)
    row = asyncio.run(sources.trials_search("metformin"))[0]
    assert row["interventions"][0]["name"] == "Metformin"
    assert row["conditions"] == ["Gestational diabetes"]


def test_reporter_abstract_for_relevance(monkeypatch):
    async def request(*args, **kwargs):
        assert "AbstractText" in kwargs["json"]["include_fields"]
        return httpx.Response(
            200, json={"results": [{"project_title": "Example", "abstract_text": "A" * 2100}]}
        )

    monkeypatch.setattr(sources.http, "request", request)
    row = asyncio.run(sources.reporter_search("breastfeeding"))[0]
    assert len(row["abstract"]) == 2000 and row["abstract_truncated"]


@pytest.mark.parametrize(
    "ids", [[], ["MALFORMED_123"], ["https://pubmed.ncbi.nlm.nih.gov/123/"], ["123", "bad"], ["0"]]
)
def test_bad_pmids_rejected_without_upstream_reinterpretation(monkeypatch, ids):
    async def forbidden(*args, **kwargs):
        raise AssertionError("Must not call NCBI")

    monkeypatch.setattr(sources, "_ncbi", forbidden)
    with pytest.raises(ValueError, match="Invalid PMID"):
        asyncio.run(sources.pubmed_abstracts(ids))


def test_valid_pmid_still_retrieves_abstract(monkeypatch):
    async def ncbi(*args, **kwargs):
        assert kwargs["id"] == "123"
        return httpx.Response(
            200,
            text="<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Test</ArticleTitle></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>",
        )

    monkeypatch.setattr(sources, "_ncbi", ncbi)
    assert asyncio.run(sources.pubmed_abstracts(["123"]))[0]["pmid"] == "123"


def test_legacy_nursing_mothers_code_is_not_false_warning():
    xml = '<document xmlns="urn:hl7-org:v3"><section><code code="34080-2"/><title>8.3 Nursing Mothers</title><text>Milk evidence.</text></section></document>'
    assert sources.dailymed_section_warnings(xml) == []
    assert "Milk evidence." in sources.parse_dailymed_sections(xml)["lactation"]
