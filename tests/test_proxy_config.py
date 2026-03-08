"""Tests for proxy configuration support."""

from src.utils.proxy import ProxyConfig


def test_proxy_config_uses_shared_proxy(monkeypatch):
    """A shared proxy should be applied to both HTTP and HTTPS."""
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://proxy.local:8080")
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)

    proxy_config = ProxyConfig()

    assert proxy_config.get_proxy_for_url("http://anypoint.mulesoft.com/test") == (
        "http://proxy.local:8080"
    )
    assert proxy_config.get_aiohttp_request_kwargs("https://anypoint.mulesoft.com/test") == {
        "proxy": "http://proxy.local:8080",
    }


def test_proxy_config_prefers_scheme_specific_proxy(monkeypatch):
    """Scheme-specific settings should override the shared proxy."""
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://shared-proxy.local:8080")
    monkeypatch.setenv("ANYPOINT_HTTP_PROXY", "http://http-proxy.local:8080")
    monkeypatch.setenv("ANYPOINT_HTTPS_PROXY", "http://https-proxy.local:8443")

    proxy_config = ProxyConfig()

    assert proxy_config.get_proxy_for_url("http://anypoint.mulesoft.com/test") == (
        "http://http-proxy.local:8080"
    )
    assert proxy_config.get_proxy_for_url("https://anypoint.mulesoft.com/test") == (
        "http://https-proxy.local:8443"
    )
