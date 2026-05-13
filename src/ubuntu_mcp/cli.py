"""Shared CLI runner for ubuntu-mcp servers."""

import argparse

from mcp.server.transport_security import TransportSecuritySettings

from ubuntu_mcp.service import set_verbose


def run_server(mcp_instance) -> None:
    """Parse CLI args and run the given FastMCP server."""
    parser = argparse.ArgumentParser(description=mcp_instance.name)
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        help="Allowed Host header value (repeatable). Required when behind a reverse proxy.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print every ubq API call",
    )
    args = parser.parse_args()

    if args.verbose:
        set_verbose(True)

    if args.transport != "stdio":
        mcp_instance.settings.host = args.host
        mcp_instance.settings.port = args.port
        if args.allowed_host:
            mcp_instance.settings.transport_security = TransportSecuritySettings(
                allowed_hosts=args.allowed_host,
                allowed_origins=args.allowed_host,
            )

    mcp_instance.run(transport=args.transport)
