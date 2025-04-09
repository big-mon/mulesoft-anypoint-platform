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
            applications = await self._get_applications()
            if not applications:
                return None

            api_details = await self._fetch_api_details(applications)
            if not api_details:
                return None

            integrated_applications = self._integrate_api_details(applications, api_details)
            if not integrated_applications:
                return None

            await self._output_api_manager_info(integrated_applications)
            return integrated_applications

        except Exception as e:
            print(f"API Manager情報の取得時にエラーが発生しました: {e}")
            return None

    async def _get_applications(self):
        """アプリケーション情報の取得"""
        try:
            applications = await self._api_manager_client.get_applications()
            compact_applications = self._api_manager_client.compact_applications(applications)
            print("アプリケーション情報の取得に成功しました")
            return compact_applications
        except Exception as e:
            print(f"アプリケーション情報の取得時にエラーが発生しました: {e}")
            return None

    async def _fetch_api_details(self, applications):
        """API詳細情報の非同期取得"""
        try:
            api_count = sum(len(env.get("apis", [])) for env in applications)
            if api_count == 0:
                print("処理対象のAPIが見つかりません")
                return None

            async with aiohttp.ClientSession() as session:
                tasks = []
                for env in applications:
                    org_id = env["org_id"]
                    env_id = env["env_id"]

                    for api in env["apis"]:
                        api_id = api["id"]
                        tasks.extend([
                            self._api_manager_client.get_policies_async(session, org_id, env_id, api_id),
                            self._api_manager_client.get_contracts_async(session, org_id, env_id, api_id),
                            self._api_manager_client.get_alerts_async(session, org_id, env_id, api_id),
                            self._api_manager_client.get_tiers_async(session, org_id, env_id, api_id)
                        ])

                results = await asyncio.gather(*tasks)
                if len(results) != 4 * api_count:
                    print(f"予期しない結果数です: {len(results)} (expected: {4 * api_count})")
                    return None

                return self._organize_api_details(applications, results)

        except Exception as e:
            print(f"API詳細情報の取得時にエラーが発生しました: {e}")
            return None

    def _organize_api_details(self, applications, results):
        """API詳細情報の整理"""
        policies = []
        contracts = []
        alerts = []
        tiers = []
        result_index = 0

        for env in applications:
            for api in env["apis"]:
                policy_result = results[result_index]
                contract_result = results[result_index + 1]
                alert_result = results[result_index + 2]
                tier_result = results[result_index + 3]
                result_index += 4

                api_details = {
                    "env_name": env["env_name"],
                    "org_id": env["org_id"],
                    "env_id": env["env_id"],
                    "api_id": str(api["id"])
                }

                policies.append({**api_details, "policies": policy_result["policies"]})
                contracts.append({**api_details, "contracts": contract_result})
                alerts.append({**api_details, "alerts": alert_result})
                tiers.append({**api_details, "tiers": tier_result})

        return {"policies": policies, "contracts": contracts, "alerts": alerts, "tiers": tiers}

    def _integrate_api_details(self, applications, api_details):
        """API詳細情報の統合"""
        try:
            for env in applications:
                for api in env["apis"]:
                    api_id = str(api["id"])
                    self._integrate_single_api_details(api, api_id, api_details)
            return applications
        except Exception as e:
            print(f"API詳細情報の統合時にエラーが発生しました: {e}")
            return None

    def _integrate_single_api_details(self, api, api_id, api_details):
        """単一APIの詳細情報統合"""
        # ポリシー情報の結合
        policy = next((p for p in api_details["policies"] if p["api_id"] == api_id), None)
        api["policies"] = policy["policies"] if policy else []

        # コントラクト情報の結合
        contract = next((c for c in api_details["contracts"] if c["api_id"] == api_id), None)
        api["contracts"] = contract["contracts"]["contracts"] if contract else []

        # アラート情報の結合
        alert = next((a for a in api_details["alerts"] if a["api_id"] == api_id), None)
        api["alerts"] = alert["alerts"] if alert else []

        # ティア情報の結合
        tier = next((t for t in api_details["tiers"] if t["api_id"] == api_id), None)
        api["tiers"] = tier["tiers"]["tiers"] if tier else []

    async def _output_api_manager_info(self, applications):
        """API Manager情報の出力"""
        if self._file_output and self._output_config.get_output_setting("api_manager"):
            filename = self._output_config.get_output_filename("api_manager")
            file_path = self._file_output.output_json(applications, filename)
            print(f"API Manager情報の出力に成功しました：{file_path}")