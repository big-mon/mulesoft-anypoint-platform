#!/usr/bin/env python3
"""API Manager API."""

import os
import asyncio

import aiohttp
import requests
from dotenv import load_dotenv

try:
    from utils.proxy import ProxyConfig
except ImportError:
    from src.utils.proxy import ProxyConfig


class APIManagerClient:
    """Client for the Anypoint API Manager API."""

    def __init__(self, token, environments):
        load_dotenv()
        self._base_url = os.getenv("ANYPOINT_BASE_URL")
        self._environments = environments
        self.__proxy_config = ProxyConfig()
        self.__session = requests.Session()
        self.__session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        self.__session.proxies.update(self.__proxy_config.get_requests_proxies())

    async def get_applications(self):
        """Fetch API applications for all environments."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self.get_applications_async(session, env))
                for env in self._environments
            ]
            return await asyncio.gather(*tasks)

    async def get_applications_async(self, session, env):
        """Fetch API applications for a single environment."""
        url = (
            f"{self._base_url}/apimanager/api/v1/organizations/"
            f"{env['org_id']}/environments/{env['env_id']}/apis"
        )
        params = {"sort": "name"}
        request_kwargs = self.__proxy_config.get_aiohttp_request_kwargs(url)

        async with session.get(
            url,
            headers=self.__session.headers,
            params=params,
            **request_kwargs,
        ) as response:
            response.raise_for_status()
            return {
                "env_name": env["name"],
                "org_id": env["org_id"],
                "env_id": env["env_id"],
                "apis": await response.json(),
            }

    def compact_applications(self, applications):
        """Flatten the API Manager applications payload."""
        compact_applications = []

        for app in applications:
            compact_app = {
                "env_name": app["env_name"],
                "org_id": app["org_id"],
                "env_id": app["env_id"],
                "apis": [],
            }

            if app["apis"]["assets"]:
                for asset in app["apis"]["assets"]:
                    for api in asset["apis"]:
                        compact_app["apis"].append({
                            "id": api["id"],
                            "exchangeAssetName": asset["exchangeAssetName"],
                            "instanceLabel": api["instanceLabel"],
                            "activeContractsCount": api["activeContractsCount"],
                            "status": api["status"],
                            "deployment_applicationId": (
                                api["deployment"]["applicationId"]
                                if api["deployment"]
                                else None
                            ),
                        })

            compact_applications.append(compact_app)

        return compact_applications

    async def get_policies_async(self, session, org_id, env_id, api_id):
        """Fetch policies for an API."""
        url = (
            f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/"
            f"environments/{env_id}/apis/{api_id}/policies"
        )
        return await self._get_json(session, url)

    async def get_contracts_async(self, session, org_id, env_id, api_id):
        """Fetch contracts for an API."""
        url = (
            f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/"
            f"environments/{env_id}/apis/{api_id}/contracts"
        )
        return await self._get_json(session, url)

    async def get_alerts_async(self, session, org_id, env_id, api_id):
        """Fetch alerts for an API."""
        url = (
            f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/"
            f"environments/{env_id}/apis/{api_id}/alerts"
        )
        return await self._get_json(session, url)

    async def get_tiers_async(self, session, org_id, env_id, api_id):
        """Fetch tiers for an API."""
        url = (
            f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/"
            f"environments/{env_id}/apis/{api_id}/tiers"
        )
        return await self._get_json(session, url)

    async def _get_json(self, session, url):
        """Fetch a JSON response from the API Manager API."""
        request_kwargs = self.__proxy_config.get_aiohttp_request_kwargs(url)

        async with session.get(
            url,
            headers=self.__session.headers,
            **request_kwargs,
        ) as response:
            response.raise_for_status()
            return await response.json()
