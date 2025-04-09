"""APIManagerClientのテスト"""

import pytest
import aiohttp
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.api.api_manager import APIManagerClient


@pytest.fixture
def api_manager_client():
    """APIManagerClientのフィクスチャ"""
    token = "test_token"
    environments = [
        {
            "name": "test_env",
            "org_id": "test_org",
            "env_id": "test_env_id"
        }
    ]
    return APIManagerClient(token, environments)


@pytest.mark.asyncio
async def test_get_applications(api_manager_client):
    """アプリケーション取得のテスト"""
    mock_response = {
        "total": 1,
        "applications": [
            {
                "id": "test_app_id",
                "name": "test_app",
                "version": "1.0.0"
            }
        ]
    }

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
        applications = await api_manager_client.get_applications()
        assert len(applications) == 1
        assert applications[0]["env_name"] == "test_env"
        assert applications[0]["org_id"] == "test_org"
        assert applications[0]["env_id"] == "test_env_id"


@pytest.mark.asyncio
async def test_get_applications_error(api_manager_client):
    """アプリケーション取得のエラーテスト"""
    async def mock_get(*args, **kwargs):
        mock = Mock()
        mock.raise_for_status = Mock(side_effect=Exception("Test error"))
        mock.__aenter__ = Mock(return_value=mock)
        mock.__aexit__ = Mock(return_value=None)
        return mock

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        with pytest.raises(Exception):
            await api_manager_client.get_applications()
