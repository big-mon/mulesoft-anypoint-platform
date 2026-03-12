"""Tests for API Manager export flow."""

import aiohttp
import pytest

from src.api_manager_export import export_api_manager_info
from tests.conftest import FakeHTTPClient, build_http_error, build_output_mocks


@pytest.mark.asyncio
async def test_export_api_manager_info_formats_and_outputs(monkeypatch):
    """It fetches, enriches, and outputs API Manager data."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="api_manager.json")
    expected_base_url = (
        "https://example.com/apimanager/api/v1/organizations/org-1/"
        "environments/env-1/apis/api-1"
    )

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
        if url == f"{expected_base_url}/policies":
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert kwargs["params"] is None
            return {"policies": [{"id": "policy-1"}]}
        if url == f"{expected_base_url}/contracts":
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert kwargs["params"] is None
            return {"contracts": [{"id": "contract-1"}]}
        if url == f"{expected_base_url}/alerts":
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert kwargs["params"] is None
            return [{"id": "alert-1"}]
        if url == f"{expected_base_url}/tiers":
            assert kwargs["headers"] == {"Authorization": "Bearer token"}
            assert kwargs["params"] is None
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
    file_output, output_config = build_output_mocks(filename="api_manager.json")

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
    file_output, output_config = build_output_mocks(filename="api_manager.json")

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
    file_output, output_config = build_output_mocks(filename="api_manager.json")

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
    file_output, output_config = build_output_mocks(
        enabled=False,
        filename="api_manager.json",
    )

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
async def test_export_api_manager_info_raises_on_http_error(monkeypatch):
    """It preserves API failures for callers and does not write output."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="api_manager.json")

    with pytest.raises(aiohttp.ClientResponseError):
        await export_api_manager_info(
            "token",
            [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
            file_output,
            output_config,
            http_client=FakeHTTPClient(lambda url, **kwargs: build_http_error(503)),
        )

    file_output.output_json.assert_not_called()


@pytest.mark.asyncio
async def test_export_api_manager_info_does_not_create_owned_client_when_injected(
    monkeypatch,
):
    """It uses the injected HTTP client without constructing another transport."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="api_manager.json")

    class UnexpectedHTTPClient:
        def __init__(self, *args, **kwargs):
            raise AssertionError("owned client should not be created")

    monkeypatch.setattr("src.export_common.AsyncHTTPClient", UnexpectedHTTPClient)

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


@pytest.mark.asyncio
async def test_export_api_manager_info_redacts_proxy_credentials_in_error_output(
    monkeypatch, capsys
):
    """It redacts proxy credentials before printing export failures."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="api_manager.json")

    with pytest.raises(RuntimeError):
        await export_api_manager_info(
            "token",
            [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
            file_output,
            output_config,
            http_client=FakeHTTPClient(
                lambda url, **kwargs: RuntimeError(
                    "proxy failed: http://user:pass@proxy.local:8080"
                )
            ),
        )

    captured = capsys.readouterr()
    assert "http://***:***@proxy.local:8080" in captured.out
    assert "http://user:pass@proxy.local:8080" not in captured.out
