import copy
import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from parent_child_pharmacology.core.snapshot_select import select_records
from parent_child_pharmacology.core.source_value import copy_source_value


def page(drug="fixture", pmid=None, records=None):
    rows = records or [
        {"pmid": "101", "doi": "10.test/first", "silver_classifications": []},
        {"pmid": "202", "doi": "10.test/second", "silver_classifications": []},
    ]
    return {
        "tool": "find_mprint_records",
        "arguments": {"drug": drug, "pmid": pmid},
        "result": {
            "results": rows,
            "classification_legend": {},
            "offset": 0,
            "has_more": False,
            "matching_records": len(rows),
        },
    }


def select(calls, indices, complete=True):
    return select_records(calls, indices, [], [], None, complete, "ascending", 1)


@pytest.mark.parametrize("path,pmid", [("/matching_records", None), ("/results/0/doi", "101")])
def test_strict_copy_rejects_unselected_metadata_even_if_field_exists(path, pmid):
    with pytest.raises(ValueError, match="Metadata answers"):
        copy_source_value([page()], 0, path, pmid, require_metadata_selection=True)


def test_selected_metadata_and_arithmetic_remain_available():
    calls = [page()]
    calls.append({"tool": "select_snapshot_records", "result": select(calls, [0])})
    assert (
        copy_source_value(calls, 1, "/results/0/doi", "101", require_metadata_selection=True)[
            "value"
        ]
        == "10.test/first"
    )
    calls.append({"tool": "calculate_aggregate_expression", "result": {"result": "1.20"}})
    assert (
        copy_source_value(calls, 2, "/result", None, require_metadata_selection=True)["value"]
        == "1.20"
    )


@pytest.mark.parametrize("replacement", [page(None, "202"), page("different")])
def test_narrowed_identifier_or_changed_query_cannot_replace_original_cohort(replacement):
    with pytest.raises(ValueError, match="original candidate"):
        select([page(), replacement], [1])


def test_original_cohort_with_contiguous_pages_is_accepted():
    first = page()
    second = copy.deepcopy(first)
    first["result"].update(results=first["result"]["results"][:1], has_more=True, next_offset=1)
    second["result"].update(results=second["result"]["results"][1:], offset=1)
    result = select([first, second], [0, 1])
    assert result["distinct_count"] == 2 and result["results"][0]["pmid"] == "101"


def test_explicit_identifier_only_task_without_prior_cohort_is_supported():
    assert select([page(None, "101", [page()["result"]["results"][0]])], [0])["distinct_count"] == 1


def test_failed_initial_query_does_not_anchor_later_successful_query():
    failure = {
        "tool": "find_mprint_records",
        "arguments": {"drug": "misspelling"},
        "result": {"error": "lookup failed"},
    }
    assert select([failure, page()], [1])["distinct_count"] == 2


def test_nested_repeat_harness_imports_actual_client_modules(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    nested = tmp_path / "repeatability" / "run-2"
    nested.mkdir(parents=True)
    for name in ["paired_evaluation.py", "grader_contract.py", "model-call.ps1"]:
        shutil.copy2(root / "eval/harness" / name, nested / name)
    monkeypatch.setenv("MCP_REPO_ROOT", str(root))
    monkeypatch.setattr(
        sys, "path", [p for p in sys.path if not str(p).replace("\\", "/").endswith("/chat-client")]
    )
    monkeypatch.delitem(sys.modules, "url_checks", raising=False)
    monkeypatch.delitem(sys.modules, "grader_contract", raising=False)
    spec = importlib.util.spec_from_file_location(
        "nested_snapshot_agent", root / "eval/phoenix/agent.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    agent = module.ParentChildPharmacologyAgent(nested)
    assert agent.gateway.ROOT == root and agent.prompt_version == "v7"
    assert (agent.root / "model-call.ps1").is_file()
