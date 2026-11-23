"""Small read-only tool loop using the already-authorized Databricks gateway.

Uses the same MCP protocol and credential boundary as the existing paired runner.
No LangChain or additional model-provider credential is required.
"""

import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

from parent_child_pharmacology.core.research_arithmetic import SCHEMA, calculate
from parent_child_pharmacology.core.snapshot_select import SCHEMA as SELECT_SCHEMA
from parent_child_pharmacology.core.snapshot_select import select_records
from parent_child_pharmacology.core.source_value import SCHEMA as VALUE_SCHEMA
from parent_child_pharmacology.core.source_value import copy_source_value


def expects_source_label(question):
    """Recognize an explicit label-return clause; ambiguous formats stay unrestricted."""
    clauses = re.findall(r"\breturn\b([^.!?]*)", question, flags=re.I)
    if any(
        re.search(
            r"\b(number|numeric|integer|decimal|count|sum|difference|rate|proportion)\b", c, re.I
        )
        for c in clauses
    ):
        return False
    return any(re.search(r"\b(label|string|doi|name)\b", c, re.I) for c in clauses)


class ParentChildPharmacologyAgent:
    def __init__(self, evidence_directory, prompt_version="v6", replay_only=False):
        self.root = Path(evidence_directory).resolve()
        self.replay_only = replay_only
        self.prompt_version = prompt_version
        sys.path.insert(0, str(self.root))
        repo_root = Path(os.environ.get("MCP_REPO_ROOT", Path(__file__).resolve().parents[2]))
        sys.path.insert(0, str(repo_root / "chat-client"))
        spec = importlib.util.spec_from_file_location(
            "benchmark_gateway", self.root / "paired_evaluation.py"
        )
        self.gateway = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.gateway)
        self.prompt = (
            Path(__file__).parent / "prompts" / f"system_prompt_{prompt_version}.txt"
        ).read_text()
        self.output = self.root / "benchmark"
        self.output.mkdir(exist_ok=True)

    def run(self, identifier, question):
        destination = self.output / f"{identifier}.json"
        if self.replay_only:
            capture = json.loads(destination.read_text(encoding="utf-8"))
            if capture["question"] != question:
                raise ValueError("Captured question differs from the frozen dataset")
            # Replay every outcome, including UNKNOWN and fixed stops; no model
            # calls, selection, answer edits or regeneration are permitted.
            return capture["answer"]
        if destination.exists():
            raise ValueError("Existing benchmark capture; never replace an answer based on score")
        started, calls, usage = time.monotonic(), [], []
        client = self.gateway.MCP()
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": question},
        ]
        answer, completed, error = "UNKNOWN", False, None
        try:
            gate = client.call("route_parent_question", {"question": question})
            calls.append(gate)
            if not gate["result"].get("allow_research"):
                raise ValueError("Question stopped by preflight")
            names = {"find_mprint_records", "get_mprint_details"}
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["inputSchema"],
                    },
                }
                for t in client.rpc("tools/list", {})["tools"]
                if t["name"] in names
            ]
            tools.extend([SCHEMA, VALUE_SCHEMA, SELECT_SCHEMA])
            for _ in range(24):
                reply = self.gateway.model_call(messages, tools, reasoning_effort="none")
                usage.append(reply.get("usage", {}))
                message = reply["choices"][0]["message"]
                messages.append(message)
                if not message.get("tool_calls"):
                    if (message.get("content") or "").strip() == "UNKNOWN":
                        answer, completed = "UNKNOWN", True
                        break
                    messages.append(
                        {
                            "role": "system",
                            "content": "Finish using return_source_value with a field from a captured result. Do not transcribe an answer from memory. If no supported value exists, return UNKNOWN.",
                        }
                    )
                    continue
                for call in message["tool_calls"]:
                    name = call["function"]["name"]
                    if name not in names | {
                        "calculate_aggregate_expression",
                        "return_source_value",
                        "select_snapshot_records",
                    }:
                        raise ValueError("Unexpected benchmark tool")
                    raw_arguments = call["function"]["arguments"]
                    argument_error = False
                    try:
                        arguments = json.loads(raw_arguments)
                        if not isinstance(arguments, dict):
                            raise ValueError("Tool arguments must be an object")
                    except (ValueError, TypeError):
                        argument_error = True
                        arguments = {"invalid_arguments": str(raw_arguments)[:3000]}
                    if name == "find_mprint_records" and not argument_error:
                        arguments["resolve_names"] = False
                        arguments["include_classifications"] = True
                    if argument_error:
                        result = {
                            "tool": name,
                            "arguments": arguments,
                            "result": {
                                "error": "InvalidToolArguments",
                                "message": "No operation executed. Retry with one valid JSON object matching this tool's schema.",
                            },
                            "execution": "local argument validation; no MCP call",
                        }
                    elif name == "return_source_value":
                        try:
                            index = arguments.get("source_call_index")
                            if (
                                expects_source_label(question)
                                and type(index) is int
                                and 0 <= index < len(calls)
                                and calls[index].get("tool") == "calculate_aggregate_expression"
                            ):
                                raise ValueError(
                                    "The question explicitly requests a source label, string, DOI or name. A calculator value is intermediate; return the requested source field instead."
                                )
                            value = copy_source_value(
                                calls, **arguments, require_metadata_selection=True
                            )
                            answer, completed = value["value"], True
                        except (ValueError, TypeError) as exc:
                            value = {"error": type(exc).__name__, "message": str(exc)}
                        result = {
                            "tool": name,
                            "arguments": arguments,
                            "result": value,
                            "execution": "local source-field binding; not an MCP retrieval",
                        }
                    elif name == "select_snapshot_records":
                        try:
                            value = select_records(calls, **arguments)
                        except (ValueError, TypeError) as exc:
                            value = {"error": type(exc).__name__, "message": str(exc)}
                        result = {
                            "tool": name,
                            "arguments": arguments,
                            "result": value,
                            "execution": "local captured-metadata filtering; not an MCP retrieval",
                        }
                    elif name == "calculate_aggregate_expression":
                        try:
                            value = calculate(**arguments)
                        except (ValueError, TypeError, SyntaxError) as exc:
                            value = {"error": type(exc).__name__, "message": str(exc)}
                        result = {
                            "tool": name,
                            "arguments": arguments,
                            "result": value,
                            "execution": "local bounded arithmetic; not an MCP retrieval",
                        }
                    else:
                        result = client.call(name, arguments)
                    calls.append(result)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "content": json.dumps(
                                {"source_call_index": len(calls) - 1, "result": result["result"]},
                                ensure_ascii=False,
                            ),
                        }
                    )
                    if completed:
                        break
                if completed:
                    break
            if not completed:
                error = "tool_round_limit"
        except Exception as exc:
            error = type(exc).__name__
        finally:
            client.close()
        capture = {
            "id": identifier,
            "question": question,
            "answer": answer,
            "completed": completed,
            "error": error,
            "calls": calls,
            "usage": usage,
            "model": os.environ["AGENT_MODEL"],
            "reasoning_effort": "none",
            "prompt_version": self.prompt_version,
            "elapsed_seconds": round(time.monotonic() - started, 2),
        }
        destination.write_text(json.dumps(capture, indent=2, ensure_ascii=False), encoding="utf-8")
        return answer
