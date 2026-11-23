"""The summary brief keeps every axis and count while leaving long source text out."""

import json

from parent_child_pharmacology.core.axis_display import axis_notices
from parent_child_pharmacology.core.brief_summary import PASSAGES_PER_LIST, summarize


def passage(n):
    return {
        "text": f"Finding {n}.",
        "source": "LactMed (lactation only): Effects in Breastfed Infants",
        "url": "https://example.gov/record",
        "pmid": None,
        "evidence_kind": "lactmed_section",
        "study_context": "source_context_requires_review",
        "population_context": {"source_population": ["lactation"], "notice": "n" * 300},
        "evidence_base": {"interpretation": "i" * 300},
        "source_balance_context": {"text": "c" * 2000},
    }


def brief(found=12):
    axis = {
        "axis": "fetal_infant_outcomes",
        "items": [passage(n) for n in range(found)],
        "context_only": [],
        "reported_gaps": [passage(99)],
        "state": "source_passages_retrieved",
        "not_evidence_of_safety": True,
        "empty_message": None,
    }
    empty = {**axis, "items": [], "reported_gaps": [], "state": "none_retrieved"}
    return {
        "drug_input": "sertraline",
        "axis_set": "pregnancy_lactation",
        "evidence_axes": [
            {"axis": "maternal_effects", "by_ingredient": [{**empty, "axis": "maternal_effects"}]},
            {
                "axis": "fetal_infant_exposure",
                "by_ingredient": [{**empty, "axis": "fetal_infant_exposure"}],
            },
            {"axis": "fetal_infant_outcomes", "by_ingredient": [axis]},
        ],
        "ingredient_evidence": [
            {
                "ingredient": "sertraline",
                "lactmed": {
                    "url": "https://example.gov/record",
                    "text": "t" * 9000,
                    "sections": {},
                },
                "literature": {
                    "results": [
                        {"pmid": str(n), "title": "T", "extra": "x" * 500} for n in range(9)
                    ],
                    "articles": [{"pmid": "1", "abstract": "a" * 3000}],
                    "abstract_coverage": {"requested_count": 9},
                },
                "trials": {
                    "studies": [{"nct": "NCT00000001", "status": "COMPLETED", "summary": "s"}]
                },
            }
        ],
    }


def test_summary_keeps_all_axes_and_reports_totals():
    out = summarize(brief())
    outcomes = out["evidence_axes"][2]["by_ingredient"][0]
    assert [a["axis"] for a in out["evidence_axes"]] == [
        "maternal_effects",
        "fetal_infant_exposure",
        "fetal_infant_outcomes",
    ]
    assert len(outcomes["items"]) == PASSAGES_PER_LIST and outcomes["items_total"] == 12
    assert outcomes["omitted_in_summary"] == {"items": 12 - PASSAGES_PER_LIST}
    assert outcomes["reported_gaps_total"] == 1 and outcomes["not_evidence_of_safety"]
    empty = out["evidence_axes"][0]["by_ingredient"][0]
    assert empty["items"] == [] and empty["items_total"] == 0 and empty["state"] == "none_retrieved"


def test_summary_passages_keep_text_source_and_population_only():
    item = summarize(brief())["evidence_axes"][2]["by_ingredient"][0]["items"][0]
    assert (
        item["text"] == "Finding 0." and item["url"] and item["source_population"] == ["lactation"]
    )
    assert "source_balance_context" not in item and "evidence_base" not in item


def test_summary_names_what_it_left_out_and_is_much_smaller():
    full = brief()
    out = summarize(full)
    row = out["ingredient_evidence"][0]
    assert "text" not in row["lactmed"] and "text" in row["lactmed"]["omitted_in_summary"]
    assert len(row["literature"]["results"]) == 5 and row["literature"]["results_total"] == 9
    assert "articles" in row["literature"]["omitted_in_summary"]
    assert row["literature"]["abstract_coverage"] == {"requested_count": 9}
    assert set(row["trials"]["studies"][0]) == {"nct", "status"}
    assert out["detail"] == "summary" and "detail='full'" in out["coverage_notice"]
    assert len(json.dumps(out)) < len(json.dumps(full)) / 4
    assert "text" in full["ingredient_evidence"][0]["lactmed"]  # the input is not modified


def test_stops_pass_through_unchanged():
    stop = {"requires_confirmation": True, "note": "Confirm the exact medicine."}
    assert summarize(stop) is stop


def test_axis_inventory_counts_all_retrieved_passages_not_only_those_listed():
    result = summarize(brief(found=12))
    notice = axis_notices([{"tool": "medication_evidence_brief", "result": result}])[0]
    assert "12" in notice["text"]


def test_condensed_brief_is_not_re_annotated_and_keeps_its_retrieved_status():
    from parent_child_pharmacology.core.evidence import annotate

    full = brief()
    full["evidence_status"] = {"state": "retrieved", "no_evidence_retrieved": False}
    out = annotate(summarize(full))
    row = out["ingredient_evidence"][0]
    # LactMed text was retrieved, then left out of the summary: status must still say retrieved.
    assert out["evidence_status"]["state"] == "retrieved"
    assert "framing_contract" not in row["lactmed"] and "content_flags" not in row["lactmed"]
    assert out["framing_contract"]["preserve_source_balance_context"]
    assert "population_context" not in row["literature"]["results"][0]


def test_summary_keeps_medicine_taker_label_sections_for_parent_questions():
    full = brief()
    full["ingredient_evidence"][0]["label"] = {
        "sections": {"lactation": "x" * 4000},
        "medicine_taker_sections": {"adverse_reactions": {"text": "Nausea was reported."}},
    }
    label = summarize(full)["ingredient_evidence"][0]["label"]
    assert label["medicine_taker_sections"]["adverse_reactions"]["text"] == "Nausea was reported."
    assert "sections" in label["omitted_in_summary"]
