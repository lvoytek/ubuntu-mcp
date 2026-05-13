"""Tests for the bugs MCP server."""

from unittest.mock import patch

from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from ubuntu_mcp.bugs.server import mcp


class TestBugsServer:
    async def test_get_bug(self, bug_service, mock_bug_record):
        with patch(
            "ubuntu_mcp.bugs.server.get_service",
            return_value=bug_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "get_bug",
                    {
                        "bug_id": "12345",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_search_bugs(self, bug_service, mock_bug_record):
        with patch(
            "ubuntu_mcp.bugs.server.get_service",
            return_value=bug_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "search_bugs",
                    {
                        "provider_name": "launchpad",
                        "title": "Test",
                    },
                )
                assert result.isError is not True

    async def test_submit_bug(self, bug_service, mock_bug_record):
        with patch(
            "ubuntu_mcp.bugs.server.get_service",
            return_value=bug_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "submit_bug",
                    {
                        "title": "New Bug",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_login_provider(self, bug_service):
        with (
            patch(
                "ubuntu_mcp.bugs.server.get_service",
                return_value=bug_service,
            ),
            patch(
                "ubuntu_mcp.bugs.server.login",
                return_value="Authenticated with 'launchpad'.",
            ),
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "login_provider",
                    {"provider_name": "launchpad"},
                )
                assert result.isError is not True

    async def test_list_bug_providers(self, bug_service):
        with patch(
            "ubuntu_mcp.bugs.server.list_providers",
            return_value=["github", "launchpad"],
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool("list_bug_providers", {})
                assert result.isError is not True
