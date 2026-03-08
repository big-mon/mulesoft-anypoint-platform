#!/usr/bin/env python3
"""Export Runtime Manager information."""

import asyncio
import os

import aiohttp
from dotenv import load_dotenv


load_dotenv()
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10, sock_read=30)


async def export_cloudhub_info(access_token, environments, file_output, output_config):
    """Fetch, transform, and optionally output Runtime Manager information."""
    base_url = os.getenv("ANYPOINT_BASE_URL", "https://anypoint.mulesoft.com")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with aiohttp.ClientSession(headers=headers, timeout=REQUEST_TIMEOUT) as session:
            applications = await _fetch_applications(session, base_url, environments)

        formatted_applications = _format_applications(applications)
        _output_cloudhub_info(formatted_applications, file_output, output_config)
        print("Runtime Manager information exported successfully.")
        return formatted_applications
    except Exception as exc:
        print(f"Failed to export Runtime Manager information: {exc}")
        raise


async def _fetch_applications(session, base_url, environments):
    """Fetch all environments and fail fast if any request fails."""
    tasks = [
        _fetch_environment_applications(session, base_url, environment)
        for environment in environments
    ]
    return await asyncio.gather(*tasks)


async def _fetch_environment_applications(session, base_url, environment):
    url = f"{base_url}/cloudhub/api/v2/applications"
    headers = {"X-ANYPNT-ENV-ID": environment["env_id"]}

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return {
            "env_name": environment["name"],
            "org_id": environment["org_id"],
            "env_id": environment["env_id"],
            "apis": await response.json(),
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
