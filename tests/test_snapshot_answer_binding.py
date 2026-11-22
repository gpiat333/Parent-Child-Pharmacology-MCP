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
                    "results": [
                        {"pmid": "101", "doi": "10.test/right"},
                        {"pmid": "202", "doi": "10.test/other"},
                    ]
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


def test_wrong_record_cannot_be_returned_under_the_selected_pmid(tmp_path, monkeypatch):
    obj = agent(
        tmp_path,
        monkeypatch,
        [
            call("find_mprint_records", {"drug": "example"}),
            call(
                "return_source_value",
                {"source_call_index": 1, "value_path": "/results/1/doi", "record_pmid": "101"},
            ),
            call(
                "return_source_value",
                {"source_call_index": 1, "value_path": "/results/0/doi", "record_pmid": "101"},
            ),
        ],
    )
    assert obj.run("fixture", "Find the identifier") == "10.test/right"
    capture = json.loads((tmp_path / "fixture.json").read_text())
    assert capture["calls"][2]["result"]["error"] == "ValueError"
    assert capture["completed"] and capture["calls"][3]["result"]["record_pmid"] == "101"


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
