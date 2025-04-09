import os
from dotenv import load_dotenv
import requests
import aiohttp


class RuntimeManagerClient:
    """Runtime Manager APIクライアント"""
    def __init__(self, token, environments):
        load_dotenv()
        self._base_url = os.getenv('ANYPOINT_BASE_URL')
        self.__session = requests.Session()
        self.__session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        self._environments = environments

    def get_applications(self):
        """アプリケーションの取得"""
        results = []
        for env in self._environments:
            url = f"{self._base_url}/hybrid/api/v2/organizations/{env['org_id']}/environments/{env['env_id']}/applications"
            response = self.__session.get(url)
            response.raise_for_status()
            data = response.json()
            
            for app in data:
                results.append({
                    "env_name": env["env_name"],
                    "org_id": env["org_id"],
                    "env_id": env["env_id"],
                    **app
                })
        
        return results

    async def get_status_async(self, session, org_id, env_id, app_id):
        """アプリケーションステータスの非同期取得"""
        url = f"{self._base_url}/hybrid/api/v2/organizations/{org_id}/environments/{env_id}/applications/{app_id}/status"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()
