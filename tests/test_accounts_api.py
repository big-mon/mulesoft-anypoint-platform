"""Tests for AccountsAPI."""

import pytest

from src.api.accounts import AccountsAPI
from src.utils.config import Config
from tests.conftest import FakeHTTPClient


def _set_required_env(monkeypatch, *, base_url, organization_id):
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", organization_id)
    monkeypatch.setenv("ANYPOINT_BASE_URL", base_url)


@pytest.mark.asyncio
async def test_get_organization_environments(monkeypatch):
    """It requests the configured organization environments."""
    _set_required_env(
        monkeypatch,
        base_url="https://example.com",
        organization_id="org-id",
    )
    http_client = FakeHTTPClient(
        get_responder=lambda url, **kwargs: {"data": [{"id": "env-1"}]}
    )
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


@pytest.mark.asyncio
async def test_get_organization_environments_normalizes_trailing_base_url_slash(
    monkeypatch,
):
    """It removes trailing slashes from the configured base URL."""
    _set_required_env(
        monkeypatch,
        base_url="https://example.com/",
        organization_id="org-id",
    )
    http_client = FakeHTTPClient(
        get_responder=lambda url, **kwargs: {"data": [{"id": "env-1"}]}
    )
    client = AccountsAPI("token", http_client, config=Config())

    response = await client.get_organization_environments()

    assert response == {"data": [{"id": "env-1"}]}
    assert http_client.calls[0]["url"] == (
        "https://example.com/accounts/api/organizations/org-id/environments"
    )
    assert http_client.calls[0]["headers"] == {"Authorization": "Bearer token"}
    assert http_client.calls[0]["params"] == {
        "extended": "false",
        "resolveTheme": "false",
    }


@pytest.mark.asyncio
async def test_get_organization_environments_trims_organization_id(monkeypatch):
    """It strips surrounding whitespace from the configured organization ID."""
    _set_required_env(
        monkeypatch,
        base_url="https://example.com",
        organization_id=" org-id ",
    )
    http_client = FakeHTTPClient(
        get_responder=lambda url, **kwargs: {"data": [{"id": "env-1"}]}
    )
    client = AccountsAPI("token", http_client, config=Config())

    response = await client.get_organization_environments()

    assert response == {"data": [{"id": "env-1"}]}
    assert http_client.calls[0]["url"] == (
        "https://example.com/accounts/api/organizations/org-id/environments"
    )
    assert http_client.calls[0]["headers"] == {"Authorization": "Bearer token"}
    assert http_client.calls[0]["params"] == {
        "extended": "false",
        "resolveTheme": "false",
    }
