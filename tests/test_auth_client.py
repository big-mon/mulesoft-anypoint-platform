"""Tests for AuthClient."""

import pytest

from src.auth.client import AuthClient
from src.utils.config import Config


class FakeHTTPClient:
    """Minimal async transport stub."""

    def __init__(self, response):
        self._response = response
        self.calls = []

    async def post_json(self, url, *, headers=None, data=None):
        self.calls.append({"url": url, "headers": headers, "data": data})
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


@pytest.mark.asyncio
async def test_get_access_token_fetches_and_caches(monkeypatch):
    """It fetches the token once and reuses the cached value."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    http_client = FakeHTTPClient({"access_token": "token-1"})
    client = AuthClient(http_client, config=Config())

    first_token = await client.get_access_token()
    second_token = await client.get_access_token()

    assert first_token == "token-1"
    assert second_token == "token-1"
    assert http_client.calls == [
        {
            "url": "https://example.com/accounts/api/v2/oauth2/token",
            "headers": None,
            "data": {
                "grant_type": "client_credentials",
                "client_id": "client-id",
                "client_secret": "client-secret",
            },
        }
    ]


@pytest.mark.asyncio
async def test_refresh_token_forces_refetch(monkeypatch):
    """It drops the cache before requesting a new token."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")

    class SequencedHTTPClient:
        def __init__(self):
            self.responses = iter(
                [{"access_token": "token-1"}, {"access_token": "token-2"}]
            )

        async def post_json(self, url, *, headers=None, data=None):
            return next(self.responses)

    client = AuthClient(SequencedHTTPClient(), config=Config())

    assert await client.get_access_token() == "token-1"
    assert await client.refresh_token() == "token-2"
