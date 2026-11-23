"""Display executed portfolio criteria as data, independently of model prose."""

import json

from .axis_display import unpack


def portfolio_notices(tool_calls, templates):
    blocks = []
    for call in tool_calls:
        if call.get("tool") not in {"search_funded_research", "summarize_research_portfolio"}:
            continue
        raw = call.get("result")
        if isinstance(raw, dict) and raw.get("isError"):
            continue
        result = unpack(raw)
        if (
            result.get("error")
            or result.get("allow_research") is False
            or result.get("requires_confirmation")
        ):
            continue
        criteria = result.get("query_criteria")
        if not isinstance(criteria, dict):
            block = templates["missing"]
        else:
            data = json.dumps(criteria, ensure_ascii=False, separators=(",", ":"))
            block = (
                templates["oversized"]
                if len(data) > templates["max_chars"]
                else "```json\n" + data + "\n```"
            )
        blocks.append(f"Query {len(blocks) + 1} ({call['tool']})\n" + block)
    if not blocks:
        return []
    return [
        {
            "id": "reporter_query_filters",
            "text": templates["title"] + "\n" + "\n".join(blocks),
            "origin": "Application display of source query metadata; not a research finding",
            "display_required": True,
        }
    ]
