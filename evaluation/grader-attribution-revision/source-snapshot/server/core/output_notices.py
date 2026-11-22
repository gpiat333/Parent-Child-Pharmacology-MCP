"""Trusted application notices, selected by tool identity rather than model prose."""
import json
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name('output_notices.json').read_text(encoding='utf-8'))


def required_notices(tool_names, blocked=False):
    if blocked:
        return []
    names = set(tool_names)
    return [{'id':n['id'], 'text':n['text'], 'origin':POLICY['origin'], 'display_required':True}
            for n in POLICY['notices'] if names.intersection(n['tools'])]


def format_required_notices(answer, tool_names, blocked=False):
    """Append missing fixed lines; leave evidence and source caveats untouched."""
    notices = required_notices(tool_names, blocked)
    lines = {line.strip() for line in answer.splitlines()}
    missing = [n['text'] for n in notices if n['text'] not in lines]
    if missing:
        answer = answer.rstrip() + '\n\nApplication limits:\n' + '\n'.join(missing)
    return answer, [n['id'] for n in notices]
