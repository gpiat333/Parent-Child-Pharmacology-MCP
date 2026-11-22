"""Exercise the benchmark client's source binding with invented records."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


def agent(tmp_path, monkeypatch, replies):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("snapshot_agent", root / "eval/phoenix/agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class MCP:
        def rpc(self, *args):
            return {
                "tools": [{"name": "find_mprint_records", "description": "test", "inputSchema": {}}]
            }

        def call(self, name, args):
            value = (
                {"allow_research": True}
                if name == "route_parent_question"
                else {
                    "classification_legend": {},
                    "offset": 0,
                    "has_more": False,
                    "matching_records": 2,
                    "results": [
                        {"pmid": "101", "doi": "10.test/right", "silver_classifications": []},
                        {"pmid": "202", "doi": "10.test/other", "silver_classifications": []},
                    ],
                }
            )
            return {"tool": name, "arguments": args, "result": value}

        def close(self):
            pass

    sequence = iter(replies)
    obj = module.ParentChildPharmacologyAgent.__new__(module.ParentChildPharmacologyAgent)
    obj.output, obj.replay_only, obj.prompt_version, obj.prompt = tmp_path, False, "v3", "test"
    obj.gateway = SimpleNamespace(
        MCP=MCP, model_call=lambda *a, **k: {"choices": [{"message": next(sequence)}]}
    )
    monkeypatch.setenv("AGENT_MODEL", "fixture-model")
    return obj


def call(name, args):
    return {
        "role": "assistant",
        "tool_calls": [
            {
                "id": name,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)},
            }
        ],
    }


def test_metadata_answer_cannot_skip_selection_or_mismatch_pmid(tmp_path, monkeypatch):
    obj = agent(
        tmp_path,
        monkeypatch,
        [
            call("find_mprint_records", {"drug": "example"}),
            call(
                "return_source_value",
                {"source_call_index": 1, "value_path": "/results/1/doi", "record_pmid": "202"},
            ),
            call(
                "select_snapshot_records",
                {
                    "source_call_indices": [1],
                    "required_labels": [],
                    "excluded_labels": [],
                    "zero_outcome_table": None,
                    "require_complete": True,
                    "sort_pmid": "ascending",
                    "limit": 1,
                },
            ),
            call(
                "return_source_value",
                {"source_call_index": 3, "value_path": "/results/0/doi", "record_pmid": "202"},
            ),
            call(
                "return_source_value",
                {"source_call_index": 3, "value_path": "/results/0/doi", "record_pmid": "101"},
            ),
        ],
    )
    assert obj.run("fixture", "Find the identifier") == "10.test/right"
    capture = json.loads((tmp_path / "fixture.json").read_text())
    assert capture["calls"][2]["result"]["error"] == "ValueError"
    assert capture["calls"][4]["result"]["error"] == "ValueError"
    assert capture["completed"] and capture["calls"][5]["result"]["record_pmid"] == "101"


def test_unbound_free_form_answer_is_not_accepted(tmp_path, monkeypatch):
    obj = agent(
        tmp_path,
        monkeypatch,
        [
            {"role": "assistant", "content": "10.test/invented"},
            {"role": "assistant", "content": "UNKNOWN"},
        ],
    )
    assert obj.run("fixture", "Find the identifier") == "UNKNOWN"
