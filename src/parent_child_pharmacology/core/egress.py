"""Resolve once, reject non-public answers, and connect only to a validated IP.

HTTP Core retains the original origin for Host and certificate/SNI verification.
No proxies or Unix sockets are supported. This is application enforcement, not
a claim that a cloud firewall has been provisioned.
"""

import asyncio
import ipaddress
import socket
import ssl

import certifi
import httpcore
import httpx


def public_ip(value):
    ip = ipaddress.ip_address(value)
    if isinstance(ip, ipaddress.IPv6Address):
        # Reject transition/tunnel addresses as well as local and reserved space.
        if ip.ipv4_mapped or ip.sixtofour or ip.teredo or ip.scope_id:
            return False
    return ip.is_global and not (ip.is_multicast or ip.is_reserved)


async def resolve(host, port):
    answers = await asyncio.get_running_loop().getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return list(dict.fromkeys(answer[4][0] for answer in answers))


class PinnedBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, resolver=resolve, backend=None):
        self.resolver = resolver
        self.backend = backend or httpcore.AnyIOBackend()

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        from .http import APPROVED_HOSTS, UpstreamUnavailable

        if host not in APPROVED_HOSTS or port != 443:
            raise UpstreamUnavailable("destination_blocked", retryable=False)
        try:
            async with asyncio.timeout(timeout or 30):
                addresses = await self.resolver(host, port)
                if not addresses or not all(public_ip(ip) for ip in addresses):
                    raise UpstreamUnavailable("non_public_dns_answer", retryable=False)
                # Passing a numeric IP prevents a second hostname resolution.
                stream = await self.backend.connect_tcp(
                    addresses[0], port, timeout, local_address, socket_options
                )
                peer = stream.get_extra_info("server_addr")
                if not peer or ipaddress.ip_address(peer[0]) != ipaddress.ip_address(addresses[0]):
                    await stream.aclose()
                    raise UpstreamUnavailable("peer_address_mismatch", retryable=False)
                return stream
        except (OSError, ValueError) as exc:
            raise httpcore.ConnectError("DNS or connection failed") from exc
        except TimeoutError as exc:
            raise httpcore.ConnectTimeout("DNS or connection timed out") from exc

    async def connect_unix_socket(self, *args, **kwargs):
        raise httpcore.ConnectError("Unix sockets are disabled")

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)


class ResponseStream(httpx.AsyncByteStream):
    def __init__(self, stream):
        self.stream = stream

    async def __aiter__(self):
        try:
            async for chunk in self.stream:
                yield chunk
        except httpcore.TimeoutException as exc:
            raise httpx.ReadTimeout("Upstream read timed out") from exc
        except (httpcore.NetworkError, httpcore.ProtocolError) as exc:
            raise httpx.ReadError("Upstream read failed") from exc

    async def aclose(self):
        await self.stream.aclose()


class PinnedTransport(httpx.AsyncBaseTransport):
    def __init__(self, backend=None):
        self.pool = httpcore.AsyncConnectionPool(
            ssl_context=ssl.create_default_context(cafile=certifi.where()),
            network_backend=backend or PinnedBackend(),
            max_connections=20,
            max_keepalive_connections=10,
        )

    async def handle_async_request(self, request):
        from .http import validate_destination

        validate_destination(str(request.url))
        core_request = httpcore.Request(
            method=request.method,
            url=httpcore.URL(
                scheme=request.url.raw_scheme,
                host=request.url.raw_host,
                port=request.url.port,
                target=request.url.raw_path,
            ),
            headers=request.headers.raw,
            content=request.stream,
            extensions=request.extensions,
        )
        try:
            response = await self.pool.handle_async_request(core_request)
        except httpcore.TimeoutException as exc:
            raise httpx.ConnectTimeout("Upstream connection timed out", request=request) from exc
        except (httpcore.NetworkError, httpcore.ProtocolError) as exc:
            raise httpx.ConnectError("Upstream connection failed", request=request) from exc
        return httpx.Response(
            response.status,
            headers=response.headers,
            stream=ResponseStream(response.stream),
            extensions=response.extensions,
        )

    async def aclose(self):
        await self.pool.aclose()
