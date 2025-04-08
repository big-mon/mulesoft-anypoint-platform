#!/usr/bin/env python3
"""Anypoint Platform認証クライアント"""

import os
import requests
from dotenv import load_dotenv

class AuthClient:
    """認証クライアント"""

    def __init__(self):
        load_dotenv()
        self.__access_token = None
        self.__client_id = os.getenv('ANYPOINT_CLIENT_ID')
        self.__client_secret = os.getenv('ANYPOINT_CLIENT_SECRET')
        self._base_url = os.getenv('ANYPOINT_BASE_URL')
        self._session = requests.Session()

    def get_access_token(self):
        """Connected Appを使用してアクセストークンを取得"""
        if self.__access_token:
            return self.__access_token

        auth_url = f"{self._base_url}/accounts/api/v2/oauth2/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.__client_id,
            'client_secret': self.__client_secret
        }
        response = self.session.post(auth_url, data=payload)
        response.raise_for_status()

        self.__access_token = response.json()['access_token']
        return self.__access_token

    def refresh_token(self):
        """アクセストークンを強制的に更新"""
        self.__access_token = None
        return self.get_access_token()
