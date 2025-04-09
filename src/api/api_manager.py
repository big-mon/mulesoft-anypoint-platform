#!/usr/bin/env python3
"""API MAnager API"""

import os
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

    def get_applications(self):
        """アプリケーションの取得"""
        # environmentsを全件ループしてアプリケーションを取得
        applications = []
        for env in self._environments:
          url = f"{self._base_url}/apimanager/api/v1/organizations/{env['org_id']}/environments/{env['env_id']}/apis"
          params = {
            'sort': 'name'
          }
          response = self.__session.get(url, params=params)
          response.raise_for_status()

          data = {
            'env_name': env['name'],
            'org_id': env['org_id'],
            'env_id': env['env_id'],
            'apis': response.json()
          }
          applications.append(data)
        return applications