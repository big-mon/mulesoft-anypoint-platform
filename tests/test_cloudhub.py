"""CloudHubClientのテスト"""

import pytest
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from src.api.cloudhub import CloudHubClient


class MockResponse:
    def __init__(self):
        self.status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def json(self):
        return self.mock_data

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(None, None, status=self.status)


@pytest.fixture
def cloudhub_client():
    """CloudHubClientのフィクスチャ"""
    token = "test_token"
    environments = [
        {
            "name": "test_env",
            "org_id": "test_org",
            "env_id": "test_env_id"
        }
    ]
    return CloudHubClient(token, environments)


@pytest.mark.asyncio
async def test_get_applications(cloudhub_client):
    """アプリケーション取得のテスト"""
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
            }
        }
    ]

    def mock_get(*args, **kwargs):
        mock_response = MockResponse()
        mock_response.mock_data = mock_data
        return mock_response

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await cloudhub_client.get_applications()
        assert len(applications) == 1
        assert applications[0]["env_name"] == "test_env"
        assert applications[0]["domain"] == "test-app"
        assert applications[0]["status"] == "STARTED"


@pytest.mark.asyncio
async def test_get_applications_error(cloudhub_client):
    """アプリケーション取得のエラーテスト"""
    def mock_get(*args, **kwargs):
        mock_response = MockResponse()
        mock_response.status = 500
        mock_response.mock_data = {"error": "Internal Server Error"}
        return mock_response

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        with pytest.raises(aiohttp.ClientResponseError):
            await cloudhub_client.get_applications()
