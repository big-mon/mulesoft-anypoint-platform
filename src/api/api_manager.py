#!/usr/bin/env python3
"""API Manager API"""

import os
import asyncio
import aiohttp
import requests
from dotenv import load_dotenv


class APIManagerClient:
    """API Manager APIクライアント"""
    def __init__(self, token, environments):
        load_dotenv()
        self._base_url = os.getenv('ANYPOINT_BASE_URL')
        self.__session = requests.Session()
        self.__session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        self._environments = environments

    async def get_applications(self):
        """アプリケーションの取得"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for env in self._environments:
                tasks.append(asyncio.create_task(
                    self.get_applications_async(session, env)
                ))
            applications = await asyncio.gather(*tasks)
            return applications

    async def get_applications_async(self, session, env):
        """アプリケーションの非同期取得"""
        url = f"{self._base_url}/apimanager/api/v1/organizations/{env['org_id']}/environments/{env['env_id']}/apis"
        params = {
            'sort': 'name'
        }
        async with session.get(url, headers=self.__session.headers, params=params) as response:
            response.raise_for_status()
            data = {
                'env_name': env['name'],
                'org_id': env['org_id'],
                'env_id': env['env_id'],
                'apis': await response.json()
            }
            return data

    def compact_applications(self, applications):
        """アプリケーション情報を解析用にコンパクト化"""
        compact_applications = []

        # applications配列をループ
        for app in applications:
            compact_app = {
                "env_name": app["env_name"],
                "org_id": app["org_id"],
                "env_id": app["env_id"],
                "apis": []
            }

            # apis.assets内のapisを格納
            if app["apis"]["assets"]:
                compact_app["apis"] = []
                for asset in app["apis"]["assets"]:
                    for api in asset["apis"]:
                        compact_app["apis"].append({
                            "id": api["id"],
                            "exchangeAssetName": asset["exchangeAssetName"],
                            "instanceLabel": api["instanceLabel"],
                            "activeContractsCount": api["activeContractsCount"],
                            "status": api["status"],
                            "deployment_applicationId": api["deployment"]["applicationId"] if api["deployment"] else None
                        })

            compact_applications.append(compact_app)

        return compact_applications

    async def get_policies_async(self, session, org_id, env_id, api_id):
        """ポリシーの非同期取得"""
        url = f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_contracts_async(self, session, org_id, env_id, api_id):
        """コントラクトの非同期取得"""
        url = f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_alerts_async(self, session, org_id, env_id, api_id):
        """アラートの非同期取得"""
        url = f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/alerts"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_tiers_async(self, session, org_id, env_id, api_id):
        """ティアの非同期取得"""
        url = f"{self._base_url}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()