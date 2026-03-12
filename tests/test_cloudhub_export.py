"""Tests for Runtime Manager export flow."""

import aiohttp
import pytest

from src.cloudhub_export import export_cloudhub_info
from tests.conftest import FakeHTTPClient, build_http_error, build_output_mocks


@pytest.mark.asyncio
async def test_export_cloudhub_info_formats_and_outputs(monkeypatch):
    """It fetches each environment and outputs the formatted payload."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="cloudhub.json")

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
    file_output, output_config = build_output_mocks(
        enabled=False,
        filename="cloudhub.json",
    )

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
    file_output, output_config = build_output_mocks(filename="cloudhub.json")

    with pytest.raises(aiohttp.ClientResponseError):
        await export_cloudhub_info(
            "token",
            [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
            file_output,
            output_config,
            http_client=FakeHTTPClient(lambda url, **kwargs: build_http_error(503)),
        )

    file_output.output_json.assert_not_called()


@pytest.mark.asyncio
async def test_export_cloudhub_info_does_not_create_owned_client_when_injected(
    monkeypatch,
):
    """It uses the injected HTTP client without constructing another transport."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="cloudhub.json")

    class UnexpectedHTTPClient:
        def __init__(self, *args, **kwargs):
            raise AssertionError("owned client should not be created")

    monkeypatch.setattr("src.export_common.AsyncHTTPClient", UnexpectedHTTPClient)

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


@pytest.mark.asyncio
async def test_export_cloudhub_info_masks_proxy_credentials_in_error_output(
    monkeypatch, capsys
):
    """It redacts proxy userinfo before logging export failures."""
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    file_output, output_config = build_output_mocks(filename="cloudhub.json")

    with pytest.raises(RuntimeError):
        await export_cloudhub_info(
            "token",
            [{"name": "Sandbox", "org_id": "org-1", "env_id": "env-1"}],
            file_output,
            output_config,
            http_client=FakeHTTPClient(
                lambda url, **kwargs: RuntimeError(
                    "proxy http://user:pass@proxy.local:8080 refused "
                    "https://example.com/cloudhub/api/v2/applications"
                )
            ),
        )

    captured = capsys.readouterr()
    assert "http://***@proxy.local:8080" in captured.out
    assert "https://example.com/cloudhub/api/v2/applications" in captured.out
    assert "user:pass" not in captured.out
