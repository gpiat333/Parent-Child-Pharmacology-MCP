import pytest

from parent_child_pharmacology.core.source_value import copy_source_value


def records():
    return [
        {
            "tool": "find_mprint_records",
            "result": {
                "results": [
                    {"pmid": "101", "source_fields": {"DOI": "10.example/first"}},
                    {"pmid": "202", "source_fields": {"DOI": "10.example/second"}},
                ]
            },
        }
    ]


def test_copy_binds_the_actual_field_to_its_record():
    result = copy_source_value(records(), 0, "/results/0/source_fields/DOI", "101")
    assert result["value"] == "10.example/first"
    with pytest.raises(ValueError, match="PMID"):
        copy_source_value(records(), 0, "/results/1/source_fields/DOI", "101")


@pytest.mark.parametrize(
    "path", ["/results/-1", "/results/02", "/results/9", "/missing", "/results/0", "/results/~2"]
)
def test_invalid_or_container_paths_are_rejected(path):
    with pytest.raises(ValueError):
        copy_source_value(records(), 0, path, "101")


@pytest.mark.parametrize("value", [None, True, {}, [], float("inf"), "", "x" * 2049])
def test_not_every_payload_value_is_a_valid_answer(value):
    calls = [{"tool": "get_mprint_details", "result": {"value": value}}]
    with pytest.raises(ValueError):
        copy_source_value(calls, 0, "/value", None)


def test_calculator_precision_is_preserved_and_failed_calls_are_rejected():
    calls = [{"tool": "calculate_aggregate_expression", "result": {"result": "12.30"}}]
    assert copy_source_value(calls, 0, "/result", None)["value"] == "12.30"
    calls[0]["result"]["error"] = "ValueError"
    with pytest.raises(ValueError):
        copy_source_value(calls, 0, "/result", None)


def test_pointer_escaping_and_missing_record_identity():
    calls = [{"tool": "get_mprint_details", "result": {"pmid": "303", "a/b~c": 5}}]
    assert copy_source_value(calls, 0, "/a~1b~0c", "303")["value"] == "5"
    with pytest.raises(ValueError):
        copy_source_value(calls, 0, "/a~1b~0c", None)


@pytest.mark.parametrize("index", [-1, 1, True, "0"])
def test_unknown_or_untyped_call_index_is_rejected(index):
    with pytest.raises(ValueError):
        copy_source_value(records(), index, "/results/0/source_fields/DOI", "101")


def test_reply_envelope_prefix_preserves_field_and_record_binding():
    result = copy_source_value(records(), 0, "/result/results/0/source_fields/DOI", "101")
    assert result["value"] == "10.example/first"
    with pytest.raises(ValueError, match="PMID"):
        copy_source_value(records(), 0, "/result/results/1/source_fields/DOI", "101")


def test_filtered_count_can_be_copied_without_using_unfiltered_total():
    from parent_child_pharmacology.core.snapshot_select import select_records

    calls = [
        {
            "tool": "find_mprint_records",
            "arguments": {"drug": "fixture"},
            "result": {
                "classification_legend": {"CT": "clinical trial", "PE": "pharmacoepidemiology"},
                "offset": 0,
                "has_more": False,
                "matching_records": 2,
                "results": [
                    {"pmid": "101", "silver_classifications": [{"study_type": "CT"}]},
                    {"pmid": "202", "silver_classifications": [{"study_type": "PE"}]},
                ],
            },
        }
    ]
    filtered = select_records(calls, [0], ["CT"], ["PE"], None, True, "ascending", None)
    calls.append({"tool": "select_snapshot_records", "result": filtered})
    assert copy_source_value(calls, 1, "/distinct_count", None)["value"] == "1"
    assert calls[0]["result"]["matching_records"] == 2
