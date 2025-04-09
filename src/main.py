#!/usr/bin/env python3
"""Anypoint Platform API Client"""

import json
import os
from auth.client import AuthClient
from api.accounts import AccountsAPI
from api.api_manager import APIManagerClient
from utils.config import Config
from utils.exceptions import ConfigurationError
from datetime import datetime

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
            environments.append({"name": env['name'], "env_id": env['id'], "org_id": env['organizationId']})

    except Exception as e:
        print(f"組織情報の取得時にエラーが発生しました: {e}")

    try:
        # API Managerクライアントの初期化
        api_manager_client = APIManagerClient(token, environments)

        # アプリケーションの取得
        applications = api_manager_client.get_applications()
        print("アプリケーションの取得に成功しました：")

        # 出力先の準備
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("output", timestamp_str)
        os.makedirs(folder_path, exist_ok=True)

        # 出力先へ出力
        file_path = f'{folder_path}/applications.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(applications, f, indent=2, ensure_ascii=False)
        print(f"アプリケーションの出力に成功しました：{file_path}")

    except Exception as e:
        print(f"アプリケーションの取得時にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()