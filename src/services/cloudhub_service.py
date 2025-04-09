import asyncio
import aiohttp
from api.runtime_manager import RuntimeManagerClient
from utils.file_output import FileOutput
from config.output_config import OutputConfig


class CloudHubService:
    """CloudHub Service"""

    def __init__(self, runtime_manager_client: RuntimeManagerClient, file_output: FileOutput, output_config: OutputConfig):
        """初期化"""
        self._runtime_manager_client = runtime_manager_client
        self._file_output = file_output
        self._output_config = output_config

    async def get_cloudhub_info(self):
        """CloudHub情報の取得"""
        try:
            # アプリケーションの取得
            applications = self._runtime_manager_client.get_applications()
            if len(applications) > 0 and self._output_config.output_applications:
                self._file_output.output_json(applications, "applications")

            # アプリケーションステータスの取得
            statuses = []
            async with aiohttp.ClientSession() as session:
                tasks = []
                for app in applications:
                    tasks.append(self._runtime_manager_client.get_status_async(
                        session,
                        app["org_id"],
                        app["env_id"],
                        app["id"]
                    ))

                if len(tasks) > 0:
                    status_results = await asyncio.gather(*tasks, return_exceptions=True)
                    for i, status_result in enumerate(status_results):
                        if isinstance(status_result, Exception):
                            print(f"Error getting status: {str(status_result)}")
                            continue

                        statuses.append({
                            "env_name": applications[i]["env_name"],
                            "org_id": applications[i]["org_id"],
                            "env_id": applications[i]["env_id"],
                            "app_id": applications[i]["id"],
                            "status": status_result
                        })

                    if len(statuses) > 0 and self._output_config.output_status:
                        self._file_output.output_json(statuses, "application_status")

        except Exception as e:
            print(f"Error in get_runtime_manager_info: {str(e)}")
            raise
