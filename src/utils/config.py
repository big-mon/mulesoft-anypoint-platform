"""設定管理モジュール"""

import os
from dotenv import load_dotenv

class Config:
    """設定管理クラス"""
    
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('ANYPOINT_CLIENT_ID')
        self.client_secret = os.getenv('ANYPOINT_CLIENT_SECRET')
        self.organization_id = os.getenv('ANYPOINT_ORGANIZATION_ID')
        self.environment_id = os.getenv('ANYPOINT_ENVIRONMENT_ID')
        self.base_url = os.getenv('ANYPOINT_BASE_URL', 'https://anypoint.mulesoft.com')

    @property
    def is_valid(self):
        """必要な設定値が全て存在するか確認"""
        return all([
            self.client_id,
            self.client_secret,
            self.organization_id,
            self.environment_id,
            self.base_url
        ])
