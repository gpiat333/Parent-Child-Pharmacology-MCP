"""Outbound policy tests exercise rejected requests and bounded streaming."""

import asyncio
import gzip

import httpx
import pytest

from parent_child_pharmacology.core import http as net


@pytest.mark.parametrize(
    "url",
    [
        "http://api.fda.gov/test",
        "https://127.0.0.1/",
        "https://[::1]/",
        "https://169.254.169.254/latest/meta-data/",
        "https://api.fda.gov.evil.example/",
        "https://api.fda.gov@evil.example/",
        "https://user:secret@api.fda.gov/",
        "https://api.fda.gov:8443/",
        "https://api.fda.gov./",
        "https://api.fda.gov/#x",
        "https://api.fda.gov\\@evil.example/",
        "https://evil.example/",
    ],
)
def test_unapproved_destination_never_reaches_transport(url):
    async def run():
        calls = []
        client = net.Http()
        await client._c.aclose()
        client._c = httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: calls.append(request) or httpx.Response(200)
            )
        )
        try:
            with pytest.raises(net.UpstreamUnavailable) as error:
                await client.request("GET", url)
            assert error.value.reason == "destination_blocked"
            assert not error.value.retryable and not calls
            assert url not in str(error.value)
        finally:
            await client._c.aclose()

    asyncio.run(run())


@pytest.mark.parametrize(
    "location", ["https://evil.example/secret", "/same-origin", "http://169.254.169.254/"]
)
def test_redirects_never_forward_query_credentials(location):
    async def run():
        seen = []

        def handler(request):
            seen.append(request)
            return httpx.Response(302, headers={"Location": location}, request=request)

        client = net.Http()
        await client._c.aclose()
        client._c = httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True)
        try:
            with pytest.raises(net.UpstreamUnavailable) as error:
                await client.request(
                    "GET",
                    "https://eutils.ncbi.nlm.nih.gov/test",
                    params={"api_key": "synthetic-secret"},
                )
            assert error.value.reason == "redirect_blocked"
            assert len(seen) == 1 and seen[0].url.host == "eutils.ncbi.nlm.nih.gov"
            assert "synthetic-secret" not in str(error.value)
        finally:
            await client._c.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("kind", ["declared", "chunked", "compressed"])
def test_response_size_limit_includes_decompressed_content(monkeypatch, kind):
    monkeypatch.setattr(net, "MAX_RESPONSE_BYTES", 64)

    async def run():
        content = b"x" * 65
        headers = {}
        if kind == "compressed":
            content = gzip.compress(content)
            headers["Content-Encoding"] = "gzip"
        if kind == "declared":
            headers["Content-Length"] = "65"

        def handler(request):
            response = httpx.Response(200, content=content, headers=headers, request=request)
            if kind == "chunked":
                del response.headers["Content-Length"]
            return response

        client = net.Http()
        await client._c.aclose()
        client._c = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        try:
            with pytest.raises(net.UpstreamUnavailable) as error:
                await client.request("GET", "https://api.fda.gov/test")
            assert error.value.reason == "response_too_large"
            assert not error.value.retryable and not client._cache
        finally:
            await client._c.aclose()

    asyncio.run(run())


def test_decoded_content_is_not_decompressed_twice():
    async def run():
        client = net.Http()
        await client._c.aclose()
        client._c = httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    200,
                    content=gzip.compress(b'{"ok":true}'),
                    headers={"Content-Encoding": "gzip", "ETag": "r1"},
                    request=r,
                )
            )
        )
        try:
            result = await client.request("GET", "https://api.fda.gov/test")
            assert result.json() == {"ok": True} and result.headers["etag"] == "r1"
        finally:
            await client._c.aclose()

    asyncio.run(run())


def test_environment_proxy_cannot_override_source_transport(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://unapproved-proxy.invalid:1234")
    monkeypatch.setenv("ALL_PROXY", "http://unapproved-proxy.invalid:1234")

    async def run():
        client = net.Http()
        try:
            # Proxy mounts route requests away from the approved direct transport.
            assert not any(t is not None for t in client._c._mounts.values())
        finally:
            await client._c.aclose()

    asyncio.run(run())
