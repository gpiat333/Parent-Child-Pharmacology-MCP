import asyncio
from datetime import datetime
from io import BytesIO

import pytest
from openpyxl import Workbook

from parent_child_pharmacology.mc import pediatric_labels as p


def fixture(headers=None, date_value=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "FDA changes"
    ws.append(headers or list(p.COLUMNS))
    ws.append(
        [
            "NDA 1",
            date_value or datetime(2020, 1, 2),
            "Example tablet",
            "example hydrochloride",
            "BPCA and PREA",
            "Condition",
            "Children 6 years and older",
            "Not established below age 6.",
            "Category",
            "TABLET",
            "ORAL",
            None,
            "No",
        ]
    )
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    return stream.getvalue()


def test_parser_preserves_scope_null_and_row():
    row = p.parse_workbook(fixture())[0]
    assert row["labeling_change_date"] == "2020-01-02"
    assert row["studied_in_neonates"] is None
    assert row["indicated_in_neonates"] == "No"
    assert row["source_row"] == 2 and row["source_sheet"] == "FDA changes"
    assert row["labeling_change_summary"] == "Not established below age 6."


def test_schema_drift_fails_closed():
    with pytest.raises(ValueError, match="schema"):
        p.parse_workbook(fixture(["Different schema"]))


def test_invalid_date_fails_closed():
    with pytest.raises(ValueError, match="date format"):
        p.parse_workbook(fixture(date_value="unknown"))


@pytest.mark.parametrize("query", ["example", "EXAMPLE", "example hydrochloride"])
def test_names_and_case(query):
    assert p.select_records(p.parse_workbook(fixture()), query, "any", 10)[1] == 1


@pytest.mark.parametrize("query", ["exam", "Condition", "6", "unrelated"])
def test_no_substring_or_indication_matches(query):
    assert p.select_records(p.parse_workbook(fixture()), query, "any", 10)[1] == 0


@pytest.mark.parametrize("legislation", ["BPCA", "PREA"])
def test_both_legislation_categories(legislation):
    assert p.select_records(p.parse_workbook(fixture()), "example", legislation, 10)[1] == 1


def test_order_count_and_limit():
    row = p.parse_workbook(fixture())[0]
    rows = [row, dict(row, labeling_change_date="2025-01-01")]
    selected, count = p.select_records(rows, "example", "any", 1)
    assert count == 2 and selected[0]["labeling_change_date"] == "2025-01-01"


def test_validation_does_not_fetch(monkeypatch):
    async def no_fetch(*args, **kwargs):
        raise AssertionError("network called")

    monkeypatch.setattr(p.http, "request", no_fetch)
    assert asyncio.run(p.search(" "))["error"] == "invalid_drug"
