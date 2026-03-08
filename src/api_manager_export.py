#!/usr/bin/env python3
"""Export API Manager information."""

import asyncio

from src.export_common import export_runtime, write_export_output


async def export_api_manager_info(
    access_token,
    environments,
    file_output,
    output_config,
    http_client=None,
    config=None,
):
    """Fetch, transform, and optionally output API Manager information."""
    try:
        async with export_runtime(
            access_token,
            http_client=http_client,
            config=config,
        ) as runtime:
            _, headers, base_url, active_http_client = runtime
            return await _export_api_manager_info(
                active_http_client,
                base_url,
                headers,
                environments,
                file_output,
                output_config,
            )
    except Exception as exc:
        print(f"Failed to export API Manager information: {exc}")
        raise


async def _export_api_manager_info(
    http_client,
    base_url,
    headers,
    environments,
    file_output,
    output_config,
):
    applications = await _fetch_applications(
        http_client,
        base_url,
        headers,
        environments,
    )
    formatted_applications = _format_applications(applications)
    detail_map = await _fetch_detail_map(
        http_client,
        base_url,
        headers,
        formatted_applications,
    )
    _apply_detail_map(formatted_applications, detail_map)
    _output_api_manager_info(formatted_applications, file_output, output_config)
    print("API Manager information exported successfully.")
    return formatted_applications


async def _fetch_applications(http_client, base_url, headers, environments):
    tasks = [
        _fetch_environment_applications(http_client, base_url, headers, environment)
        for environment in environments
    ]
    return await asyncio.gather(*tasks)


async def _fetch_environment_applications(http_client, base_url, headers, environment):
    url = (
        f"{base_url}/apimanager/api/v1/organizations/{environment['org_id']}"
        f"/environments/{environment['env_id']}/apis"
    )
    payload = await http_client.get_json(
        url,
        headers=headers,
        params={"sort": "name"},
    )
    return {
        "env_name": environment["name"],
        "org_id": environment["org_id"],
        "env_id": environment["env_id"],
        "apis": payload,
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


async def _fetch_detail_map(http_client, base_url, headers, applications):
    tasks = []
    for environment in applications:
        for api in environment["apis"]:
            api_id = api.get("id")
            if api_id is None:
                continue
            tasks.append(
                _fetch_api_details(
                    http_client,
                    base_url,
                    headers,
                    environment["org_id"],
                    environment["env_id"],
                    api_id,
                )
            )

    details = await asyncio.gather(*tasks)
    return {
        (detail["org_id"], detail["env_id"], detail["api_id"]): detail
        for detail in details
    }


async def _fetch_api_details(http_client, base_url, headers, org_id, env_id, api_id):
    base_api_url = (
        f"{base_url}/apimanager/api/v1/organizations/{org_id}"
        f"/environments/{env_id}/apis/{api_id}"
    )
    policies, contracts, alerts, tiers = await asyncio.gather(
        _fetch_json(http_client, f"{base_api_url}/policies", headers),
        _fetch_json(http_client, f"{base_api_url}/contracts", headers),
        _fetch_json(http_client, f"{base_api_url}/alerts", headers),
        _fetch_json(http_client, f"{base_api_url}/tiers", headers),
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


async def _fetch_json(http_client, url, headers):
    return await http_client.get_json(url, headers=headers)


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
    write_export_output(
        "api_manager",
        "API Manager",
        applications,
        file_output,
        output_config,
    )
