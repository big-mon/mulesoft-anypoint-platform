#!/usr/bin/env python3
"""CloudHub Service"""

import asyncio
import aiohttp
from api.cloudhub import CloudHubClient
from utils.file_output import FileOutput
from utils.output_config import OutputConfig


class CloudHubService:
    """CloudHub Service"""

    def __init__(self, cloudhub_client: CloudHubClient, file_output: FileOutput, output_config: OutputConfig):
        """初期化"""
        self._cloudhub_client = cloudhub_client
        self._file_output = file_output
        self._output_config = output_config

    async def get_cloudhub_info(self):
        """CloudHub情報の取得"""
        try:
            # アプリケーションの取得
            applications = await self._cloudhub_client.get_applications()
            print("get_cloudhub_infoに成功しました：")

        except Exception as e:
            print(f"get_cloudhub_info時にエラーが発生しました: {e}")
            raise

        # CloudHub情報の出力
        if self._file_output and self._output_config.get_output_setting("cloudhub"):
            filename = self._output_config.get_output_filename("cloudhub")
            file_path = self._file_output.output_json(applications, filename)
            print(f"get_cloudhub_info:CloudHub情報の出力に成功しました：{file_path}")