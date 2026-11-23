"""Render all three brief axes as metadata independently of model prose."""

import json
from pathlib import Path

POLICY = json.loads(Path(__file__).with_suffix(".json").read_text(encoding="utf-8"))


def unpack(value):
    if not isinstance(value, dict):
        return {}
    if isinstance(value.get("structuredContent"), dict):
        return value["structuredContent"]
    for block in value.get("content", []):
        if block.get("type") == "text":
            try:
                decoded = json.loads(block["text"])
                if isinstance(decoded, dict):
                    return decoded
            except (ValueError, KeyError, TypeError):
                pass
    return value


def axis_notices(tool_calls):
    latest = {}
    for call in tool_calls:
        if call.get("tool") != "medication_evidence_brief":
            continue
        result = unpack(call.get("result"))
        if (
            result.get("error")
            or result.get("allow_research") is False
            or result.get("requires_confirmation")
        ):
            continue
        latest[str(result.get("drug_input", "brief"))] = result
    if not latest:
        return []
    lines = [POLICY["title"]]
    for index, result in enumerate(latest.values(), 1):
        if len(latest) > 1:
            lines.append(f"Brief {index}")
        lines += [
            "| Evidence axis | Extracted findings | Context-only passages | Gap statements |",
            "|---|---|---:|---:|",
        ]
        axes = result.get("evidence_axes", [])
        for key, label in POLICY["axes"].items():
            matches = (
                [a for a in axes if isinstance(a, dict) and a.get("axis") == key]
                if isinstance(axes, list)
                else []
            )
            groups = matches[0].get("by_ingredient") if len(matches) == 1 else None
            valid = (
                isinstance(groups, list)
                and bool(groups)
                and all(
                    isinstance(g, dict)
                    and all(
                        isinstance(g.get(f), list)
                        for f in ["items", "context_only", "reported_gaps"]
                    )
                    for g in groups
                )
            )
            if valid:
                counts = {
                    f: sum(len(g[f]) for g in groups)
                    for f in ["items", "context_only", "reported_gaps"]
                }
                status = (
                    POLICY["found"].replace("{n}", str(counts["items"]))
                    if counts["items"]
                    else POLICY["empty"]
                )
                context, gaps = str(counts["context_only"]), str(counts["reported_gaps"])
            else:
                status, context, gaps = POLICY["missing"], "unknown", "unknown"
            lines.append(f"| {label} | {status} | {context} | {gaps} |")
    lines.append(POLICY["note"])
    return [
        {
            "id": "three_axis_inventory",
            "text": "\n".join(lines),
            "origin": "Application structural retrieval inventory; not clinical findings",
            "display_required": True,
        }
    ]
