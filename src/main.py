#!/usr/bin/env python3
"""Anypoint Platform API Client"""

from auth.client import AuthClient
from api.accounts import AccountsAPI
from utils.config import Config
from utils.exceptions import ConfigurationError

def main():
    """メイン処理"""
    # 設定の読み込みと検証
    config = Config()
    if not config.is_valid:
        raise ConfigurationError("必要な環境変数が設定されていません。")

    try:
        # 認証クライアントの初期化
        auth_client = AuthClient()

        # アクセストークンの取得
        token = auth_client.get_access_token()
        print("アクセストークンの取得に成功しました：")
    except Exception as e:
        print(f"アクセストークンの取得時にエラーが発生しました: {e}")

    try:
        # API Platformクライアントの初期化
        api_platform_client = AccountsAPI(token)

        # 組織内の環境を取得
        organization = api_platform_client.get_organization_environments()
        environments = []
        print("組織情報の取得に成功しました：")
        for env in organization['data']:
            environments.append({"name": env['name'], "id": env['id']})

    except Exception as e:
        print(f"組織情報の取得時にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()