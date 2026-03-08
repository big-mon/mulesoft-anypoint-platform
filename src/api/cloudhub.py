"""CloudHub API client."""

import os
import asyncio

from aiohttp import ClientSession
from dotenv import load_dotenv

try:
    from utils.proxy import ProxyConfig
except ImportError:
    from src.utils.proxy import ProxyConfig


class CloudHubClient:
    """Client for the CloudHub API."""

    def __init__(self, token, environments):
        load_dotenv()
        self._base_url = os.getenv("ANYPOINT_BASE_URL")
        self._token = token
        self._environments = environments
        self._proxy_config = ProxyConfig()

    async def get_applications(self):
        """Fetch CloudHub applications for all environments."""

        async def fetch_env_applications(session: ClientSession, env: dict) -> dict:
            url = f"{self._base_url}/cloudhub/api/v2/applications"
            headers = {
                "X-ANYPNT-ENV-ID": env["env_id"],
                "Authorization": f"Bearer {self._token}",
            }
            request_kwargs = self._proxy_config.get_aiohttp_request_kwargs(url)

            async with session.get(url, headers=headers, **request_kwargs) as response:
                response.raise_for_status()
                return {
                    "env_name": env["name"],
                    "org_id": env["org_id"],
                    "env_id": env["env_id"],
                    "apis": await response.json(),
                }

        async with ClientSession() as session:
            tasks = [
                fetch_env_applications(session, env)
                for env in self._environments
            ]
            return await asyncio.gather(*tasks)
