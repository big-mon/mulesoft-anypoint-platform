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
        self._environment_id = os.getenv('ANYPOINT_ENVIRONMENT_ID')
        self._base_url = os.getenv('ANYPOINT_BASE_URL', 'https://anypoint.mulesoft.com')

    @property
    def is_valid(self):
        """必要な設定値が全て存在するか確認"""
        return all([
            self.__client_id,
            self.__client_secret,
            self._organization_id,
            self._environment_id,
            self._base_url
        ])
