#!/usr/bin/env python3
"""Anypoint Platform API Client"""

from auth.client import AuthClient
from utils.config import Config
from utils.exceptions import ConfigurationError

def main():
    """メイン処理"""
    # 設定の読み込みと検証
    config = Config()
    if not config.is_valid:
        raise ConfigurationError("必要な環境変数が設定されていません。")

    # 認証クライアントの初期化
    auth_client = AuthClient()

    try:
        # アクセストークンの取得
        token = auth_client.get_access_token()
        print("アクセストークンの取得に成功しました：")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()