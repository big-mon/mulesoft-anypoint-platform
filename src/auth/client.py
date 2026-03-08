#!/usr/bin/env python3
"""Anypoint authentication client."""

import asyncio

from src.utils.config import Config


class AuthClient:
    """Fetch OAuth access tokens from Access Management API."""

    def __init__(self, http_client, config=None):
        self._http_client = http_client
        self._config = config or Config()
        self.__access_token = None
        self._token_lock = asyncio.Lock()

    async def get_access_token(self):
        """Return a cached access token or fetch a new one."""
        if self.__access_token:
            return self.__access_token

        async with self._token_lock:
            if self.__access_token:
                return self.__access_token

            self.__access_token = await self._fetch_access_token()
            return self.__access_token

    async def refresh_token(self):
        """Force a new access token fetch."""
        async with self._token_lock:
            self.__access_token = await self._fetch_access_token()
            return self.__access_token

    async def _fetch_access_token(self):
        auth_url = f"{self._config.get_base_url()}/accounts/api/v2/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._config.get_client_id(),
            "client_secret": self._config.get_client_secret(),
        }
        response = await self._http_client.post_json(auth_url, data=payload)
        return response["access_token"]
