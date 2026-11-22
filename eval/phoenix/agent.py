"""Small read-only tool loop using the already-authorized Databricks gateway.

Uses the same MCP protocol and credential boundary as the existing paired runner.
No LangChain or additional model-provider credential is required.
"""

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

from parent_child_pharmacology.core.research_arithmetic import SCHEMA, calculate


class ParentChildPharmacologyAgent:
    def __init__(self, evidence_directory, prompt_version="v2", replay_only=False):
        self.root = Path(evidence_directory).resolve()
        self.replay_only = replay_only
        sys.path.insert(0, str(self.root))
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
            tools.append(SCHEMA)
            for _ in range(24):
                reply = self.gateway.model_call(messages, tools, reasoning_effort="none")
                usage.append(reply.get("usage", {}))
                message = reply["choices"][0]["message"]
                messages.append(message)
                if not message.get("tool_calls"):
                    answer = message.get("content") or "UNKNOWN"
                    completed = True
                    break
                for call in message["tool_calls"]:
                    name = call["function"]["name"]
                    if name not in names | {"calculate_aggregate_expression"}:
                        raise ValueError("Unexpected benchmark tool")
                    arguments = json.loads(call["function"]["arguments"])
                    if name == "find_mprint_records":
                        arguments["resolve_names"] = False
                        arguments["include_classifications"] = True
                    if name == "calculate_aggregate_expression":
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
                            "content": json.dumps(result["result"], ensure_ascii=False),
                        }
                    )
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
            "prompt_version": "v2",
            "elapsed_seconds": round(time.monotonic() - started, 2),
        }
        destination.write_text(json.dumps(capture, indent=2, ensure_ascii=False), encoding="utf-8")
        return answer
