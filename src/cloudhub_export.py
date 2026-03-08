#!/usr/bin/env python3
"""Export Runtime Manager information."""

import asyncio

from src.export_common import export_runtime, write_export_output


async def export_cloudhub_info(
    access_token,
    environments,
    file_output,
    output_config,
    http_client=None,
    config=None,
):
    """Fetch, transform, and optionally output Runtime Manager information."""
    async with export_runtime(
        access_token,
        http_client=http_client,
        config=config,
    ) as runtime:
        _, headers, base_url, active_http_client = runtime
        return await _export_cloudhub_info(
            active_http_client,
            base_url,
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
    write_export_output(
        "cloudhub",
        "Runtime Manager",
        applications,
        file_output,
        output_config,
    )
