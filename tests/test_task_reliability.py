"""General task, routing and calculation regressions; no benchmark answers in runtime."""

import asyncio
import json
import sqlite3

import pytest

from parent_child_pharmacology.clients import mprint_data as m
from parent_child_pharmacology.core import research_arithmetic as math_tool
from parent_child_pharmacology.core.language import english_confidence
from parent_child_pharmacology.core.output_notices import format_required_notices
from parent_child_pharmacology.core.safety import route


@pytest.mark.parametrize(
    "clause",
    [
        "For each exposure compute maximum minus minimum.",
        "Check Silver labels for all nine.",
        "Compute the mean minus the median for each outcome.",
    ],
)
def test_english_mathematical_clauses(clause):
    assert english_confidence("Inspect the public study dataset. " + clause)["confident_english"]


@pytest.mark.parametrize(
    "clause",
    [
        "¿Puedo tomar este medicamento durante la lactancia?",
        "No quiero vivir y quiero hacer daño a mi bebé.",
        "For each exposure compute maximum minus minimum. ¿Cuánto debo tomar?",
    ],
)
def test_math_instruction_does_not_override_foreign_request(clause):
    assert not route("Inspect the public study dataset. " + clause)["allow_research"]


def test_aggregate_seizure_measure_is_not_an_active_symptom():
    assert route(
        "Read the study outcome rows for control of seizures after exposure.",
        language_required=False,
    )["allow_research"]


@pytest.mark.parametrize(
    "suffix",
    [
        " My child is having seizures.",
        " I want to harm myself.",
        " My baby is not breathing.",
        " We need control of seizures now.",
    ],
)
def test_research_wrapper_cannot_hide_personal_danger(suffix):
    assert not route(
        "This is a dataset audit about seizure control." + suffix, language_required=False
    )["allow_research"]


def test_study_team_handoff_is_appended_once_and_suppressed_on_stop():
    text, ids = format_required_notices("One record returned.", ["find_recruiting_studies"])
    assert "study_team_confirmation" in ids and "must confirm eligibility" in text
    assert format_required_notices(text, ["find_recruiting_studies"])[0] == text
    assert not format_required_notices("Stopped.", ["find_recruiting_studies"], blocked=True)[1]


def test_mprint_enriched_pages_keep_distinct_labels_and_export_counts(tmp_path, monkeypatch):
    db = tmp_path / "mprint.sqlite"
    with sqlite3.connect(db) as con:
        con.executescript(
            "CREATE TABLE gold(pmid TEXT,drug TEXT,population TEXT,study_type TEXT,payload TEXT); CREATE TABLE silver(pmid TEXT,study_type TEXT,source_row INTEGER);"
        )
        for pmid in ["101", "102", "103"]:
            payload = json.dumps({"source_file": "fixture.csv", "source_row": 1})
            con.execute(
                "INSERT INTO gold VALUES(?,?,?,?,?)", (pmid, "example", "Lactation", "PK", payload)
            )
        con.executemany(
            "INSERT INTO silver VALUES(?,?,?)",
            [("103", "PK", 1), ("103", "PK", 2), ("103", "CT", 3)],
        )
    for parity in [0, 1]:
        with sqlite3.connect(tmp_path / f"outcomes-{parity}.sqlite") as con:
            con.execute("CREATE TABLE outcomes(pmid TEXT,kind TEXT)")
            if parity == 1:
                con.executemany(
                    "INSERT INTO outcomes VALUES(?,?)",
                    [("103", "PK_summary"), ("103", "PK_summary")],
                )
    monkeypatch.setattr(m, "DATABASE", db)
    monkeypatch.setattr(m, "OUTCOMES_DATABASE", tmp_path / "outcomes.sqlite")
    monkeypatch.setattr(m, "_base", lambda tier: {"dataset_revision": "fixture"})
    first = asyncio.run(
        m.search_gold("example", 2, "lactation", "PK", include_classifications=True)
    )
    second = asyncio.run(
        m.search_gold(
            "example",
            2,
            "lactation",
            "PK",
            offset=first["next_offset"],
            include_classifications=True,
        )
    )
    assert [r["pmid"] for r in first["results"] + second["results"]] == ["103", "102", "101"]
    item = first["results"][0]
    assert item["silver_distinct_label_count"] == 2
    assert item["exported_outcome_rows"] == {"PK_summary": 2, "PE_CT": 0}
    assert second["next_offset"] is None and first["matching_records"] == 3
    assert "not independent studies" in item["classification_join_notice"]


@pytest.mark.parametrize(
    "expression,places,expected",
    [("(7/32 - 2/19)*100", 2, "11.35"), ("(15-8)-(20-16)", 0, "3"), ("0.1+0.2", 1, "0.3")],
)
def test_decimal_arithmetic_is_deterministic(expression, places, expected):
    assert math_tool.calculate(expression, places)["result"] == expected


@pytest.mark.parametrize(
    "expression",
    ["__import__('os').getcwd()", "2**999999", "[1][0]", "True+1", "1/0", "1e999", "sum([1,2])"],
)
def test_calculator_rejects_code_and_unbounded_operations(expression):
    with pytest.raises((ValueError, SyntaxError)):
        math_tool.calculate(expression, 2)
