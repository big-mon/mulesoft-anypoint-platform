"""Tests for the shared async HTTP client."""

import asyncio
from unittest.mock import Mock

import aiohttp
import pytest

from src.utils.config import Config
from src.utils.http_client import AsyncHTTPClient


class MockResponse:
    """Async response stub used by MockSession."""

    def __init__(self, payload, status=200, headers=None, tracker=None, wait_event=None):
        self._payload = payload
        self.status = status
        self.headers = headers or {}
        self._tracker = tracker
        self._wait_event = wait_event

    async def __aenter__(self):
        if self._tracker is not None:
            self._tracker["current"] += 1
            self._tracker["max"] = max(self._tracker["max"], self._tracker["current"])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._tracker is not None:
            self._tracker["current"] -= 1
        return False

    async def json(self):
        if self._wait_event is not None:
            await self._wait_event.wait()
        return self._payload

    async def read(self):
        return b""

    def raise_for_status(self):
        if self.status >= 400:
            request_info = Mock()
            request_info.real_url = "https://example.com"
            raise aiohttp.ClientResponseError(
                request_info=request_info,
                history=(),
                status=self.status,
            )


class MockSession:
    """Minimal aiohttp-like session stub."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.closed = False

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return self._responses.pop(0)

    async def close(self):
        self.closed = True


def _build_config(monkeypatch, **env):
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_BASE_URL", "https://example.com")
    defaults = {
        "ANYPOINT_HTTP_MAX_CONCURRENCY": "5",
        "ANYPOINT_HTTP_MIN_INTERVAL_MS": "0",
        "ANYPOINT_HTTP_MAX_RETRIES": "5",
        "ANYPOINT_HTTP_BACKOFF_BASE_MS": "500",
        "ANYPOINT_HTTP_BACKOFF_MAX_MS": "10000",
        "ANYPOINT_HTTP_TIMEOUT_SECONDS": "30",
    }
    defaults.update(env)
    for key, value in defaults.items():
        monkeypatch.setenv(key, value)
    return Config()


@pytest.mark.asyncio
async def test_http_client_applies_configured_proxy(monkeypatch):
    """It passes proxy kwargs to aiohttp based on the request URL."""
    monkeypatch.setenv("ANYPOINT_HTTPS_PROXY", "http://proxy.local:8443")
    config = _build_config(monkeypatch)
    session = MockSession([MockResponse({"ok": True})])

    client = AsyncHTTPClient(config, session=session)
    result = await client.get_json("https://example.com/resource")

    assert result == {"ok": True}
    assert session.calls[0]["kwargs"]["proxy"] == "http://proxy.local:8443"


@pytest.mark.asyncio
async def test_http_client_retries_retry_after(monkeypatch):
    """It honors Retry-After headers before retrying."""
    config = _build_config(
        monkeypatch,
        ANYPOINT_HTTP_MIN_INTERVAL_MS="0",
        ANYPOINT_HTTP_MAX_RETRIES="2",
    )
    session = MockSession(
        [
            MockResponse({"error": "rate limited"}, status=429, headers={"Retry-After": "3"}),
            MockResponse({"ok": True}),
        ]
    )
    sleeps = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr("src.utils.http_client.asyncio.sleep", fake_sleep)

    client = AsyncHTTPClient(config, session=session)
    result = await client.get_json("https://example.com/resource")

    assert result == {"ok": True}
    assert sleeps == [3.0]


@pytest.mark.asyncio
async def test_http_client_retries_with_backoff_when_retry_after_missing(monkeypatch):
    """It falls back to exponential backoff when Retry-After is absent."""
    config = _build_config(
        monkeypatch,
        ANYPOINT_HTTP_MIN_INTERVAL_MS="0",
        ANYPOINT_HTTP_MAX_RETRIES="2",
        ANYPOINT_HTTP_BACKOFF_BASE_MS="500",
        ANYPOINT_HTTP_BACKOFF_MAX_MS="10000",
    )
    session = MockSession(
        [
            MockResponse({"error": "busy"}, status=503),
            MockResponse({"ok": True}),
        ]
    )
    sleeps = []

    async def fake_sleep(delay):
        sleeps.append(delay)

    monkeypatch.setattr("src.utils.http_client.asyncio.sleep", fake_sleep)
    monkeypatch.setattr("src.utils.http_client.random.uniform", lambda start, end: 0)

    client = AsyncHTTPClient(config, session=session)
    result = await client.get_json("https://example.com/resource")

    assert result == {"ok": True}
    assert sleeps == [0.5]


@pytest.mark.asyncio
async def test_http_client_does_not_retry_non_retryable_status(monkeypatch):
    """It immediately raises for non-retryable client errors."""
    config = _build_config(monkeypatch, ANYPOINT_HTTP_MAX_RETRIES="3")
    session = MockSession([MockResponse({"error": "bad request"}, status=400)])

    client = AsyncHTTPClient(config, session=session)

    with pytest.raises(aiohttp.ClientResponseError) as exc_info:
        await client.get_json("https://example.com/resource")

    assert exc_info.value.status == 400
    assert len(session.calls) == 1


@pytest.mark.asyncio
async def test_http_client_limits_max_concurrency(monkeypatch):
    """It keeps in-flight requests under the configured semaphore limit."""
    config = _build_config(
        monkeypatch,
        ANYPOINT_HTTP_MAX_CONCURRENCY="2",
        ANYPOINT_HTTP_MIN_INTERVAL_MS="0",
    )
    tracker = {"current": 0, "max": 0}
    release_event = asyncio.Event()
    session = MockSession(
        [
            MockResponse({"id": 1}, tracker=tracker, wait_event=release_event),
            MockResponse({"id": 2}, tracker=tracker, wait_event=release_event),
            MockResponse({"id": 3}, tracker=tracker, wait_event=release_event),
        ]
    )
    client = AsyncHTTPClient(config, session=session)

    tasks = [
        asyncio.create_task(client.get_json(f"https://example.com/{index}"))
        for index in range(3)
    ]
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert tracker["max"] == 2
    assert len(session.calls) == 2

    release_event.set()
    results = await asyncio.gather(*tasks)

    assert results == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert len(session.calls) == 3
