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
        # environmentsを全件ループしてアプリケーションを取得
        applications = []
        for env in self._environments:
            url = f"{self._base_url}/cloudhub/api/v2/applications"
            unique_headers = {
                'X-ANYPNT-ENV-ID': env['env_id']
            }
            headers = self.__session.headers.copy()
            headers.update(unique_headers)
            response = self.__session.get(url, headers=headers)
            response.raise_for_status()

            data = {
                'env_name': env['name'],
                'org_id': env['org_id'],
                'env_id': env['env_id'],
                'apis': response.json()
            }
            applications.append(data)
        return applications
