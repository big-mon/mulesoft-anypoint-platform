#!/usr/bin/env python3
"""Anypoint Platform API Client"""

import os
import requests
from dotenv import load_dotenv

class AnypointClient:
    """MuleSoft Anypoint Platform APIクライアント"""

    def __init__(self):
        load_dotenv()  # .envファイルから環境変数を読み込み
        self.client_id = os.getenv('ANYPOINT_CLIENT_ID')
        self.client_secret = os.getenv('ANYPOINT_CLIENT_SECRET')
        self.base_url = os.getenv('ANYPOINT_BASE_URL')
        self.session = requests.Session()

    def get_access_token(self):
        """Connected Appを使用してアクセストークンを取得"""
        auth_url = f"{self.base_url}/accounts/api/v2/oauth2/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']

    def get_applications(self):
        """アプリケーション一覧を取得"""
        pass

if __name__ == "__main__":
    client = AnypointClient()
    print("Anypoint Platform Client initialized")
    try:
        token = client.get_access_token()
        print("アクセストークンの取得に成功しました：")
        print(f"Token: {token[:30]}...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")