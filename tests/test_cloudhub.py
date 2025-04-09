"""CloudHubClientのテスト"""

import pytest
import aiohttp
from unittest.mock import Mock, patch, AsyncMock
from src.api.cloudhub import CloudHubClient


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
    mock_response = [
        {
            "domain": "test-app",
            "fullDomain": "test-app.cloudhub.io",
            "status": "STARTED",
            "muleVersion": "4.4.0",
            "properties": {
                "env": "test"
            }
        }
    ]

    class MockResponse:
        def __init__(self):
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def json(self):
            return mock_response

        def raise_for_status(self):
            if self.status >= 400:
                raise aiohttp.ClientResponseError(None, None, status=self.status)

    def mock_get(*args, **kwargs):
        return MockResponse()

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        applications = await cloudhub_client.get_applications()
        assert len(applications) == 1
        assert applications[0]["env_name"] == "test_env"
        assert applications[0]["domain"] == "test-app"
        assert applications[0]["status"] == "STARTED"


@pytest.mark.asyncio
async def test_get_applications_error(cloudhub_client):
    """アプリケーション取得のエラーテスト"""
    async def mock_get(*args, **kwargs):
        mock = Mock()
        mock.raise_for_status = Mock(side_effect=Exception("Test error"))
        mock.__aenter__ = Mock(return_value=mock)
        mock.__aexit__ = Mock(return_value=None)
        return mock

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        with pytest.raises(Exception):
            await cloudhub_client.get_applications()
