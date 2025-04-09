"""設定管理モジュール"""

import os
from dotenv import load_dotenv

class Config:
    """設定管理クラス"""

    def __init__(self):
        load_dotenv()
        self.__client_id = os.getenv('ANYPOINT_CLIENT_ID')
        self.__client_secret = os.getenv('ANYPOINT_CLIENT_SECRET')
        self._organization_id = os.getenv('ANYPOINT_ORGANIZATION_ID')
        self._base_url = os.getenv('ANYPOINT_BASE_URL', 'https://anypoint.mulesoft.com')

    def get_client_id(self):
        """クライアントIDを取得"""
        return self.__client_id

    def get_client_secret(self):
        """クライアントシークレットを取得"""
        return self.__client_secret

    def get_organization_id(self):
        """組織IDを取得"""
        return self._organization_id

    def get_base_url(self):
        """ベースURLを取得"""
        return self._base_url

    @property
    def is_valid(self):
        """必要な設定値が全て存在するか確認"""
        return all([
            self.__client_id,
            self.__client_secret,
            self._organization_id,
            self._base_url
        ])
