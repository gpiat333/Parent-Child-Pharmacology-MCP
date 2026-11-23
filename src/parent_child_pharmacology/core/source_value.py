"""Copy a scalar from a captured tool result without model transcription.

Client utility, not an MCP tool. This binds an answer to an observed field; it
does not determine whether the model selected the right record for a question.
"""

import math
import re

SCHEMA = {
    "type": "function",
    "function": {
        "name": "return_source_value",
        "description": "Finish the snapshot lookup by copying exactly one scalar from an observed tool result. Supply its source_call_index, JSON pointer within that result, and enclosing record PMID when present. No free-form answer is accepted. For a calculation, point to the calculator's /result. This does not validate clinical meaning or candidate selection.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_call_index": {"type": "integer", "minimum": 0},
                "value_path": {"type": "string", "maxLength": 512},
                "record_pmid": {"type": ["string", "null"]},
            },
            "required": ["source_call_index", "value_path", "record_pmid"],
            "additionalProperties": False,
        },
    },
}


def copy_source_value(
    calls, source_call_index, value_path, record_pmid, *, require_metadata_selection=False
):
    if type(source_call_index) is not int or not 0 <= source_call_index < len(calls):
        raise ValueError("Unknown source call")
    call = calls[source_call_index]
    if call.get("tool") not in {
        "find_mprint_records",
        "get_mprint_details",
        "calculate_aggregate_expression",
        "select_snapshot_records",
        "aggregate_outcome_rows",
    }:
        raise ValueError("Not a research-value source")
    if require_metadata_selection and call.get("tool") == "find_mprint_records":
        raise ValueError(
            "Metadata answers must use select_snapshot_records on the original candidate cohort, with the requested filters and ordering. Copy the selected field or filtered count from that result, not from an unfiltered or narrowed lookup."
        )
    if not isinstance(value_path, str) or not value_path.startswith("/") or len(value_path) > 512:
        raise ValueError("Use a bounded JSON pointer within the captured result")
    if value_path.startswith("/result/"):
        value_path = value_path[len("/result") :]  # Explicit reply-envelope prefix.
    node = call["result"]
    if not isinstance(node, dict) or node.get("error"):
        raise ValueError("Source result failed")
    pmid = None
    for token in value_path[1:].split("/"):
        if re.search(r"~(?![01])", token):
            raise ValueError("Invalid JSON pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if node.get("error"):
                raise ValueError("Source branch failed")
            if node.get("pmid") is not None:
                pmid = str(node["pmid"])
            if token not in node:
                raise ValueError("Field not present")
            node = node[token]
        elif isinstance(node, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token) or int(token) >= len(node):
                raise ValueError("Invalid result index")
            node = node[int(token)]
        else:
            raise ValueError("Pointer continues past a scalar")
    if record_pmid != pmid:
        raise ValueError("Record PMID does not match the selected field's enclosing record")
    if type(node) not in (str, int, float) or isinstance(node, float) and not math.isfinite(node):
        raise ValueError("Select one finite scalar, not a missing value or container")
    value = str(node)
    if not value.strip() or len(value) > 2048:
        raise ValueError("Empty or oversized answer value")
    return {
        "value": value,
        "source_call_index": source_call_index,
        "value_path": value_path,
        "record_pmid": pmid,
        "scope": "Exact source-field copy only; candidate selection remains unverified",
    }
