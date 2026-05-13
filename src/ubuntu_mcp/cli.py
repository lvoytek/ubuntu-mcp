"""Shared CLI runner for ubuntu-mcp servers."""

import argparse


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
    args = parser.parse_args()

    if args.transport != "stdio":
        mcp_instance.settings.host = args.host
        mcp_instance.settings.port = args.port

    mcp_instance.run(transport=args.transport)
