"""MCP server for Ubuntu merge request data via ubq."""

from datetime import datetime

from mcp.server.fastmcp import FastMCP
from ubq.models import UserRecord

from ubuntu_mcp.cli import run_server
from ubuntu_mcp.service import (
    get_service,
    list_active_sessions,
    list_providers,
    login,
)

mcp = FastMCP("ubuntu-mcp-merge-requests")


@mcp.tool()
def login_provider(
    provider_name: str,
    username: str | None = None,
    token: str | None = None,
    credential_file: str | None = None,
) -> str:
    """Authenticate with a merge request provider.

    Supported providers include 'launchpad' and 'github'.
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
def list_merge_request_providers() -> list[str]:
    """List all available merge request provider names."""
    return list_providers()


@mcp.tool()
def get_merge_request(
    merge_request_id: str,
    provider_name: str,
) -> dict | None:
    """Fetch a merge request by ID from the given provider."""
    svc = get_service()
    try:
        record = svc.get_merge_request(
            merge_request_id=merge_request_id,
            provider_name=provider_name,
        )
    except ValueError as exc:
        return {"error": str(exc)}

    if record is None:
        return None

    return _mr_record_to_dict(record)


@mcp.tool()
def get_merge_requests_from_user(
    user_id: str,
    provider_name: str,
) -> list[dict]:
    """Fetch merge requests assigned to a user from the provider."""
    svc = get_service()
    try:
        records = svc.get_merge_requests_from_user(
            user_id=user_id,
            provider_name=provider_name,
        )
    except ValueError as exc:
        return [{"error": str(exc)}]

    return [_mr_record_to_dict(r) for r in records]


@mcp.resource("ubq://merge-requests/providers")
def merge_requests_providers_resource() -> str:
    """Available merge request providers."""
    return "\n".join(list_providers())


@mcp.resource("ubq://merge-requests/sessions")
def merge_requests_sessions_resource() -> str:
    """Active merge request provider sessions."""
    sessions = list_active_sessions()
    return "\n".join(sessions) if sessions else "No active sessions"


def _mr_record_to_dict(record) -> dict:
    return {
        "provider_name": record.provider_name,
        "id": record.id,
        "title": record.title,
        "description": record.description,
        "status": record.status,
        "source_branch": record.source_branch,
        "target_branch": record.target_branch,
        "web_url": record.web_url,
        "author": _user_to_dict(record.author),
        "assignees": [_user_to_dict(a) for a in record.assignees],
        "created_at": _fmt_dt(record.created_at),
        "updated_at": _fmt_dt(record.updated_at),
        "merged_at": _fmt_dt(record.merged_at),
        "package": (_package_to_dict(record.package) if record.package else None),
    }


def _user_to_dict(user: UserRecord | None) -> dict | None:
    if user is None:
        return None
    return {
        "username": user.username,
        "display_name": user.display_name,
        "profile_url": user.profile_url,
    }


def _package_to_dict(package) -> dict:
    return {
        "provider_name": package.provider_name,
        "name": package.name,
        "package_url": package.package_url,
    }


def _fmt_dt(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def main():
    run_server(mcp)


if __name__ == "__main__":
    main()
