"""Tests for AuthClient."""

import pytest

from src.auth.client import AuthClient
from src.utils.config import Config
from tests.conftest import FakeHTTPClient


@pytest.mark.asyncio
async def test_get_access_token_fetches_and_caches(monkeypatch):
    """It fetches the token once and reuses the cached value."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    http_client = FakeHTTPClient(post_responder=lambda url, **kwargs: {"access_token": "token-1"})
    client = AuthClient(http_client, config=Config())

    first_token = await client.get_access_token()
    second_token = await client.get_access_token()

    assert first_token == "token-1"
    assert second_token == "token-1"
    assert http_client.calls == [
        {
            "method": "POST",
            "url": "https://example.com/accounts/api/v2/oauth2/token",
            "headers": None,
            "params": None,
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

    responses = iter(
        [{"access_token": "token-1"}, {"access_token": "token-2"}]
    )
    http_client = FakeHTTPClient(
        post_responder=lambda url, **kwargs: next(responses)
    )

    client = AuthClient(http_client, config=Config())

    assert await client.get_access_token() == "token-1"
    assert await client.refresh_token() == "token-2"
