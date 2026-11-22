"""Trusted application notices, selected by tool identity rather than model prose."""

import json
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name("output_notices.json").read_text(encoding="utf-8"))


def required_notices(tool_names, blocked=False, tool_calls=()):
    if blocked:
        return []
    names = set(tool_names)
    from .abstract_coverage import disclosure_notices
    from .axis_display import axis_notices

    return (
        [
            {"id": n["id"], "text": n["text"], "origin": POLICY["origin"], "display_required": True}
            for n in POLICY["notices"]
            if names.intersection(n["tools"])
        ]
        + disclosure_notices(tool_calls, POLICY["abstract_coverage"])
        + axis_notices(tool_calls)
    )


def format_required_notices(answer, tool_names, blocked=False, tool_calls=()):
    """Append missing fixed lines; leave evidence and source caveats untouched."""
    notices = required_notices(tool_names, blocked, tool_calls)
    lines = {line.strip() for line in answer.splitlines()}
    missing = [
        n["text"]
        for n in notices
        if (
            ("\n" + n["text"] + "\n") not in ("\n" + answer.strip() + "\n")
            if "\n" in n["text"]
            else n["text"] not in lines
        )
    ]
    if missing:
        answer = answer.rstrip() + "\n\nApplication limits:\n" + "\n".join(missing)
    return answer, [n["id"] for n in notices]
