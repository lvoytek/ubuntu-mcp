"""Tests for the packages MCP server."""

from unittest.mock import patch

from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from ubuntu_mcp.packages.server import mcp


class TestPackagesServer:
    async def test_get_package(self, package_service, mock_package_record):
        with patch(
            "ubuntu_mcp.packages.server.get_service",
            return_value=package_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "get_package",
                    {
                        "package_name": "test-package",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_login_provider(self, package_service):
        with patch(
            "ubuntu_mcp.packages.server.login",
            return_value="Authenticated with 'launchpad'.",
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "login_provider",
                    {"provider_name": "launchpad"},
                )
                assert result.isError is not True

    async def test_list_package_providers(self, package_service):
        with patch(
            "ubuntu_mcp.packages.server.list_providers",
            return_value=["launchpad", "snapcraft"],
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool("list_package_providers", {})
                assert result.isError is not True
