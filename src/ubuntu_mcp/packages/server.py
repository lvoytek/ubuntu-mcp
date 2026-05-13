"""MCP server for Ubuntu package data via ubq."""

from mcp.server.fastmcp import FastMCP

from ubuntu_mcp.cli import run_server
from ubuntu_mcp.service import (
    get_service,
    list_active_sessions,
    list_providers,
    login,
)

mcp = FastMCP("ubuntu-mcp-packages")


@mcp.tool()
def login_provider(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
) -> str:
    """Authenticate with a package data provider.

    Supported providers include 'launchpad' and 'snapcraft'.
    For providers supporting keyring auth (like Launchpad),
    username and token can be omitted to use system-stored
    credentials.
    """
    return login(
        provider_name=provider_name,
        username=username,
        token=token,
    )


@mcp.tool()
def list_package_providers() -> list[str]:
    """List all available package data provider names."""
    return list_providers()


@mcp.tool()
def get_package(
    package_name: str,
    provider_name: str,
) -> dict | None:
    """Fetch a package by name from the given provider."""
    svc = get_service()
    try:
        record = svc.get_package(
            package_name=package_name,
            provider_name=provider_name,
        )
    except ValueError as exc:
        return {"error": str(exc)}

    if record is None:
        return None

    return {
        "provider_name": record.provider_name,
        "name": record.name,
        "package_url": record.package_url,
    }


@mcp.resource("ubq://packages/providers")
def packages_providers_resource() -> str:
    """Available package data providers."""
    return "\n".join(list_providers())


@mcp.resource("ubq://packages/sessions")
def packages_sessions_resource() -> str:
    """Active package data provider sessions."""
    sessions = list_active_sessions()
    return "\n".join(sessions) if sessions else "No active sessions"


def main():
    run_server(mcp)


if __name__ == "__main__":
    main()
