"""Tool wrapper: error envelope, disclaimer injection, non-blocking audit logging."""

import asyncio
import functools
import inspect
import logging
import time
import uuid

from parent_child_pharmacology.clients import lakehouse
from parent_child_pharmacology.core import config as cfg

from .http import UpstreamUnavailable, request_provenance
from .response import normalize

log = logging.getLogger("mc")
_tasks: set[asyncio.Task] = set()


class LibraryPrivacyFilter(logging.Filter):
    """Keep library severity/name, but not arbitrary exception/request contents."""

    def filter(self, record):
        if record.name.split(".")[0] in {"mcp", "httpx", "httpcore", "databricks", "uvicorn"}:
            record.msg = "Library event; request and exception details omitted for privacy"
            record.args = ()
            record.exc_info = None
            record.exc_text = None
            record.stack_info = None
        return True


def _fire(coro) -> None:
    t = asyncio.create_task(coro)
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)


async def _safe_log(*a) -> None:
    try:
        await lakehouse.log_call(*a)
    except Exception as e:  # never let audit failure affect a tool
        log.warning("audit log failed (%s)", type(e).__name__)


# Answers may repeat this server's notices; say who wrote them so attribution is verifiable.
NOTICE_ATTRIBUTION = (
    "Notices, interpretation rules, routing messages and clinician questions in this result (for example "
    "continuity_of_care_notice, coverage and population notices, deadline interpretations and "
    "required_display_notices) are written by this MCP server, Parent-child Pharmacology MCP. They are not "
    "quoted from the cited sources. When repeating one, attribute it to this MCP server, never to a cited "
    "source or dataset author."
)


# Free-text arguments that are screened like a question before any source is called.
SCREENED_ARGUMENTS = {
    "drug",
    "name",
    "query",
    "question",
    "topic",
    "condition_or_drug",
    "drug_or_topic",
    "ingredient",
}
# A short medicine or topic selector is data, not an English sentence.
SELECTOR_ARGUMENTS = SCREENED_ARGUMENTS - {"question"}


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from _strings(item)


def _screen_arguments(name, bound):
    """Return a stop payload when the arguments must not reach a source, else None.

    The router itself handles urgent concerns before privacy, so it is not screened here.
    Other tools must not forward obvious identifiers to external evidence services, and a
    dose, crisis or override request does not become allowed by being sent to a data tool.
    """
    if name == "route_parent_question":
        return None
    from .language import scientific_selector
    from .safety import contains_identifiers, route

    if any(contains_identifiers(text) for text in _strings((bound.args, bound.kwargs))):
        return {
            "source": "validation",
            "error": "identifying_input",
            "allow_research": False,
            "note": "Remove contact details, birth dates and medical record numbers; use a general research query.",
        }
    for key, value in bound.arguments.items():
        if key not in SCREENED_ARGUMENTS or not isinstance(value, str) or not value.strip():
            continue
        selector = key in SELECTOR_ARGUMENTS and scientific_selector(value)
        decision = route(value, language_required=not selector)
        if not decision["allow_research"]:
            return decision
    return None


def _failure(name, exc):
    """Turn an exception into an error payload without leaking request or upstream detail."""
    error_id = uuid.uuid4().hex
    log.warning("tool %s failed (%s), error_id=%s", name, type(exc).__name__, error_id)
    out = {
        "error": type(exc).__name__,
        "error_id": error_id,
        "note": "Tool failed. Retry, or try a different tool/source.",
    }
    if isinstance(exc, UpstreamUnavailable):
        out["error"] = "upstream_unavailable"
        out["retry_hint"] = {
            "retryable": exc.retryable,
            "retry_after_seconds": exc.retry_after,
            "reason": exc.reason,
        }
    return out


def _participation_tier(name, out):
    """Mark participation results as unranked navigation, emptied on any stop."""
    from .participation import TOOLS, tier

    if not isinstance(out, dict) or name not in TOOLS:
        return out
    return tier(
        out,
        suppressed=out.get("allow_research") is False or bool(out.get("requires_confirmation")),
        reason=out.get("route") or out.get("error"),
    )


def _envelope(name, out, provenance):
    """Add the safety metadata, shared response fields and required display notices."""
    from .abstract_coverage import disclosure_notices
    from .output_notices import POLICY, required_notices
    from .safety import envelope

    if isinstance(out, dict):
        out.setdefault("safety", envelope(out))
        out.setdefault("disclaimer", cfg.DISCLAIMER)
        out.setdefault("notice_attribution", NOTICE_ATTRIBUTION)
    out = normalize(out, provenance)
    stopped = (
        out.get("allow_research") is False
        or bool(out.get("requires_confirmation"))
        or bool(out.get("error"))
    )
    out["required_display_notices"] = required_notices([name], blocked=stopped)
    # Source failures need coverage disclosure; policy and identity stops do not.
    if out.get("allow_research") is not False and not out.get("requires_confirmation"):
        out["required_display_notices"] += disclosure_notices(
            [{"tool": name, "result": out}], POLICY["abstract_coverage"]
        )
    return out


def audited(fn):
    """Wrap a tool: screen its arguments, run it, and return one consistent envelope."""
    name = fn.__name__

    @functools.wraps(fn)  # preserves signature so FastMCP builds the right JSON schema
    async def wrapper(*args, **kwargs):
        started, error = time.perf_counter(), None
        provenance = []
        token = request_provenance.set(provenance)
        try:
            try:
                bound = inspect.signature(fn).bind(*args, **kwargs)
                out = _screen_arguments(name, bound)
                if out is None:
                    out = await fn(*args, **kwargs)
                    if isinstance(out, dict):
                        bound.apply_defaults()
                        if "population" in bound.arguments:
                            from .population import preserve_population

                            out = preserve_population(out, bound.arguments["population"])
                out = _participation_tier(name, out)
            except Exception as exc:
                error = type(exc).__name__
                out = _failure(name, exc)
            if isinstance(out, dict) and out.get("error"):
                error = error or "tool_error"
            out = _envelope(name, out, provenance)
        finally:
            request_provenance.reset(token)
        if cfg.USE_LAKEHOUSE:
            source = out.get("source", "n/a") if isinstance(out, dict) else "n/a"
            elapsed = int((time.perf_counter() - started) * 1000)
            _fire(_safe_log(name, str(source), elapsed, error is None, error))
        return out

    return wrapper
