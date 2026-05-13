"""Tests for the merge requests MCP server."""

from unittest.mock import patch

from mcp.shared.memory import (
    create_connected_server_and_client_session,
)

from ubuntu_mcp.merge_requests.server import mcp


class TestMergeRequestsServer:
    async def test_get_merge_request(self, mr_service, mock_merge_request_record):
        with patch(
            "ubuntu_mcp.merge_requests.server.get_service",
            return_value=mr_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "get_merge_request",
                    {
                        "merge_request_id": "42",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_get_merge_requests_from_user(self, mr_service):
        with patch(
            "ubuntu_mcp.merge_requests.server.get_service",
            return_value=mr_service,
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "get_merge_requests_from_user",
                    {
                        "user_id": "testuser",
                        "provider_name": "launchpad",
                    },
                )
                assert result.isError is not True

    async def test_login_provider(self, mr_service):
        with patch(
            "ubuntu_mcp.merge_requests.server.login",
            return_value="Authenticated with 'launchpad'.",
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool(
                    "login_provider",
                    {"provider_name": "launchpad"},
                )
                assert result.isError is not True

    async def test_list_merge_request_providers(self, mr_service):
        with patch(
            "ubuntu_mcp.merge_requests.server.list_providers",
            return_value=["github", "launchpad"],
        ):
            async with create_connected_server_and_client_session(mcp) as session:
                result = await session.call_tool("list_merge_request_providers", {})
                assert result.isError is not True
