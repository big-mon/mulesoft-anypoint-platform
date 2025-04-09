"""出力設定を制御するモジュール"""

import json
import os
from typing import Dict


class OutputConfig:
    """出力設定を制御するクラス"""

    def __init__(self):
        self._config = {}
        self._load_config()

    def _load_config(self):
        """設定ファイルを読み込む"""
        config_path = "config/output_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)

    @property
    def is_output_required(self) -> bool:
        """いずれかの出力が必要かどうか

        Returns:
            bool: いずれかの出力が必要な場合はTrue
        """
        return any(self.get_output_setting(key) for key in ["applications"])

    def get_output_setting(self, key: str) -> bool:
        """指定された情報の出力設定を取得する

        Args:
            key (str): 設定キー

        Returns:
            bool: 出力が必要な場合はTrue
        """
        return self._config.get(key, {}).get("enabled", True)

    def get_output_filename(self, key: str) -> str:
        """指定された情報の出力ファイル名を取得する

        Args:
            key (str): 設定キー

        Returns:
            str: 出力ファイル名
        """
        output_filenames = {
            "applications": "applications-full.json"
        }
        return output_filenames.get(key, "")
