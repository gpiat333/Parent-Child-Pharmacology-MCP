"""A local client must work without disabling DNS-rebinding protection."""
import asyncio
from starlette.requests import HTTPConnection
from mcp.server.transport_security import TransportSecurityMiddleware
from server import mcp

def test_local_transport_allows_loopback_and_rejects_untrusted_hosts_and_origins():
    middleware = TransportSecurityMiddleware(mcp.settings.transport_security)
    assert middleware.settings.enable_dns_rebinding_protection
    for host, origin, expected in [
        ('127.0.0.1:18080', None, None),
        ('localhost:8000', 'http://localhost:8000', None),
        ('[::1]:8000', None, None),
        ('attacker.example:18080', None, 421),
        ('localhost.attacker.example:18080', None, 421),
        ('127.0.0.1:18080', 'https://attacker.example', 403),
    ]:
        headers = [(b'host', host.encode()), (b'content-type', b'application/json')]
        if origin: headers.append((b'origin', origin.encode()))
        connection = HTTPConnection({'type': 'http', 'headers': headers})
        response = asyncio.run(middleware.validate_request(connection, is_post=True))
        assert (response.status_code if response else None) == expected
