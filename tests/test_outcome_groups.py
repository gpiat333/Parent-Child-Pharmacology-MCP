"""Per-group statistics over captured outcome rows (benchmark client utility)."""

import pytest

from parent_child_pharmacology.core.outcome_groups import aggregate_rows
from parent_child_pharmacology.core.research_arithmetic import calculate
from parent_child_pharmacology.core.source_value import copy_source_value


def details(rows, pmid="123"):
    return {
        "tool": "get_mprint_details",
        "result": {"pmid": pmid, "results": [{"pmid": pmid, "source_fields": r} for r in rows]},
    }


ROWS = [
    {"Exposure": "Drug A", "Value": "0.7", "Outcome": "r"},
    {"Exposure": "Drug B", "Value": "0.65", "Outcome": "r"},
    {"Exposure": "Drug A", "Value": "0.34", "Outcome": "r"},
    {"Exposure": "Drug B", "Value": "0.48", "Outcome": "r"},
    {"Exposure": "Total", "Value": "9", "Outcome": "other"},
]


def test_range_is_computed_for_every_group_and_sorted():
    out = aggregate_rows(
        [details(ROWS)], 0, "Exposure", "Value", "range", [{"field": "Outcome", "equals": "r"}], 2
    )
    assert [(g["group"], g["statistic_value"]) for g in out["groups"]] == [
        ("Drug A", "0.36"),
        ("Drug B", "0.17"),
    ]
    assert out["groups_compared"] == 2 and out["groups"][0]["row_indices"] == [0, 2]


def test_group_label_is_copied_exactly_with_return_source_value():
    calls = [details(ROWS)]
    calls.append(
        {
            "tool": "aggregate_outcome_rows",
            "result": aggregate_rows(calls, 0, "Exposure", "Value", "range", [], 2),
        }
    )
    copied = copy_source_value(calls, 1, "/groups/0/group", "123")
    assert copied["value"] == "Drug A"


def test_count_and_ties_are_reported():
    rows = [{"Site": "Site 1", "Value": "0"}, {"Site": "Site 2", "Value": "1"}]
    out = aggregate_rows([details(rows)], 0, "Site", "Value", "max", [], 0)
    assert out["groups"][0]["group"] == "Site 2" and not out["groups"][0]["tied_for_largest"]
    out = aggregate_rows([details(rows)], 0, "Site", "Value", "count", [], 0)
    assert all(g["tied_for_largest"] for g in out["groups"])


def test_non_numeric_values_are_excluded_and_listed():
    rows = [{"Exposure": "A", "Value": "n/a"}, {"Exposure": "A", "Value": "2"}]
    out = aggregate_rows([details(rows)], 0, "Exposure", "Value", "max", [], 0)
    assert out["groups"][0]["statistic_value"] == "2" and out["excluded_rows"][0]["row"] == 0


def test_only_captured_outcome_tables_are_accepted():
    with pytest.raises(ValueError):
        aggregate_rows(
            [{"tool": "find_mprint_records", "result": {}}], 0, "Exposure", "Value", "range", [], 2
        )
    with pytest.raises(ValueError):
        aggregate_rows([details(ROWS)], 0, "Nope", "Value", "range", [], 2)


def test_calculator_supports_max_min_abs_but_nothing_else():
    assert calculate("max(0.7,0.7,0.34)-min(0.7,0.7,0.34)", 2)["result"] == "0.36"
    assert calculate("abs(0.3-0.5)", 1)["result"] == "0.2"
    for bad in ["__import__('os')", "max(x=1)", "pow(2,3)", "abs(1,2)"]:
        with pytest.raises((ValueError, SyntaxError)):
            calculate(bad, 0)
