"""Tests for Runtime Manager export flow."""

from unittest.mock import Mock

import aiohttp
import pytest

from src.cloudhub_export import export_cloudhub_info


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
    file_output.output_json.return_value = "output/cloudhub.json"
    output_config = Mock()
    output_config.get_output_setting.return_value = enabled
    output_config.get_output_filename.return_value = "cloudhub.json"
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
async def test_export_cloudhub_info_formats_and_outputs(monkeypatch):
    """It fetches each environment and outputs the formatted payload."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    def responder(url, **kwargs):
        assert kwargs["headers"]["Authorization"] == "Bearer token"
        env_id = kwargs["headers"]["X-ANYPNT-ENV-ID"]
        return [{"id": f"app-{env_id}", "status": "STARTED"}]

    environments = [
        {"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"},
        {"name": "Prod", "org_id": "org-1", "env_id": "env-2"},
    ]
    result = await export_cloudhub_info(
        "token",
        environments,
        file_output,
        output_config,
        http_client=FakeHTTPClient(responder),
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

    result = await export_cloudhub_info(
        "token",
        [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
        file_output,
        output_config,
        http_client=FakeHTTPClient(
            lambda url, **kwargs: [{"id": "app-1", "status": "STARTED"}]
        ),
    )

    assert result[0]["apis"] == [{"id": "app-1", "status": "STARTED"}]
    file_output.output_json.assert_not_called()


@pytest.mark.asyncio
async def test_export_cloudhub_info_raises_on_http_error(monkeypatch):
    """It preserves fail-fast behavior when Runtime Manager calls fail."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = _build_output_mocks()

    with pytest.raises(aiohttp.ClientResponseError):
        await export_cloudhub_info(
            "token",
            [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
            file_output,
            output_config,
            http_client=FakeHTTPClient(lambda url, **kwargs: _build_http_error(503)),
        )

    file_output.output_json.assert_not_called()
