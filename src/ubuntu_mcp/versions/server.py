"""MCP server for Ubuntu package version data via ubq."""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

from ubuntu_mcp.cli import run_server
from ubuntu_mcp.service import (
    get_service,
    list_active_sessions,
    list_providers,
    login,
)

mcp = FastMCP("ubuntu-mcp-versions")


@mcp.tool()
def login_provider(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
    credential_file: str | None = None,
) -> str:
    """Authenticate with a version data provider.

    Supported providers include 'launchpad' and 'snapcraft'.
    For Launchpad: provide a token directly, a credential file path
    containing the token, or omit both to authenticate anonymously.
    """
    return login(
        provider_name=provider_name,
        username=username,
        token=token,
        credential_file=credential_file,
    )


@mcp.tool()
def list_version_providers() -> list[str]:
    """List all available version data provider names."""
    return list_providers()


@mcp.tool()
def get_version(
    package_name: str,
    series: str,
    provider_name: str,
    pocket: str | None = None,
) -> dict | None:
    """Fetch the version of a package in a given Ubuntu series.

    The 'series' is the Ubuntu codename (e.g. 'noble', 'jammy').
    The 'pocket' can be 'Release', 'Security', 'Updates',
    'Proposed', or None for the default.
    """
    svc = get_service()
    try:
        record = svc.get_version(
            package_name=package_name,
            series=series,
            pocket=pocket,
            provider_name=provider_name,
        )
    except ValueError as exc:
        return {"error": str(exc)}

    if record is None:
        return None

    return {
        "provider_name": record.provider_name,
        "version_string": record.version_string,
        "package_name": record.package_name,
        "series": record.series,
        "pocket": record.pocket,
        "created_at": _fmt_dt(record.created_at),
        "released_at": _fmt_dt(record.released_at),
    }


@mcp.resource("ubq://versions/providers")
def versions_providers_resource() -> str:
    """Available version data providers."""
    return "\n".join(list_providers())


@mcp.resource("ubq://versions/sessions")
def versions_sessions_resource() -> str:
    """Active version data provider sessions."""
    sessions = list_active_sessions()
    return "\n".join(sessions) if sessions else "No active sessions"


def _fmt_dt(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def main():
    run_server(mcp)


if __name__ == "__main__":
    main()
