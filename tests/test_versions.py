"""Tests for the versions MCP server."""

from unittest.mock import patch

from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from ubuntu_mcp.versions.server import mcp


class TestVersionsServer:
    async def test_get_version(self, version_service, mock_version_record):
        with patch(
            "ubuntu_mcp.versions.server.get_service",
            return_value=version_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "get_version",
                    {
                        "package_name": "test-package",
                        "series": "noble",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_login_provider(self, version_service):
        with patch(
            "ubuntu_mcp.versions.server.login",
            return_value="Authenticated with 'launchpad'.",
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "login_provider",
                    {"provider_name": "launchpad"},
                )
                assert result.isError is not True

    async def test_list_version_providers(self, version_service):
        with patch(
            "ubuntu_mcp.versions.server.list_providers",
            return_value=["launchpad", "snapcraft"],
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool("list_version_providers", {})
                assert result.isError is not True
