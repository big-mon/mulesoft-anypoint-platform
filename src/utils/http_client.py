"""Shared aiohttp transport with retry and rate limiting."""

import asyncio
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import aiohttp

from src.utils.proxy import ProxyConfig


RETRYABLE_STATUSES = {429, 503}


class AsyncHTTPClient:
    """Issue JSON requests through a shared aiohttp session."""

    def __init__(self, config, session=None, proxy_config=None):
        self._config = config
        self._proxy_config = proxy_config or ProxyConfig()
        self._session = session
        self._owns_session = session is None
        self._semaphore = asyncio.Semaphore(config.get_http_max_concurrency())
        self._pacing_lock = asyncio.Lock()
        self._next_request_at = 0.0
        timeout_seconds = config.get_http_timeout_seconds()
        self._timeout = aiohttp.ClientTimeout(
            total=timeout_seconds,
            connect=min(timeout_seconds, 10),
            sock_read=timeout_seconds,
        )

    async def __aenter__(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                trust_env=False,
            )
            self._owns_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the owned session."""
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    async def get_json(self, url, *, headers=None, params=None):
        """Issue a GET request and decode the JSON response."""
        return await self.request_json(
            "GET",
            url,
            headers=headers,
            params=params,
        )

    async def post_json(self, url, *, headers=None, data=None):
        """Issue a POST request and decode the JSON response."""
        return await self.request_json(
            "POST",
            url,
            headers=headers,
            data=data,
        )

    async def request_json(self, method, url, *, headers=None, params=None, data=None):
        """Issue a JSON request with retry and pacing."""
        session = self._require_session()
        max_retries = self._config.get_http_max_retries()

        for attempt in range(max_retries + 1):
            async with self._semaphore:
                await self._wait_for_turn()
                request_kwargs = self._proxy_config.get_aiohttp_request_kwargs(url)
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                    **request_kwargs,
                ) as response:
                    if response.status in RETRYABLE_STATUSES and attempt < max_retries:
                        await self._drain_response(response)
                        delay = self._get_retry_delay_seconds(response, attempt)
                    else:
                        response.raise_for_status()
                        return await response.json()

            await asyncio.sleep(delay)

        raise RuntimeError("Unreachable retry loop termination")

    def _require_session(self):
        if self._session is None:
            raise RuntimeError("AsyncHTTPClient session has not been initialized")
        return self._session

    async def _wait_for_turn(self):
        async with self._pacing_lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            wait_seconds = max(0.0, self._next_request_at - now)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
                now = loop.time()
            self._next_request_at = now + (
                self._config.get_http_min_interval_ms() / 1000.0
            )

    async def _drain_response(self, response):
        read_method = getattr(response, "read", None)
        if read_method is not None:
            await read_method()

    def _get_retry_delay_seconds(self, response, attempt):
        retry_after = self._parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is not None:
            return retry_after

        base_delay = self._config.get_http_backoff_base_ms() / 1000.0
        max_delay = self._config.get_http_backoff_max_ms() / 1000.0
        delay = min(max_delay, base_delay * (2**attempt))
        return delay + random.uniform(0, delay / 4 if delay > 0 else 0)

    @staticmethod
    def _parse_retry_after(value):
        if not value:
            return None

        try:
            seconds = float(value)
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                return None

            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, delay)

        return max(0.0, seconds)
