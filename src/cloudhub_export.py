#!/usr/bin/env python3
"""Export Runtime Manager information."""

import asyncio

try:
    from utils.config import Config
    from utils.http_client import AsyncHTTPClient
except ImportError:
    from src.utils.config import Config
    from src.utils.http_client import AsyncHTTPClient


async def export_cloudhub_info(
    access_token,
    environments,
    file_output,
    output_config,
    http_client=None,
    config=None,
):
    """Fetch, transform, and optionally output Runtime Manager information."""
    config = config or Config()
    headers = {"Authorization": f"Bearer {access_token}"}

    if http_client is None:
        async with AsyncHTTPClient(config) as owned_http_client:
            return await _export_cloudhub_info(
                owned_http_client,
                config.get_base_url(),
                headers,
                environments,
                file_output,
                output_config,
            )

    return await _export_cloudhub_info(
        http_client,
        config.get_base_url(),
        headers,
        environments,
        file_output,
        output_config,
    )


async def _export_cloudhub_info(
    http_client,
    base_url,
    headers,
    environments,
    file_output,
    output_config,
):
    try:
        applications = await _fetch_applications(
            http_client,
            base_url,
            headers,
            environments,
        )
        formatted_applications = _format_applications(applications)
        _output_cloudhub_info(formatted_applications, file_output, output_config)
        print("Runtime Manager information exported successfully.")
        return formatted_applications
    except Exception as exc:
        print(f"Failed to export Runtime Manager information: {exc}")
        raise


async def _fetch_applications(http_client, base_url, headers, environments):
    """Fetch all environments and fail fast if any request fails."""
    tasks = [
        _fetch_environment_applications(http_client, base_url, headers, environment)
        for environment in environments
    ]
    return await asyncio.gather(*tasks)


async def _fetch_environment_applications(http_client, base_url, headers, environment):
    request_headers = {
        **headers,
        "X-ANYPNT-ENV-ID": environment["env_id"],
    }
    payload = await http_client.get_json(
        f"{base_url}/cloudhub/api/v2/applications",
        headers=request_headers,
    )
    return {
        "env_name": environment["name"],
        "org_id": environment["org_id"],
        "env_id": environment["env_id"],
        "apis": payload,
    }


def _format_applications(applications):
    return [
        {
            "env_name": application["env_name"],
            "org_id": application["org_id"],
            "env_id": application["env_id"],
            "apis": application["apis"],
        }
        for application in applications
    ]


def _output_cloudhub_info(applications, file_output, output_config):
    if file_output and output_config.get_output_setting("cloudhub"):
        filename = output_config.get_output_filename("cloudhub")
        file_path = file_output.output_json(applications, filename)
        print(f"Runtime Manager output saved to: {file_path}")
