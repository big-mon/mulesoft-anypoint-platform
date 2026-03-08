"""Tests for API Manager export flow."""

from unittest.mock import Mock

import aiohttp
import pytest

from src.api_manager_export import export_api_manager_info


class MockResponse:
    """Minimal async response stub."""

    def __init__(self, payload, status=200):
        self._payload = payload
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(None, None, status=self.status)


def _build_output_mocks(enabled=True):
    file_output = Mock()
    file_output.output_json.return_value = "output/api_manager.json"
    output_config = Mock()
    output_config.get_output_setting.return_value = enabled
    output_config.get_output_filename.return_value = "api_manager.json"
    return file_output, output_config


@pytest.mark.asyncio
async def test_export_api_manager_info_formats_and_outputs(monkeypatch):
    """It fetches, enriches, and outputs API Manager data."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def mock_get(self, url, **kwargs):
        if url.endswith("/apis"):
            return MockResponse(
                {
                    "assets": [
                        {
                            "exchangeAssetName": "orders-api",
                            "apis": [
                                {
                                    "id": "api-1",
                                    "instanceLabel": "Orders",
                                    "activeContractsCount": 2,
                                    "status": "ACTIVE",
                                    "deployment": {"applicationId": "orders-app"},
                                }
                            ],
                        }
                    ]
                }
            )
        if url.endswith("/policies"):
            return MockResponse({"policies": [{"id": "policy-1"}]})
        if url.endswith("/contracts"):
            return MockResponse({"contracts": [{"id": "contract-1"}]})
        if url.endswith("/alerts"):
            return MockResponse([{"id": "alert-1"}])
        if url.endswith("/tiers"):
            return MockResponse({"tiers": [{"id": "tier-1"}]})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
    )

    assert result == [
        {
            "env_name": "Sandbox",
            "org_id": "org-1",
            "env_id": "env-1",
            "apis": [
                {
                    "id": "api-1",
                    "exchangeAssetName": "orders-api",
                    "instanceLabel": "Orders",
                    "activeContractsCount": 2,
                    "status": "ACTIVE",
                    "deployment_applicationId": "orders-app",
                    "policies": [{"id": "policy-1"}],
                    "contracts": [{"id": "contract-1"}],
                    "alerts": [{"id": "alert-1"}],
                    "tiers": [{"id": "tier-1"}],
                }
            ],
        }
    ]
    file_output.output_json.assert_called_once_with(result, "api_manager.json")


@pytest.mark.asyncio
async def test_export_api_manager_info_handles_empty_api_list(monkeypatch):
    """It still outputs structured data when no APIs are returned."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def mock_get(self, url, **kwargs):
        if url.endswith("/apis"):
            return MockResponse({"assets": []})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
    )

    assert result == [
        {"env_name": "Sandbox", "org_id": "org-1", "env_id": "env-1", "apis": []}
    ]
    file_output.output_json.assert_called_once_with(result, "api_manager.json")


@pytest.mark.asyncio
async def test_export_api_manager_info_handles_empty_detail_payloads(monkeypatch):
    """It fills missing detail collections with empty lists."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks(enabled=False)

    def mock_get(self, url, **kwargs):
        if url.endswith("/apis"):
            return MockResponse(
                {
                    "assets": [
                        {
                            "exchangeAssetName": "orders-api",
                            "apis": [
                                {
                                    "id": "api-1",
                                    "instanceLabel": "Orders",
                                    "activeContractsCount": 0,
                                    "status": "ACTIVE",
                                    "deployment": None,
                                }
                            ],
                        }
                    ]
                }
            )
        if url.endswith("/policies"):
            return MockResponse({})
        if url.endswith("/contracts"):
            return MockResponse({})
        if url.endswith("/alerts"):
            return MockResponse([])
        if url.endswith("/tiers"):
            return MockResponse({})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
    )

    assert result[0]["apis"][0]["deployment_applicationId"] is None
    assert result[0]["apis"][0]["policies"] == []
    assert result[0]["apis"][0]["contracts"] == []
    assert result[0]["apis"][0]["alerts"] == []
    assert result[0]["apis"][0]["tiers"] == []
    file_output.output_json.assert_not_called()
