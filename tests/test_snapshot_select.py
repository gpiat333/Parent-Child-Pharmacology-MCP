import copy

import pytest

from parent_child_pharmacology.core.snapshot_select import select_records


def data():
    rows = [
        {
            "pmid": str(i),
            "silver_classifications": [{"study_type": c} for c in codes],
            "exported_outcome_rows": {"PK_summary": n},
        }
        for i, codes, n in [
            (101, ["PK", "CT"], 0),
            (202, ["PK", "CT", "PE"], 0),
            (303, ["PK", "CT"], 2),
            (404, ["CT"], 0),
            (101, ["PK", "CT"], 0),
        ]
    ]
    return [
        {
            "tool": "find_mprint_records",
            "arguments": {"drug": "fixture", "population": "lactation", "study_type": "PK"},
            "result": {
                "results": rows,
                "classification_legend": {"PK": "PK", "CT": "CT", "PE": "PE"},
                "offset": 0,
                "has_more": False,
                "next_offset": None,
                "matching_records": 5,
                "dataset_revision": "fixture",
            },
        }
    ]


def choose(calls, **changes):
    args = {
        "source_call_indices": [0],
        "required_labels": ["PK", "CT"],
        "excluded_labels": ["PE"],
        "zero_outcome_table": "PK_summary",
        "require_complete": True,
        "sort_pmid": "ascending",
        "limit": None,
    }
    args.update(changes)
    return select_records(calls, **args)


def test_counts_filtered_distinct_pmids_not_candidates_or_labels():
    out = choose(data())
    assert out["distinct_count"] == 1 and [r["pmid"] for r in out["results"]] == ["101"]
    assert len(data()[0]["result"]["results"]) == 5


def test_sort_and_limit_preserve_the_filtered_total():
    out = choose(
        data(), excluded_labels=[], zero_outcome_table=None, sort_pmid="descending", limit=1
    )
    assert out["distinct_count"] == 3 and out["results"][0]["pmid"] == "303"


def test_unknown_count_does_not_mean_zero():
    calls = data()
    del calls[0]["result"]["results"][0]["exported_outcome_rows"]["PK_summary"]
    with pytest.raises(ValueError, match="unknown"):
        choose(calls)


def test_missing_join_and_unknown_labels_fail_closed():
    calls = data()
    del calls[0]["result"]["results"][0]["silver_classifications"]
    with pytest.raises(ValueError):
        choose(calls)
    with pytest.raises(ValueError):
        choose(data(), required_labels=["invented"])


def test_incomplete_pages_require_explicit_bounded_cohort():
    calls = data()
    calls[0]["result"].update(has_more=True, next_offset=5, matching_records=6)
    with pytest.raises(ValueError):
        choose(calls)
    assert choose(calls, require_complete=False)["distinct_count"] == 1


def test_all_pages_are_counted_and_deduplicated():
    calls = data()
    second = copy.deepcopy(calls[0])
    second["result"].update(
        results=[
            {
                "pmid": "505",
                "silver_classifications": [{"study_type": "PK"}, {"study_type": "CT"}],
                "exported_outcome_rows": {"PK_summary": 0},
            }
        ],
        offset=5,
        matching_records=6,
    )
    calls[0]["result"].update(has_more=True, next_offset=5, matching_records=6)
    calls.append(second)
    assert choose(calls, source_call_indices=[1, 0])["distinct_count"] == 2


def test_different_queries_cannot_be_combined():
    calls = data()
    other = copy.deepcopy(calls[0])
    other["arguments"]["drug"] = "other"
    calls.append(other)
    with pytest.raises(ValueError, match="different"):
        choose(calls, source_call_indices=[0, 1])


@pytest.mark.parametrize(
    "changes",
    [
        {"source_call_indices": [0, 0]},
        {"source_call_indices": [-1]},
        {"source_call_indices": [True]},
        {"required_labels": ["PK"], "excluded_labels": ["PK"]},
        {"limit": 0},
    ],
)
def test_invalid_filter_contracts_are_rejected(changes):
    with pytest.raises(ValueError):
        choose(data(), **changes)
