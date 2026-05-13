"""Tests for the shared CLI runner."""

import sys
from unittest.mock import MagicMock, patch

from ubuntu_mcp.cli import run_server


class TestCli:
    def test_default_streamable_http(self):
        mock_mcp = MagicMock()
        with patch.object(sys, "argv", ["ubuntu-mcp-bugs"]):
            run_server(mock_mcp)
        assert mock_mcp.settings.host == "0.0.0.0"
        assert mock_mcp.settings.port == 8000
        mock_mcp.run.assert_called_once_with(transport="streamable-http")

    def test_streamable_http_defaults(self):
        mock_mcp = MagicMock()
        with patch.object(
            sys,
            "argv",
            [
                "ubuntu-mcp-bugs",
                "--transport",
                "streamable-http",
            ],
        ):
            run_server(mock_mcp)
        assert mock_mcp.settings.host == "0.0.0.0"
        assert mock_mcp.settings.port == 8000
        mock_mcp.run.assert_called_once_with(transport="streamable-http")

    def test_streamable_http_custom_host_port(self):
        mock_mcp = MagicMock()
        with patch.object(
            sys,
            "argv",
            [
                "ubuntu-mcp-bugs",
                "--transport",
                "streamable-http",
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
            ],
        ):
            run_server(mock_mcp)
        assert mock_mcp.settings.host == "127.0.0.1"
        assert mock_mcp.settings.port == 9000
        mock_mcp.run.assert_called_once_with(transport="streamable-http")

    def test_stdio_ignores_host_port(self):
        mock_mcp = MagicMock()
        original_host = mock_mcp.settings.host
        original_port = mock_mcp.settings.port
        with patch.object(
            sys,
            "argv",
            [
                "ubuntu-mcp-bugs",
                "--transport",
                "stdio",
                "--host",
                "0.0.0.0",
                "--port",
                "9000",
            ],
        ):
            run_server(mock_mcp)
        assert mock_mcp.settings.host == original_host
        assert mock_mcp.settings.port == original_port
        mock_mcp.run.assert_called_once_with(transport="stdio")

    def test_verbose_flag_short(self):
        from ubuntu_mcp import service

        service._verbose = False
        mock_mcp = MagicMock()
        with patch.object(sys, "argv", ["ubuntu-mcp-bugs", "-v"]):
            run_server(mock_mcp)
        assert service._verbose is True
        service._verbose = False

    def test_verbose_flag_long(self):
        from ubuntu_mcp import service

        service._verbose = False
        mock_mcp = MagicMock()
        with patch.object(sys, "argv", ["ubuntu-mcp-bugs", "--verbose"]):
            run_server(mock_mcp)
        assert service._verbose is True
        service._verbose = False
