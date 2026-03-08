"""Tests for AccountsAPI."""

import pytest

from src.api.accounts import AccountsAPI
from src.utils.config import Config


class FakeHTTPClient:
    """Minimal async transport stub."""

    def __init__(self, response):
        self._response = response
        self.calls = []

    async def get_json(self, url, *, headers=None, params=None):
        self.calls.append({"url": url, "headers": headers, "params": params})
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


@pytest.mark.asyncio
async def test_get_organization_environments(monkeypatch):
    """It requests the configured organization environments."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    http_client = FakeHTTPClient({"data": [{"id": "env-1"}]})
    client = AccountsAPI("token", http_client, config=Config())

    response = await client.get_organization_environments()

    assert response == {"data": [{"id": "env-1"}]}
    assert http_client.calls == [
        {
            "url": "https://example.com/accounts/api/organizations/org-id/environments",
            "headers": {"Authorization": "Bearer token"},
            "params": {"extended": "false", "resolveTheme": "false"},
        }
    ]
