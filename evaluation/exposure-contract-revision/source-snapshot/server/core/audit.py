"""Tool wrapper: error envelope, disclaimer injection, non-blocking audit logging."""
import asyncio
import functools
import inspect
from .http import request_provenance, UpstreamUnavailable
from .response import normalize
import logging
import time
import uuid
import re

from core import config as cfg
from clients import lakehouse

log = logging.getLogger("mc")
_tasks: set[asyncio.Task] = set()


class LibraryPrivacyFilter(logging.Filter):
    """Keep library severity/name, but not arbitrary exception/request contents."""
    def filter(self, record):
        if record.name.split('.')[0] in {'mcp', 'httpx', 'httpcore', 'databricks'}:
            record.msg = 'Library event; request and exception details omitted for privacy'
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


def audited(fn):
    @functools.wraps(fn)  # preserves signature so FastMCP builds the right JSON schema
    async def wrapper(*args, **kwargs):
        t0, ok, err, out = time.perf_counter(), True, None, None
        provenance=[]
        token=request_provenance.set(provenance)
        try:
            from core.safety import contains_identifiers
            def strings(v):
                if isinstance(v,str): yield v
                elif isinstance(v,dict):
                    for x in v.values(): yield from strings(x)
                elif isinstance(v,(tuple,list)):
                    for x in v: yield from strings(x)
            # Router handles urgent concerns before privacy. Other tools must not
            # forward obvious identifiers to external evidence services.
            if fn.__name__!='route_parent_question' and any(contains_identifiers(x) for x in strings((args,kwargs))):
                out={'source':'validation','error':'identifying_input','allow_research':False,
                     'note':'Remove contact details, birth dates and medical record numbers; use a general research query.'}
            else:
                from .safety import route
                bound=inspect.signature(fn).bind(*args,**kwargs)
                blocked=None
                if fn.__name__!='route_parent_question':
                    for key,value in bound.arguments.items():
                        if key in {'drug','name','query','question','topic','condition_or_drug','drug_or_topic','ingredient'} and isinstance(value,str) and value.strip():
                            # A single medicine/topic identifier (or identifier plus
                            # controlled English population/focus words) is data,
                            # not an English sentence. Actual questions still require
                            # preflight; intent/identity rules still run here.
                            from .language import scientific_selector
                            selector=(key in {'drug','name','query','topic','condition_or_drug','drug_or_topic','ingredient'} and scientific_selector(value))
                            decision=route(value, language_required=not selector)
                            if not decision['allow_research']:
                                blocked=decision;break
                out=blocked if blocked else await fn(*args, **kwargs)
                if isinstance(out,dict) and not blocked:
                    bound.apply_defaults()
                    if 'population' in bound.arguments:
                        from .population import preserve_population
                        out=preserve_population(out,bound.arguments['population'])
            from .participation import TOOLS, tier
            if isinstance(out,dict) and fn.__name__ in TOOLS:
                out=tier(out,suppressed=out.get('allow_research') is False or bool(out.get('requires_confirmation')),
                         reason=out.get('route') or out.get('error'))
        except Exception as e:
            ok, err = False, type(e).__name__
            error_id = uuid.uuid4().hex
            log.warning("tool %s failed (%s), error_id=%s", fn.__name__, err, error_id)
            out = {"error": err, "error_id": error_id,
                   "note": "Tool failed. Retry, or try a different tool/source."}
            if isinstance(e,UpstreamUnavailable):
                out["error"]="upstream_unavailable"
                out["retry_hint"]={"retryable":True,"retry_after_seconds":e.retry_after,"reason":e.reason}
        try:
            if isinstance(out, dict):
                from core.safety import envelope
                out.setdefault("safety", envelope(out))
                out.setdefault("disclaimer", cfg.DISCLAIMER)
                if out.get("error"):
                    ok = False
                    err = err or "tool_error"
            out=normalize(out,provenance)
            from .output_notices import required_notices
            stopped = out.get('allow_research') is False or bool(out.get('requires_confirmation')) or bool(out.get('error'))
            out['required_display_notices'] = required_notices([fn.__name__], blocked=stopped)
        finally:
            request_provenance.reset(token)
        if cfg.USE_LAKEHOUSE:
            src = out.get("source", "n/a") if isinstance(out, dict) else "n/a"
            _fire(_safe_log(fn.__name__, str(src), int((time.perf_counter() - t0) * 1000), ok, err))
        return out
    return wrapper
