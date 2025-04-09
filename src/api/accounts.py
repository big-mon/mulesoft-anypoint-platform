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
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        self.__organization_id = os.getenv('ANYPOINT_ORGANIZATION_ID')

    def get_organization_environments(self):
        """組織内の環境の取得"""
        url = f"{self._base_url}/accounts/api/organizations/{self.__organization_id}/environments"
        payload = {
          'extended': False,
          'resolveTheme': False
        }
        response = self._session.get(url, data=payload)
        response.raise_for_status()
        return response.json()
