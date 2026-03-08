"""Tests for Runtime Manager export flow."""

from unittest.mock import Mock

import aiohttp
import pytest

from src.cloudhub_export import export_cloudhub_info


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
    file_output.output_json.return_value = "output/cloudhub.json"
    output_config = Mock()
    output_config.get_output_setting.return_value = enabled
    output_config.get_output_filename.return_value = "cloudhub.json"
    return file_output, output_config


@pytest.mark.asyncio
async def test_export_cloudhub_info_formats_and_outputs(monkeypatch):
    """It fetches each environment and outputs the formatted payload."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def mock_get(self, url, **kwargs):
        env_id = kwargs["headers"]["X-ANYPNT-ENV-ID"]
        payload = [{"id": f"app-{env_id}", "status": "STARTED"}]
        return MockResponse(payload)

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    environments = [
        {"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"},
        {"name": "Prod", "org_id": "org-1", "env_id": "env-2"},
    ]
    result = await export_cloudhub_info(
        "token",
        environments,
        file_output,
        output_config,
    )

    assert result == [
        {
            "env_name": "Sandbox",
            "org_id": "org-1",
            "env_id": "env-1",
            "apis": [{"id": "app-env-1", "status": "STARTED"}],
        },
        {
            "env_name": "Prod",
            "org_id": "org-1",
            "env_id": "env-2",
            "apis": [{"id": "app-env-2", "status": "STARTED"}],
        },
    ]
    file_output.output_json.assert_called_once_with(result, "cloudhub.json")


@pytest.mark.asyncio
async def test_export_cloudhub_info_skips_output_when_disabled(monkeypatch):
    """It returns data without writing files when output is disabled."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks(enabled=False)

    def mock_get(self, url, **kwargs):
        return MockResponse([{"id": "app-1", "status": "STARTED"}])

    monkeypatch.setattr("aiohttp.ClientSession.get", mock_get)

    result = await export_cloudhub_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
    )

    assert result[0]["apis"] == [{"id": "app-1", "status": "STARTED"}]
    file_output.output_json.assert_not_called()
