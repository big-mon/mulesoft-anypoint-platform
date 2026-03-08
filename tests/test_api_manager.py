"""Tests for APIManagerClient."""

import aiohttp
import pytest
from unittest.mock import patch

from src.api.api_manager import APIManagerClient


class MockResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(None, None, status=self.status)


@pytest.fixture
def api_manager_client(monkeypatch):
    """Build an API manager client without proxy settings."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    monkeypatch.delenv("ANYPOINT_PROXY_URL", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)
    token = "test_token"
    environments = [
        {
            "name": "test_env",
            "org_id": "test_org",
            "env_id": "test_env_id",
        }
    ]
    return APIManagerClient(token, environments)


@pytest.mark.asyncio
async def test_get_applications(api_manager_client):
    """Applications should be fetched without a proxy by default."""
    mock_response = {
        "total": 1,
        "applications": [
            {
                "id": "test_app_id",
                "name": "test_app",
                "version": "1.0.0",
            }
        ],
    }

    def mock_get(*args, **kwargs):
        assert kwargs["proxy"] is None
        return MockResponse(mock_response)

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await api_manager_client.get_applications()
        assert len(applications) == 1
        assert applications[0]["env_name"] == "test_env"
        assert applications[0]["org_id"] == "test_org"
        assert applications[0]["env_id"] == "test_env_id"


@pytest.mark.asyncio
async def test_get_applications_error(api_manager_client):
    """Client errors should be raised from the async request path."""

    def mock_get(*args, **kwargs):
        return MockResponse({"error": "failure"}, status=500)

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        with pytest.raises(aiohttp.ClientResponseError):
            await api_manager_client.get_applications()


@pytest.mark.asyncio
async def test_get_applications_uses_https_proxy(monkeypatch):
    """Configured HTTPS proxy should be passed to aiohttp requests."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    monkeypatch.setenv("ANYPOINT_HTTPS_PROXY", "http://proxy.local:8443")
    monkeypatch.delenv("ANYPOINT_PROXY_URL", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    client = APIManagerClient(
        "test_token",
        [{"name": "test_env", "org_id": "test_org", "env_id": "test_env_id"}],
    )

    def mock_get(*args, **kwargs):
        assert kwargs["proxy"] == "http://proxy.local:8443"
        return MockResponse({"assets": []})

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await client.get_applications()
        assert len(applications) == 1
