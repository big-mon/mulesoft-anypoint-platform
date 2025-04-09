#!/usr/bin/env python3
"""Accounts API"""

import os
import requests
from dotenv import load_dotenv

class AccountsAPI:
    """Accounts APIクライアント"""

    def __init__(self, token):
        load_dotenv()
        self._base_url = os.getenv('ANYPOINT_BASE_URL')
        self._organization_id = os.getenv('ANYPOINT_ORGANIZATION_ID')
        self.__session = requests.Session()
        self.__session.headers.update({
            'Authorization': f'Bearer {token}'
        })

    def get_organization_environments(self):
        """組織内の環境の取得"""
        url = f"{self._base_url}/accounts/api/organizations/{self._organization_id}/environments"
        payload = {
          'extended': False,
          'resolveTheme': False
        }
        response = self.__session.get(url, data=payload)
        response.raise_for_status()
        return response.json()
