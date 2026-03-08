"""Tests for AccountsAPI."""

import pytest

from src.api.accounts import AccountsAPI
from src.utils.config import Config
from tests.conftest import FakeHTTPClient


@pytest.mark.asyncio
async def test_get_organization_environments(monkeypatch):
    """It requests the configured organization environments."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    http_client = FakeHTTPClient(get_responder=lambda url, **kwargs: {"data": [{"id": "env-1"}]})
    client = AccountsAPI("token", http_client, config=Config())

    response = await client.get_organization_environments()

    assert response == {"data": [{"id": "env-1"}]}
    assert http_client.calls == [
        {
            "method": "GET",
            "url": "https://example.com/accounts/api/organizations/org-id/environments",
            "headers": {"Authorization": "Bearer token"},
            "data": None,
            "params": {"extended": "false", "resolveTheme": "false"},
        }
    ]
