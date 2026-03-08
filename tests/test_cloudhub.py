"""Tests for CloudHubClient."""

import aiohttp
import pytest
from unittest.mock import patch

from src.api.cloudhub import CloudHubClient


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
def cloudhub_client(monkeypatch):
    """Build a CloudHub client without proxy settings."""
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
    return CloudHubClient(token, environments)


@pytest.mark.asyncio
async def test_get_applications(cloudhub_client):
    """Applications should be fetched without a proxy by default."""
    mock_data = [
        {
            "id": "test_app_id",
            "name": "test_app",
            "domain": "test-app",
            "fullDomain": "test-app.cloudhub.io",
            "status": "STARTED",
            "muleVersion": "4.4.0",
            "properties": {
                "env": "test"
            },
        }
    ]

    def mock_get(*args, **kwargs):
        assert kwargs["proxy"] is None
        return MockResponse(mock_data)

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await cloudhub_client.get_applications()
        assert len(applications) == 1
        assert applications[0]["env_name"] == "test_env"
        assert applications[0]["org_id"] == "test_org"
        assert applications[0]["env_id"] == "test_env_id"
        assert len(applications[0]["apis"]) == 1
        assert applications[0]["apis"][0]["domain"] == "test-app"
        assert applications[0]["apis"][0]["status"] == "STARTED"


@pytest.mark.asyncio
async def test_get_applications_error(cloudhub_client):
    """Client errors should be raised from the async request path."""

    def mock_get(*args, **kwargs):
        return MockResponse({"error": "Internal Server Error"}, status=500)

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        with pytest.raises(aiohttp.ClientResponseError):
            await cloudhub_client.get_applications()


@pytest.mark.asyncio
async def test_get_applications_uses_shared_proxy(monkeypatch):
    """Configured shared proxy should be passed to CloudHub aiohttp requests."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    monkeypatch.setenv("ANYPOINT_PROXY_URL", "http://proxy.local:8080")
    monkeypatch.delenv("ANYPOINT_HTTP_PROXY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTPS_PROXY", raising=False)
    client = CloudHubClient(
        "test_token",
        [{"name": "test_env", "org_id": "test_org", "env_id": "test_env_id"}],
    )

    def mock_get(*args, **kwargs):
        assert kwargs["proxy"] == "http://proxy.local:8080"
        return MockResponse([])

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await client.get_applications()
        assert len(applications) == 1
