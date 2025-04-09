import os
from dotenv import load_dotenv
import requests
import aiohttp


class CloudHubClient:
    """CloudHub APIクライアント"""
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
            url = f"{self._base_url}/cloudhub/api/v2/applications"
            unique_headers = {
                'X-ANYPNT-ENV-ID': env['env_id']
            }
            headers = self.__session.headers.copy()
            headers.update(unique_headers)
            response = self.__session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for app in data:
                results.append(app)

        return results

    async def get_status_async(self, session, app_id):
        """アプリケーションステータスの非同期取得"""
        url = f"{self._base_url}/cloudhub/api/v2/applications/{app_id}/status"
        async with session.get(url, headers=self.__session.headers) as response:
            response.raise_for_status()
            return await response.json()