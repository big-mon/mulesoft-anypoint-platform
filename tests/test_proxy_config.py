"""Tests for proxy configuration support."""

from src.api.accounts import AccountsAPI
from src.auth.client import AuthClient
from src.utils.proxy import ProxyConfig


def test_proxy_config_uses_shared_proxy(monkeypatch):
    """A shared proxy should be applied to both HTTP and HTTPS."""
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://proxy.local:8080")
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)

    proxy_config = ProxyConfig()

    assert proxy_config.get_requests_proxies() == {
        "http": "http://proxy.local:8080",
        "https": "http://proxy.local:8080",
    }
    assert proxy_config.get_aiohttp_request_kwargs("https://anypoint.mulesoft.com/test") == {
        "proxy": "http://proxy.local:8080",
    }


def test_proxy_config_prefers_scheme_specific_proxy(monkeypatch):
    """Scheme-specific settings should override the shared proxy."""
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://shared-proxy.local:8080")
    monkeypatch.setenv("ANYPOINT_HTTP_PROXY", "http://http-proxy.local:8080")
    monkeypatch.setenv("ANYPOINT_HTTPS_PROXY", "http://https-proxy.local:8443")

    proxy_config = ProxyConfig()

    assert proxy_config.get_requests_proxies() == {
        "http": "http://http-proxy.local:8080",
        "https": "http://https-proxy.local:8443",
    }
    assert proxy_config.get_aiohttp_request_kwargs("https://anypoint.mulesoft.com/test") == {
        "proxy": "http://https-proxy.local:8443",
    }


def test_auth_client_uses_configured_proxy(monkeypatch):
    """Auth client should configure requests.Session proxies when provided."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://proxy.local:8080")
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)

    client = AuthClient()

    assert client._session.trust_env is False
    assert client._session.proxies == {
        "http": "http://proxy.local:8080",
        "https": "http://proxy.local:8080",
    }


def test_accounts_api_keeps_direct_requests_when_proxy_is_not_configured(monkeypatch):
    """Accounts API should not configure proxies if no proxy env vars are set."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.delenv("ANYPOINT_PROXY_URL", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)

    client = AccountsAPI("token")

    assert client._AccountsAPI__session.trust_env is False
    assert client._AccountsAPI__session.proxies == {}
