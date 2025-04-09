"""ファイル出力を制御するモジュール"""

import json
import os
from datetime import datetime


class FileOutput:
    """ファイル出力を制御するクラス"""

    @staticmethod
    def output_json(data: dict, filename: str) -> str:
        """JSONデータをファイルに出力する

        Args:
            data (dict): 出力するデータ
            filename (str): 出力ファイル名

        Returns:
            str: 出力したファイルのパス
        """
        # 出力先の準備
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        folder_path = os.path.join("output", timestamp_str)
        os.makedirs(folder_path, exist_ok=True)

        # 出力先へ出力
        file_path = f'{folder_path}/{filename}'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path
