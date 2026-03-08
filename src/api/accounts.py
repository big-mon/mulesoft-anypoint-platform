#!/usr/bin/env python3
"""Accounts API client."""

try:
    from utils.config import Config
except ImportError:
    from src.utils.config import Config


class AccountsAPI:
    """Fetch organization metadata from the Accounts API."""

    def __init__(self, token, http_client, config=None):
        self._http_client = http_client
        self._config = config or Config()
        self._headers = {"Authorization": f"Bearer {token}"}

    async def get_organization_environments(self):
        """Return the environments configured for the organization."""
        url = (
            f"{self._config.get_base_url()}/accounts/api/organizations/"
            f"{self._config.get_organization_id()}/environments"
        )
        params = {
            "extended": "false",
            "resolveTheme": "false",
        }
        return await self._http_client.get_json(
            url,
            headers=self._headers,
            params=params,
        )
