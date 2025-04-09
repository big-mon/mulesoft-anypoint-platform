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
                            "status": api["status"]
                        })

            compact_applications.append(compact_app)

        return compact_applications