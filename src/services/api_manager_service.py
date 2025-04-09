#!/usr/bin/env python3
"""API Manager Service"""

import asyncio
import aiohttp
from api.api_manager import APIManagerClient
from utils.file_output import FileOutput
from utils.output_config import OutputConfig

class APIManagerService:
    """API Manager Service"""

    def __init__(self, api_manager_client: APIManagerClient, file_output: FileOutput, output_config: OutputConfig):
        """初期化"""
        self._api_manager_client = api_manager_client
        self._file_output = file_output
        self._output_config = output_config

    async def get_api_manager_info(self):
        """API Manager情報の取得"""
        try:
            # アプリケーションの取得
            applications = self._api_manager_client.get_applications()
            print("アプリケーションの取得に成功しました：")
        except Exception as e:
            print(f"アプリケーションの取得時にエラーが発生しました: {e}")
            return None

        try:
            # アプリケーション情報のコンパクト化
            compact_applications = self._api_manager_client.compact_applications(applications)
            print("アプリケーションのコンパクト化に成功しました：")
        except Exception as e:
            print(f"アプリケーションのコンパクト化時にエラーが発生しました: {e}")
            return None

        try:
            # アプリケーション別にポリシー情報、Contracts情報、アラート情報を非同期で取得
            policies = []
            contracts = []
            alerts = []
            tiers = []
            async with aiohttp.ClientSession() as session:
                tasks = []
                for env in compact_applications:
                    org_id = env["org_id"]
                    env_id = env["env_id"]

                    for api in env["apis"]:
                        api_id = api["id"]
                        tasks.append(asyncio.create_task(
                            self._api_manager_client.get_policies_async(session, org_id, env_id, api_id)
                        ))
                        tasks.append(asyncio.create_task(
                            self._api_manager_client.get_contracts_async(session, org_id, env_id, api_id)
                        ))
                        tasks.append(asyncio.create_task(
                            self._api_manager_client.get_alerts_async(session, org_id, env_id, api_id)
                        ))
                        tasks.append(asyncio.create_task(
                            self._api_manager_client.get_tiers_async(session, org_id, env_id, api_id)
                        ))

                # すべてのタスクを実行
                results = await asyncio.gather(*tasks)

                # 結果を整理
                if not compact_applications:
                    print("アプリケーション情報が見つかりません")
                    return None

                # API情報を含む環境をカウント
                api_count = 0
                for env in compact_applications:
                    if env.get("apis") and len(env["apis"]) > 0:
                        api_count += len(env["apis"])

                if api_count == 0:
                    print("処理対象のAPIが見つかりません")
                    return None

                if len(results) != 4 * api_count:
                    print(f"予期しない結果数です: {len(results)} (expected: {4 * api_count})")
                    return None

                result_index = 0
                for env in compact_applications:
                    for api in env["apis"]:
                        policy_result = results[result_index]
                        contract_result = results[result_index + 1]
                        alert_result = results[result_index + 2]
                        tier_result = results[result_index + 3]
                        result_index += 4

                        policies.append({
                            "env_name": env["env_name"],
                            "org_id": env["org_id"],
                            "env_id": env["env_id"],
                            "api_id": str(api["id"]),
                            "policies": policy_result["policies"]
                        })
                        alerts.append({
                            "env_name": env["env_name"],
                            "org_id": env["org_id"],
                            "env_id": env["env_id"],
                            "api_id": str(api["id"]),
                            "alerts": alert_result
                        })
                        contracts.append({
                            "env_name": env["env_name"],
                            "org_id": env["org_id"],
                            "env_id": env["env_id"],
                            "api_id": str(api["id"]),
                            "contracts": contract_result
                        })

            # ポリシー情報の出力
            if self._file_output and self._output_config.get_output_setting("policies"):
                filename = self._output_config.get_output_filename("policies")
                file_path = self._file_output.output_json(policies, filename)
                print(f"ポリシー情報の出力に成功しました：{file_path}")

            # Contracts情報の出力
            if self._file_output and self._output_config.get_output_setting("contracts"):
                filename = self._output_config.get_output_filename("contracts")
                file_path = self._file_output.output_json(contracts, filename)
                print(f"Contracts情報の出力に成功しました：{file_path}")

            # アラート情報の出力
            if self._file_output and self._output_config.get_output_setting("alerts"):
                filename = self._output_config.get_output_filename("alerts")
                file_path = self._file_output.output_json(alerts, filename)
                print(f"アラート情報の出力に成功しました：{file_path}")

            # ティア情報の出力
            if self._file_output and self._output_config.get_output_setting("tiers"):
                filename = self._output_config.get_output_filename("tiers")
                file_path = self._file_output.output_json(tiers, filename)
                print(f"ティア情報の出力に成功しました：{file_path}")

            print("ポリシー情報、Contracts情報、アラート情報、ティア情報の取得に成功しました：")

            try:
                # API Manager情報を統合
                for env in compact_applications:
                    for api in env["apis"]:
                        api_id = str(api["id"])
                        # ポリシー情報の結合
                        policy = next((p for p in policies if p["api_id"] == api_id), None)
                        if policy:
                            api["policies"] = policy["policies"]
                        else:
                            api["policies"] = []

                        # コントラクト情報の結合
                        contract = next((c for c in contracts if c["api_id"] == api_id), None)
                        if contract:
                            api["contracts"] = contract["contracts"]["contracts"]
                        else:
                            api["contracts"] = []

                        # アラート情報の結合
                        alert = next((a for a in alerts if a["api_id"] == api_id), None)
                        if alert:
                            api["alerts"] = alert["alerts"]
                        else:
                            api["alerts"] = []

                        # ティア情報の結合
                        tier = next((t for t in tiers if t["api_id"] == api_id), None)
                        if tier:
                            api["tiers"] = tier["tiers"]
                        else:
                            api["tiers"] = []

                # 統合したAPI Manager情報の出力
                if self._file_output and self._output_config.get_output_setting("api_manager"):
                    filename = self._output_config.get_output_filename("api_manager")
                    file_path = self._file_output.output_json(compact_applications, filename)
                    print(f"API Manager情報の出力に成功しました：{file_path}")

                return compact_applications

            except Exception as e:
                print(f"API Manager情報の統合時にエラーが発生しました: {e}")
                return None

        except Exception as e:
            print(f"ポリシー情報、Contracts情報、アラート情報の取得時にエラーが発生しました: {e}")
            return None
