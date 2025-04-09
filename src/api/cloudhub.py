import os
import asyncio
from dotenv import load_dotenv
from aiohttp import ClientSession

class CloudHubClient:
    """CloudHub APIクライアント"""
    def __init__(self, token, environments):
        load_dotenv()
        self._base_url = os.getenv('ANYPOINT_BASE_URL')
        self._token = token
        self._environments = environments

    async def get_applications(self):
        """アプリケーションの取得（非同期）"""
        async def fetch_env_applications(session: ClientSession, env: dict) -> dict:
            url = f"{self._base_url}/cloudhub/api/v2/applications"
            headers = {'X-ANYPNT-ENV-ID': env['env_id'], 'Authorization': f'Bearer {self._token}'}

            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                apis = await response.json()
                return {
                    'env_name': env['name'],
                    'org_id': env['org_id'],
                    'env_id': env['env_id'],
                    'apis': apis
                }

        async with ClientSession() as session:
            tasks = [fetch_env_applications(session, env) for env in self._environments]
            applications = await asyncio.gather(*tasks)
            return applications
