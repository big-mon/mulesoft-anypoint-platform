"""Proxy configuration helpers for outbound HTTP requests."""

import os
from urllib.parse import urlparse

from dotenv import load_dotenv


class ProxyConfig:
    """Resolve optional proxy settings from environment variables."""

    def __init__(self):
        load_dotenv()
        self._default_proxy = os.getenv("ANYPOINT_PROXY_URL")
        self._http_proxy = os.getenv("ANYPOINT_HTTP_PROXY")
        self._https_proxy = os.getenv("ANYPOINT_HTTPS_PROXY")

    def get_requests_proxies(self):
        """Build a proxies mapping for requests.Session."""
        proxies = {}

        if self._default_proxy:
            proxies["http"] = self._default_proxy
            proxies["https"] = self._default_proxy

        if self._http_proxy:
            proxies["http"] = self._http_proxy

        if self._https_proxy:
            proxies["https"] = self._https_proxy

        return proxies

    def get_proxy_for_url(self, url):
        """Return the proxy URL that matches the request scheme."""
        scheme = urlparse(url).scheme.lower()

        if scheme == "http":
            return self._http_proxy or self._default_proxy

        if scheme == "https":
            return self._https_proxy or self._default_proxy

        return self._default_proxy

    def get_aiohttp_request_kwargs(self, url):
        """Build request kwargs for aiohttp based on the target URL."""
        proxy = self.get_proxy_for_url(url)
        return {"proxy": proxy} if proxy else {"proxy": None}
