"""出力設定を制御するモジュール"""

import os
from typing import Dict
from dotenv import dotenv_values


class OutputConfig:
    """出力設定を制御するクラス"""

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """設定ファイルを読み込む

        Returns:
            Dict: 設定内容
        """
        config_path = "config/output_config.env"
        if not os.path.exists(config_path):
            return {}
        return dotenv_values(config_path)

    @property
    def is_output_required(self) -> bool:
        """いずれかの出力が必要かどうか

        Returns:
            bool: いずれかの出力が必要な場合はTrue
        """
        output_keys = ["applications", "applications_compact"]
        return any(self.get_output_setting(key) for key in output_keys)

    def get_output_setting(self, key: str) -> bool:
        """指定された情報の出力設定を取得する

        Args:
            key (str): 設定キー

        Returns:
            bool: 出力が必要な場合はTrue
        """
        env_key = f"{key.upper()}_ENABLED"
        return self._config.get(env_key, "true").lower() == "true"

    def get_output_filename(self, key: str) -> str:
        """指定された情報の出力ファイル名を取得する

        Args:
            key (str): 設定キー

        Returns:
            str: 出力ファイル名
        """
        env_key = f"{key.upper()}_FILENAME"
        # デフォルトのファイル名を設定
        default_filenames = {
            "policies": "policies.json",
            "contracts": "contracts.json",
            "alerts": "alerts.json",
            "tiers": "tiers.json",
            "api_manager": "api_manager.json"
        }
        return self._config.get(env_key, default_filenames.get(key, f"{key}.json"))
