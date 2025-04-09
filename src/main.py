#!/usr/bin/env python3
"""Anypoint Platform API Client"""

import asyncio
from auth.client import AuthClient
from api.accounts import AccountsAPI
from api.api_manager import APIManagerClient
from utils.config import Config
from utils.file_output import FileOutput
from utils.output_config import OutputConfig
from services.api_manager_service import APIManagerService

async def main():
    """メイン処理"""
    # 設定の読み込みと検証
    config = Config()
    if not config.is_valid:
        return

    # 認証クライアントの初期化
    auth_client = AuthClient()

    # アクセストークンの取得
    try:
        access_token = auth_client.get_access_token()
        print("アクセストークンの取得に成功しました：")
    except Exception as e:
        print(f"アクセストークンの取得時にエラーが発生しました: {e}")
        return

    # 出力設定の読み込み
    output_config = OutputConfig()

    # ファイル出力クライアントの初期化
    file_output = FileOutput()
    file_output.prepare_output_folder()

    # 組織情報の取得
    try:
        accounts_api = AccountsAPI(access_token)
        environments = accounts_api.get_organization_environments()
        print("組織情報の取得に成功しました：")
    except Exception as e:
        print(f"組織情報の取得時にエラーが発生しました: {e}")
        return

    # 環境情報の整形
    formatted_environments = []
    for env in environments['data']:
        formatted_environments.append({
            'name': env['name'],
            'org_id': env['organizationId'],
            'env_id': env['id']
        })

    # API Managerクライアントの初期化
    api_manager_client = APIManagerClient(
        access_token,
        formatted_environments
    )

    # API Manager Serviceの初期化
    api_manager_service = APIManagerService(api_manager_client, file_output, output_config)

    # API Manager情報の取得
    await api_manager_service.get_api_manager_info()

    print("処理を完了しました。")

if __name__ == "__main__":
    asyncio.run(main())