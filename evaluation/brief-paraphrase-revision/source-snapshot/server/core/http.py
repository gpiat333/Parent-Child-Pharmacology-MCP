"""Shared HTTP: explicit TTL policy, bounded retries and request-local provenance."""
import asyncio
from contextvars import ContextVar
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
import random
import time
from urllib.parse import urlparse
import httpx

request_provenance = ContextVar('request_provenance', default=None)
from .config import CACHE_TTL_SECONDS
for name in ('httpx','httpcore'):
    logging.getLogger(name).disabled=True

class UpstreamUnavailable(RuntimeError):
    def __init__(self, reason, retry_after=None):
        super().__init__('Upstream unavailable')
        self.reason=reason
        self.retry_after=retry_after

def retry_delay(value):
    if value is None: return None
    try: return max(0,float(value))
    except (ValueError,TypeError):
        try: return max(0,(parsedate_to_datetime(value)-datetime.now(timezone.utc)).total_seconds())
        except (ValueError,TypeError,OverflowError): return None

class Http:
    def __init__(self):
        self._c=httpx.AsyncClient(timeout=30,follow_redirects=True,headers={'User-Agent':'parent-child-pharmacology-mcp/1.0'})
        self._locks={};self._last={};self._cache={}
    async def _throttle(self,host,interval):
        async with self._locks.setdefault(host,asyncio.Lock()):
            delay=self._last.get(host,0)+interval-time.monotonic()
            if delay>0: await asyncio.sleep(delay)
            self._last[host]=time.monotonic()
    def _record(self,r,host,cache_hit):
        records=request_provenance.get()
        if records is not None:
            records.append({'host':host,'retrieved_at':r.extensions['retrieved_at'],
                'cache_hit':cache_hit,'source_version':r.headers.get('etag') or r.headers.get('last-modified') or 'not_provided_by_upstream'})
    async def request(self,method,url,*,params=None,json=None,ttl=0,interval=0.05,bypass_cache=False):
        host=urlparse(url).netloc
        # Preserve adapter TTL intent, capped by centrally configured host policy.
        ttl=min(ttl,CACHE_TTL_SECONDS.get(host,ttl)) if ttl else 0
        key=(url,repr(sorted((params or {}).items()))) if ttl and method.upper()=='GET' else None
        if key and not bypass_cache:
            cached=self._cache.get(key)
            if cached and cached[0]>time.monotonic():
                self._record(cached[1],host,True);return cached[1]
        reason='unknown';after=None
        for attempt in range(3):
            await self._throttle(host,interval)
            try:
                r=await self._c.request(method,url,params=params,json=json)
                if r.status_code==429 or 500<=r.status_code<600:
                    reason=f'HTTP {r.status_code}';after=retry_delay(r.headers.get('Retry-After'))
                    # Do not retry sooner than Retry-After; long waits become a caller retry hint.
                    if after is not None and after>30: raise UpstreamUnavailable(reason,after)
                else:
                    r.raise_for_status()
                    r.extensions['retrieved_at']=datetime.now(timezone.utc).isoformat()
                    if key:
                        self._cache[key]=(time.monotonic()+ttl,r)
                        if len(self._cache)>500:self._cache.pop(next(iter(self._cache)))
                    self._record(r,host,False);return r
            except httpx.TransportError as exc:
                reason=type(exc).__name__;after=None
            if attempt<2:await asyncio.sleep(after if after is not None else 2**attempt+random.uniform(0,0.25))
        raise UpstreamUnavailable(reason,after)
http=Http()
