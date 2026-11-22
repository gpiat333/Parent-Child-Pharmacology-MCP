"""Bounded allowlisted HTTPS retrieval, retries, cache and provenance."""

import asyncio
import logging
import random
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import httpx

from .config import CACHE_TTL_SECONDS

request_provenance = ContextVar("request_provenance", default=None)
APPROVED_HOSTS = frozenset(
    {
        "eutils.ncbi.nlm.nih.gov",
        "www.ncbi.nlm.nih.gov",
        "dailymed.nlm.nih.gov",
        "rxnav.nlm.nih.gov",
        "clinicaltrials.gov",
        "api.reporter.nih.gov",
        "api.fda.gov",
        "www.fda.gov",
        "wsearch.nlm.nih.gov",
        "connect.medlineplus.gov",
        "www.nichd.nih.gov",
        "dash.nichd.nih.gov",
        "www.federalregister.gov",
    }
)
MAX_RESPONSE_BYTES = 5_000_000
for name in ("httpx", "httpcore"):
    logging.getLogger(name).disabled = True


class UpstreamUnavailable(RuntimeError):
    def __init__(self, reason, retry_after=None, *, retryable=True):
        super().__init__("Upstream unavailable")
        self.reason, self.retry_after, self.retryable = reason, retry_after, retryable


def validate_destination(url):
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname in APPROVED_HOSTS
            and parsed.port in (None, 443)
            and not parsed.username
            and not parsed.password
            and not parsed.fragment
            and "\\" not in url
            and not any(ord(c) < 32 for c in url)
        )
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise UpstreamUnavailable("destination_blocked", retryable=False)
    return parsed.hostname


def retry_delay(value):
    if value is None:
        return None
    try:
        return max(0, float(value))
    except (ValueError, TypeError):
        try:
            return max(
                0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            )
        except (ValueError, TypeError, OverflowError):
            return None


class Http:
    def __init__(self):
        from .egress import PinnedTransport

        self._c = httpx.AsyncClient(
            transport=PinnedTransport(),
            timeout=30,
            follow_redirects=False,
            trust_env=False,
            headers={"User-Agent": "parent-child-pharmacology-mcp/0.12"},
        )
        self._locks, self._last, self._cache = {}, {}, {}

    async def _throttle(self, host, interval):
        async with self._locks.setdefault(host, asyncio.Lock()):
            delay = self._last.get(host, 0) + interval - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            self._last[host] = time.monotonic()

    def _record(self, response, host, cache_hit):
        records = request_provenance.get()
        if records is not None:
            records.append(
                {
                    "host": host,
                    "retrieved_at": response.extensions["retrieved_at"],
                    "cache_hit": cache_hit,
                    "source_version": response.headers.get("etag")
                    or response.headers.get("last-modified")
                    or "not_provided_by_upstream",
                }
            )

    async def _fetch(self, method, url, params, json):
        request = self._c.build_request(method, url, params=params, json=json)
        response = await self._c.send(request, stream=True, follow_redirects=False)
        try:
            if 300 <= response.status_code < 400:
                raise UpstreamUnavailable("redirect_blocked", retryable=False)
            size = response.headers.get("content-length")
            if size and size.isdecimal() and int(size) > MAX_RESPONSE_BYTES:
                raise UpstreamUnavailable("response_too_large", retryable=False)
            content = bytearray()
            async for chunk in response.aiter_bytes():
                if len(content) + len(chunk) > MAX_RESPONSE_BYTES:
                    raise UpstreamUnavailable("response_too_large", retryable=False)
                content.extend(chunk)
            headers = {
                k: v
                for k, v in response.headers.items()
                if k.lower() not in {"content-encoding", "content-length", "transfer-encoding"}
            }
            return httpx.Response(
                response.status_code,
                headers=headers,
                content=bytes(content),
                request=response.request,
            )
        finally:
            await response.aclose()

    async def request(
        self, method, url, *, params=None, json=None, ttl=0, interval=0.05, bypass_cache=False
    ):
        host = validate_destination(url)
        ttl = min(ttl, CACHE_TTL_SECONDS.get(host, ttl)) if ttl else 0
        key = (
            (url, repr(sorted((params or {}).items()))) if ttl and method.upper() == "GET" else None
        )
        if key and not bypass_cache:
            cached = self._cache.get(key)
            if cached and cached[0] > time.monotonic():
                self._record(cached[1], host, True)
                return cached[1]
        reason, after = "unknown", None
        for attempt in range(3):
            await self._throttle(host, interval)
            try:
                response = await self._fetch(method, url, params, json)
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    reason = f"HTTP {response.status_code}"
                    after = retry_delay(response.headers.get("Retry-After"))
                    if after is not None and after > 30:
                        raise UpstreamUnavailable(reason, after)
                else:
                    response.raise_for_status()
                    response.extensions["retrieved_at"] = datetime.now(timezone.utc).isoformat()
                    if key:
                        self._cache[key] = (time.monotonic() + ttl, response)
                        if len(self._cache) > 500:
                            self._cache.pop(next(iter(self._cache)))
                    self._record(response, host, False)
                    return response
            except httpx.TransportError as exc:
                reason, after = type(exc).__name__, None
            if attempt < 2:
                await asyncio.sleep(
                    after if after is not None else 2**attempt + random.uniform(0, 0.25)
                )
        raise UpstreamUnavailable(reason, after)


http = Http()
