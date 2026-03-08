"""Tests for API Manager export flow."""

from unittest.mock import Mock

import aiohttp
import pytest

from src.api_manager_export import export_api_manager_info


class FakeHTTPClient:
    """Minimal async transport stub."""

    def __init__(self, responder):
        self._responder = responder
        self.calls = []

    async def get_json(self, url, *, headers=None, params=None):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "params": params,
            }
        )
        result = self._responder(url, headers=headers, params=params)
        if isinstance(result, Exception):
            raise result
        return result


def _build_output_mocks(enabled=True):
    file_output = Mock()
    file_output.output_json.return_value = "output/api_manager.json"
    output_config = Mock()
    output_config.get_output_setting.return_value = enabled
    output_config.get_output_filename.return_value = "api_manager.json"
    return file_output, output_config


def _build_http_error(status):
    request_info = Mock()
    request_info.real_url = "https://example.com"
    return aiohttp.ClientResponseError(
        request_info=request_info,
        history=(),
        status=status,
    )


@pytest.mark.asyncio
async def test_export_api_manager_info_formats_and_outputs(monkeypatch):
    """It fetches, enriches, and outputs API Manager data."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def responder(url, **kwargs):
        if url.endswith("/apis"):
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert kwargs["params"] == {"sort": "name"}
            return {
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
        if url.endswith("/policies"):
            return {"policies": [{"id": "policy-1"}]}
        if url.endswith("/contracts"):
            return {"contracts": [{"id": "contract-1"}]}
        if url.endswith("/alerts"):
            return [{"id": "alert-1"}]
        if url.endswith("/tiers"):
            return {"tiers": [{"id": "tier-1"}]}
        raise AssertionError(f"Unexpected URL: {url}")

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(responder),
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
async def test_export_api_manager_info_handles_missing_api_fields(monkeypatch):
    """It defaults missing API fields instead of raising KeyError."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def responder(url, **kwargs):
        if url.endswith("/apis"):
            return {
                "assets": [
                    {
                        "apis": [
                            {
                                "deployment": None,
                            }
                        ],
                    }
                ]
            }
        raise AssertionError(f"Unexpected URL: {url}")

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(responder),
    )

    assert result == [
        {
            "env_name": "Sandbox",
            "org_id": "org-1",
            "env_id": "env-1",
            "apis": [
                {
                    "id": None,
                    "exchangeAssetName": "",
                    "instanceLabel": "",
                    "activeContractsCount": 0,
                    "status": None,
                    "deployment_applicationId": None,
                    "policies": [],
                    "contracts": [],
                    "alerts": [],
                    "tiers": [],
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

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(lambda url, **kwargs: {"assets": []}),
    )

    assert result == [
        {"env_name": "Sandbox", "org_id": "org-1", "env_id": "env-1", "apis": []}
    ]
    file_output.output_json.assert_called_once_with(result, "api_manager.json")


@pytest.mark.asyncio
async def test_export_api_manager_info_handles_empty_detail_payloads(monkeypatch):
    """It fills missing detail collections with empty lists."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def responder(url, **kwargs):
        if url.endswith("/apis"):
            return {
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
        if url.endswith("/policies"):
            return {}
        if url.endswith("/contracts"):
            return {}
        if url.endswith("/alerts"):
            return []
        if url.endswith("/tiers"):
            return {}
        raise AssertionError(f"Unexpected URL: {url}")

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(responder),
    )

    assert result[0]["apis"][0]["deployment_applicationId"] is None
    assert result[0]["apis"][0]["policies"] == []
    assert result[0]["apis"][0]["contracts"] == []
    assert result[0]["apis"][0]["alerts"] == []
    assert result[0]["apis"][0]["tiers"] == []
    file_output.output_json.assert_called_once_with(result, "api_manager.json")


@pytest.mark.asyncio
async def test_export_api_manager_info_skips_output_when_disabled(monkeypatch):
    """It returns data without writing files when output is disabled."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks(enabled=False)

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(lambda url, **kwargs: {"assets": []}),
    )

    assert result == [
        {"env_name": "Sandbox", "org_id": "org-1", "env_id": "env-1", "apis": []}
    ]
    file_output.output_json.assert_not_called()


@pytest.mark.asyncio
async def test_export_api_manager_info_returns_none_on_http_error(monkeypatch):
    """It returns None and does not write output when API Manager calls fail."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    result = await export_api_manager_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(lambda url, **kwargs: _build_http_error(503)),
    )

    assert result is None
    file_output.output_json.assert_not_called()
