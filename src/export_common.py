"""Shared helpers for export flows."""

from contextlib import asynccontextmanager

from src.utils.config import Config
from src.utils.http_client import AsyncHTTPClient


def build_auth_headers(access_token):
    """Return the standard bearer authorization header."""
    return {"Authorization": f"Bearer {access_token}"}


@asynccontextmanager
async def export_runtime(access_token, http_client=None, config=None):
    """Yield the resolved config, headers, base URL, and HTTP client."""
    resolved_config = config or Config()
    headers = build_auth_headers(access_token)
    base_url = resolved_config.get_base_url()

    if http_client is None:
        async with AsyncHTTPClient(resolved_config) as owned_http_client:
            yield resolved_config, headers, base_url, owned_http_client
        return

    yield resolved_config, headers, base_url, http_client


def write_export_output(output_key, label, payload, file_output, output_config):
    """Write export payload when the output key is enabled."""
    if file_output and output_config.get_output_setting(output_key):
        filename = output_config.get_output_filename(output_key)
        file_path = file_output.output_json(payload, filename)
        print(f"{label} output saved to: {file_path}")
