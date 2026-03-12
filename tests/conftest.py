"""Shared test helpers."""

import asyncio
from unittest.mock import Mock

import aiohttp


class FakeHTTPClient:
    """Minimal async transport stub."""

    def __init__(self, responder=None, *, get_responder=None, post_responder=None):
        self._default_responder = responder
        self._get_responder = get_responder
        self._post_responder = post_responder
        self.calls = []

    async def get_json(self, url, *, headers=None, params=None):
        return await self._handle_call(
            "GET",
            url,
            headers=headers,
            params=params,
        )

    async def post_json(self, url, *, headers=None, data=None):
        return await self._handle_call(
            "POST",
            url,
            headers=headers,
            data=data,
        )

    async def _handle_call(self, method, url, *, headers=None, params=None, data=None):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
                "data": data,
            }
        )
        responder = self._default_responder
        if method == "GET" and self._get_responder is not None:
            responder = self._get_responder
        if method == "POST" and self._post_responder is not None:
            responder = self._post_responder
        if responder is None:
            raise AssertionError(f"No responder configured for {method} {url}")
        result = responder(url, headers=headers, params=params, data=data)
        if asyncio.iscoroutine(result):
            result = await result
        if isinstance(result, Exception):
            raise result
        return result


def build_output_mocks(*, enabled=True, filename):
    """Return mocked file output and output config objects."""
    file_output = Mock()
    file_output.output_json.return_value = f"output/{filename}"
    output_config = Mock()
    output_config.get_output_setting.return_value = enabled
    output_config.get_output_filename.return_value = filename
    return file_output, output_config


def build_http_error(status):
    """Return an aiohttp response error with the given status."""
    request_info = Mock()
    request_info.real_url = "https://example.com"
    return aiohttp.ClientResponseError(
        request_info=request_info,
        history=(),
        status=status,
    )
