#!/usr/bin/env python3
"""Anypoint Platform API Client."""

import asyncio

from src.api.accounts import AccountsAPI
from src.api_manager_export import export_api_manager_info
from src.auth.client import AuthClient
from src.cloudhub_export import export_cloudhub_info
from src.utils.config import Config
from src.utils.file_output import FileOutput
from src.utils.http_client import AsyncHTTPClient
from src.utils.output_config import OutputConfig


async def main():
    """Main entry point."""
    config = Config()
    if not config.is_valid:
        return

    output_config = OutputConfig()
    file_output = FileOutput()
    file_output.prepare_output_folder()

    async with AsyncHTTPClient(config) as http_client:
        auth_client = AuthClient(http_client, config=config)

        try:
            access_token = await auth_client.get_access_token()
            print("Access token retrieved successfully.")
        except Exception as exc:
            print(f"Failed to retrieve access token: {exc}")
            return

        try:
            accounts_api = AccountsAPI(access_token, http_client, config=config)
            environments = await accounts_api.get_organization_environments()
            print("Organization environments retrieved successfully.")
        except Exception as exc:
            print(f"Failed to retrieve organization environments: {exc}")
            return

        formatted_environments = [
            {
                "name": environment["name"],
                "org_id": environment["organizationId"],
                "env_id": environment["id"],
            }
            for environment in environments.get("data", [])
        ]

        try:
            await asyncio.gather(
                export_api_manager_info(
                    access_token,
                    formatted_environments,
                    file_output,
                    output_config,
                    http_client=http_client,
                    config=config,
                ),
                export_cloudhub_info(
                    access_token,
                    formatted_environments,
                    file_output,
                    output_config,
                    http_client=http_client,
                    config=config,
                ),
            )
        except Exception as exc:
            print(f"Failed to export information: {exc}")
            return

    print("Completed.")


if __name__ == "__main__":
    asyncio.run(main())
