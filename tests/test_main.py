"""Tests for the main entrypoint."""

import pytest

import src.main as main_module


class DummyConfig:
    """Minimal config stub for main tests."""

    def __init__(self):
        self.is_valid = True


class DummyOutputConfig:
    """Minimal output config stub."""


class DummyFileOutput:
    """Minimal file output stub."""

    def prepare_output_folder(self):
        return None


class DummyHTTPClientContext:
    """Minimal async context manager for AsyncHTTPClient."""

    def __init__(self, config):
        self.config = config

    async def __aenter__(self):
        return object()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class DummyAuthClient:
    """Minimal auth client stub."""

    def __init__(self, http_client, config=None):
        self.http_client = http_client
        self.config = config

    async def get_access_token(self):
        return "token"


class DummyAccountsAPI:
    """Minimal accounts API stub."""

    def __init__(self, token, http_client, config=None):
        self.token = token
        self.http_client = http_client
        self.config = config

    async def get_organization_environments(self):
        return {
            "data": [
                {
                    "name": "Sandbox",
                    "organizationId": "org-1",
                    "id": "env-1",
                }
            ]
        }


@pytest.mark.asyncio
async def test_main_returns_zero_on_success(monkeypatch):
    """It returns zero when all startup and export steps succeed."""
    monkeypatch.setattr(main_module, "Config", DummyConfig)
    monkeypatch.setattr(main_module, "OutputConfig", DummyOutputConfig)
    monkeypatch.setattr(main_module, "FileOutput", DummyFileOutput)
    monkeypatch.setattr(main_module, "AsyncHTTPClient", DummyHTTPClientContext)
    monkeypatch.setattr(main_module, "AuthClient", DummyAuthClient)
    monkeypatch.setattr(main_module, "AccountsAPI", DummyAccountsAPI)

    async def export_api_manager_info(*args, **kwargs):
        return []

    async def export_cloudhub_info(*args, **kwargs):
        return []

    monkeypatch.setattr(main_module, "export_api_manager_info", export_api_manager_info)
    monkeypatch.setattr(main_module, "export_cloudhub_info", export_cloudhub_info)

    assert await main_module.main() == 0


@pytest.mark.asyncio
async def test_main_returns_one_when_export_fails(monkeypatch):
    """It returns one when export execution raises an error."""
    monkeypatch.setattr(main_module, "Config", DummyConfig)
    monkeypatch.setattr(main_module, "OutputConfig", DummyOutputConfig)
    monkeypatch.setattr(main_module, "FileOutput", DummyFileOutput)
    monkeypatch.setattr(main_module, "AsyncHTTPClient", DummyHTTPClientContext)
    monkeypatch.setattr(main_module, "AuthClient", DummyAuthClient)
    monkeypatch.setattr(main_module, "AccountsAPI", DummyAccountsAPI)

    async def export_api_manager_info(*args, **kwargs):
        raise RuntimeError("boom")

    async def export_cloudhub_info(*args, **kwargs):
        return []

    monkeypatch.setattr(main_module, "export_api_manager_info", export_api_manager_info)
    monkeypatch.setattr(main_module, "export_cloudhub_info", export_cloudhub_info)

    assert await main_module.main() == 1
