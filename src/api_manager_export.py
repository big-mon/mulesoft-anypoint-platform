#!/usr/bin/env python3
"""Export API Manager information."""

import asyncio
import os

import aiohttp
from dotenv import load_dotenv

try:
    from utils.proxy import ProxyConfig
except ImportError:
    from src.utils.proxy import ProxyConfig


load_dotenv()
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10, sock_read=30)


async def export_api_manager_info(access_token, environments, file_output, output_config):
    """Fetch, transform, and optionally output API Manager information."""
    base_url = os.getenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    headers = {"Authorization": f"Bearer {access_token}"}
    proxy_config = ProxyConfig()

    try:
        async with aiohttp.ClientSession(headers=headers, timeout=REQUEST_TIMEOUT) as session:
            applications = await _fetch_applications(
                session,
                base_url,
                environments,
                proxy_config,
            )
            formatted_applications = _format_applications(applications)
            detail_map = await _fetch_detail_map(
                session,
                base_url,
                formatted_applications,
                proxy_config,
            )

        _apply_detail_map(formatted_applications, detail_map)
        _output_api_manager_info(formatted_applications, file_output, output_config)
        print("API Manager information exported successfully.")
        return formatted_applications
    except Exception as exc:
        print(f"Failed to export API Manager information: {exc}")
        return None


async def _fetch_applications(session, base_url, environments, proxy_config):
    tasks = [
        _fetch_environment_applications(session, base_url, environment, proxy_config)
        for environment in environments
    ]
    return await asyncio.gather(*tasks)


async def _fetch_environment_applications(session, base_url, environment, proxy_config):
    url = (
        f"{base_url}/apimanager/api/v1/organizations/{environment['org_id']}"
        f"/environments/{environment['env_id']}/apis"
    )
    params = {"sort": "name"}
    request_kwargs = proxy_config.get_aiohttp_request_kwargs(url)
    async with session.get(url, params=params, **request_kwargs) as response:
        response.raise_for_status()
        return {
            "env_name": environment["name"],
            "org_id": environment["org_id"],
            "env_id": environment["env_id"],
            "apis": await response.json(),
        }


def _format_applications(applications):
    formatted = []
    for application in applications:
        formatted_application = {
            "env_name": application["env_name"],
            "org_id": application["org_id"],
            "env_id": application["env_id"],
            "apis": [],
        }

        for asset in application["apis"].get("assets", []):
            for api in asset.get("apis", []):
                deployment = api.get("deployment") or {}
                formatted_application["apis"].append(
                    {
                        "id": api.get("id"),
                        "exchangeAssetName": asset.get("exchangeAssetName", ""),
                        "instanceLabel": api.get("instanceLabel", ""),
                        "activeContractsCount": api.get("activeContractsCount", 0),
                        "status": api.get("status"),
                        "deployment_applicationId": deployment.get("applicationId"),
                    }
                )

        formatted.append(formatted_application)

    return formatted


async def _fetch_detail_map(session, base_url, applications, proxy_config):
    tasks = []
    for environment in applications:
        for api in environment["apis"]:
            api_id = api.get("id")
            if api_id is None:
                continue
            tasks.append(
                _fetch_api_details(
                    session,
                    base_url,
                    environment["org_id"],
                    environment["env_id"],
                    api_id,
                    proxy_config,
                )
            )

    details = await asyncio.gather(*tasks)
    return {
        (detail["org_id"], detail["env_id"], detail["api_id"]): detail
        for detail in details
    }


async def _fetch_api_details(session, base_url, org_id, env_id, api_id, proxy_config):
    policies_url = (
        f"{base_url}/apimanager/api/v1/organizations/{org_id}"
        f"/environments/{env_id}/apis/{api_id}/policies"
    )
    contracts_url = (
        f"{base_url}/apimanager/api/v1/organizations/{org_id}"
        f"/environments/{env_id}/apis/{api_id}/contracts"
    )
    alerts_url = (
        f"{base_url}/apimanager/api/v1/organizations/{org_id}"
        f"/environments/{env_id}/apis/{api_id}/alerts"
    )
    tiers_url = (
        f"{base_url}/apimanager/api/v1/organizations/{org_id}"
        f"/environments/{env_id}/apis/{api_id}/tiers"
    )

    policies, contracts, alerts, tiers = await asyncio.gather(
        _fetch_json(session, policies_url, proxy_config),
        _fetch_json(session, contracts_url, proxy_config),
        _fetch_json(session, alerts_url, proxy_config),
        _fetch_json(session, tiers_url, proxy_config),
    )

    return {
        "org_id": org_id,
        "env_id": env_id,
        "api_id": str(api_id),
        "policies": policies.get("policies", []),
        "contracts": contracts.get("contracts", []),
        "alerts": alerts,
        "tiers": tiers.get("tiers", []),
    }


async def _fetch_json(session, url, proxy_config):
    request_kwargs = proxy_config.get_aiohttp_request_kwargs(url)
    async with session.get(url, **request_kwargs) as response:
        response.raise_for_status()
        return await response.json()


def _apply_detail_map(applications, detail_map):
    for environment in applications:
        for api in environment["apis"]:
            api_id = api.get("id")
            detail = detail_map.get(
                (environment["org_id"], environment["env_id"], str(api_id))
            )
            api["policies"] = detail["policies"] if detail else []
            api["contracts"] = detail["contracts"] if detail else []
            api["alerts"] = detail["alerts"] if detail else []
            api["tiers"] = detail["tiers"] if detail else []


def _output_api_manager_info(applications, file_output, output_config):
    if file_output and output_config.get_output_setting("api_manager"):
        filename = output_config.get_output_filename("api_manager")
        file_path = file_output.output_json(applications, filename)
        print(f"API Manager output saved to: {file_path}")
