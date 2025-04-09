"""ファイル出力を制御するモジュール"""

import json
import os
from datetime import datetime
from typing import Optional


class FileOutput:
    """ファイル出力を制御するクラス"""
    
    def __init__(self):
        self._output_folder: Optional[str] = None

    def prepare_output_folder(self) -> None:
        """出力先フォルダを準備する"""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M")
        self._output_folder = os.path.join("output", timestamp_str)
        os.makedirs(self._output_folder, exist_ok=True)

    def output_json(self, data: dict, filename: str) -> str:
        """JSONデータをファイルに出力する

        Args:
            data (dict): 出力するデータ
            filename (str): 出力ファイル名

        Returns:
            str: 出力したファイルのパス

        Raises:
            RuntimeError: 出力フォルダが準備されていない場合
        """
        if not self._output_folder:
            raise RuntimeError("出力フォルダが準備されていません。prepare_output_folderを先に呼び出してください。")

        # 出力先へ出力
        file_path = os.path.join(self._output_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path
