#!/usr/bin/env python3
"""Anypoint Platform API Client"""

import json
from auth.client import AuthClient
from api.accounts import AccountsAPI
from api.api_manager import APIManagerClient
from utils.config import Config
from utils.exceptions import ConfigurationError
from utils.file_output import FileOutput
from utils.output_config import OutputConfig

def main():
    """メイン処理"""
    # 設定の読み込みと検証
    config = Config()
    if not config.is_valid:
        raise ConfigurationError("必要な環境変数が設定されていません。")

    # 出力設定の読み込みとフォルダの準備
    output_config = OutputConfig()
    file_output = None
    if output_config.is_output_required:
        file_output = FileOutput()
        file_output.prepare_output_folder()

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

        # 環境別アプリケーションの取得
        applications = api_manager_client.get_applications()
        print("アプリケーションの取得に成功しました：")

        # 環境別アプリケーション情報の出力
        if file_output and output_config.get_output_setting("applications"):
            filename = output_config.get_output_filename("applications")
            file_path = file_output.output_json(applications, filename)
            print(f"アプリケーションの出力に成功しました：{file_path}")

    except Exception as e:
        print(f"アプリケーションの取得時にエラーが発生しました: {e}")

    try:
        # 環境別アプリケーション情報を解析用にコンパクト化
        compact_applications = api_manager_client.compact_applications(applications)

        # コンパクト化されたアプリケーション情報の出力
        if file_output and output_config.get_output_setting("applications_compact"):
            filename = output_config.get_output_filename("applications_compact")
            file_path = file_output.output_json(compact_applications, filename)
            print(f"コンパクト化されたアプリケーション情報の出力に成功しました：{file_path}")

        print("アプリケーションのコンパクト化に成功しました：")
    except Exception as e:
        print(f"アプリケーションのコンパクト化時にエラーが発生しました: {e}")

    try:
        # アプリケーション別にポリシー情報を取得
        policies = []
        for env in compact_applications:
            org_id = env["org_id"]
            env_id = env["env_id"]

            for api in env["apis"]:
                api_id = api["id"]
                policy = api_manager_client.get_policies(org_id, env_id, api_id)
                policies.append({
                    "env_name": env["env_name"],
                    "org_id": org_id,
                    "env_id": env_id,
                    "api_id": str(api_id),
                    "policies": policy["policies"]
                })

        # ポリシー情報の出力
        if file_output and output_config.get_output_setting("policies"):
            filename = output_config.get_output_filename("policies")
            file_path = file_output.output_json(policies, filename)
            print(f"ポリシー情報の出力に成功しました：{file_path}")

        print("ポリシー情報の取得に成功しました：")
    except Exception as e:
        print(f"ポリシー情報の取得時にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()